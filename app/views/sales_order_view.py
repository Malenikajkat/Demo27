
"""API для заказов покупателей."""
import uuid
from datetime import date

from flask import request, Blueprint

from app.views.base_view import BaseAPIView
from app.services.sales_order_service import SalesOrderService
from app.models import SalesOrder, SalesOrderItem, Product, ProductionOrder

sales_orders_bp = Blueprint("sales_orders", __name__)


def validate_discount(item_data, db):
    """Проверяет, что скидка является числом от 0 до 100 процентов."""
    try:
        discount = float(item_data.get("discount", 0))
    except (TypeError, ValueError):
        db.session.rollback()
        return None, "Скидка должна быть числом от 0 до 100"

    if not 0 <= discount <= 100:
        db.session.rollback()
        return None, "Скидка должна быть от 0 до 100 процентов"

    return discount, None


class SalesOrderListAPI(BaseAPIView):
    """Список и создание заказов."""

    def __init__(self):
        self.service = SalesOrderService()

    def get(self):
        """Список заказов."""
        orders = self.service.get_all_dto()
        return self._success_response({
            "sales_orders": [o.to_dict() for o in orders]
        })

    def post(self):
        """Создание заказа."""
        from app.extensions import db
        from sqlalchemy import text

        data = request.get_json()
        required_fields = ["order_date", "client_id", "executor_id"]

        if not data or not all(field in data for field in required_fields):
            return self._error_response(
                "Укажите order_date, client_id, executor_id"
            )

        try:
            client_uuid = uuid.UUID(data["client_id"])
            executor_uuid = uuid.UUID(data["executor_id"])
        except (ValueError, AttributeError):
            return self._error_response("Неверный формат UUID")

        od = data["order_date"]
        order_date = date.fromisoformat(od) if isinstance(od, str) else od

        # Автоматическая генерация номера заказа
        order_number = data.get("order_number")

        if not order_number:
            result = db.session.execute(text(
                "SELECT order_number FROM sales_orders "
                "WHERE order_number IS NOT NULL AND order_number != ''"
            )).scalars().all()

            max_num = 0

            for on in result:
                try:
                    num_part = on.split("-")[-1]
                    num = int(num_part)

                    if num > max_num:
                        max_num = num

                except (ValueError, IndexError):
                    continue

            order_number = f"ЗК-{max_num + 1:06d}"

        new_order = SalesOrder(
            order_number=order_number,
            order_date=order_date,
            client_id=client_uuid,
            executor_id=executor_uuid
        )

        db.session.add(new_order)
        db.session.flush()

        # Создаём позиции заказа
        total_amount = 0.0
        items_list = []

        if "items" in data:
            for item_data in data["items"]:
                product_id_str = item_data.get("product_id")

                if not product_id_str:
                    continue

                try:
                    product_uuid = uuid.UUID(product_id_str)
                except (ValueError, AttributeError):
                    continue

                quantity = float(item_data.get("quantity", 1))
                unit_price = float(item_data.get("unit_price", 0))

                discount, error = validate_discount(item_data, db)

                if error:
                    return self._error_response(error)

                item = SalesOrderItem(
                    sales_order=new_order,
                    product_id=product_uuid,
                    quantity=quantity,
                    unit_price=unit_price,
                    discount=discount
                )

                db.session.add(item)

                items_list.append({
                    "product_uuid": product_uuid,
                    "quantity": quantity,
                    "unit_price": unit_price,
                    "discount": discount
                })

        # Пересчёт суммы заказа
        for item_data in items_list:
            quantity = item_data["quantity"]
            unit_price = item_data["unit_price"]
            discount = item_data["discount"]

            item_total = quantity * unit_price * (1 - discount / 100)
            total_amount += item_total

        new_order.total_amount = total_amount
        db.session.commit()

        # Автоматическое создание заказа на производство
        production_order_id = None

        if data.get("auto_create_production", True):
            from app.models import (
                ProductionOrder,
                ProductionOrderItem,
                SpecificationMaterial,
                SpecificationOperation
            )
            from app.models import MaterialPrice, OperationPrice
            from sqlalchemy import select

            existing_prod_order = db.session.query(
                ProductionOrder
            ).filter_by(
                sales_order_id=new_order.sales_order_id
            ).first()

            if existing_prod_order:
                prod_order = existing_prod_order

                for old_item in prod_order.items:
                    db.session.delete(old_item)

            else:
                prod_result = db.session.execute(text(
                    "SELECT order_number FROM production_orders "
                    "WHERE order_number IS NOT NULL AND order_number != ''"
                )).scalars().all()

                prod_max_num = 0

                for on in prod_result:
                    try:
                        num_part = on.split("-")[-1]
                        num = int(num_part)

                        if num > prod_max_num:
                            prod_max_num = num

                    except (ValueError, IndexError):
                        continue

                prod_order_number = f"ЗП-{prod_max_num + 1:06d}"

                prod_order = ProductionOrder(
                    order_number=prod_order_number,
                    order_date=order_date,
                    subdivision="Основное подразделение",
                    client_id=client_uuid,
                    sales_order_id=new_order.sales_order_id,
                    status="Новый"
                )

                db.session.add(prod_order)
                db.session.flush()

            total_production_cost = 0.0

            for item_data in items_list:
                product_uuid = item_data["product_uuid"]
                quantity = item_data["quantity"]

                product = db.session.get(Product, product_uuid)

                if not product:
                    continue

                prod_item = ProductionOrderItem(
                    production_order=prod_order,
                    product_id=product_uuid,
                    quantity=quantity,
                    completed_quantity=0,
                    unit_price=0,
                    total_price=0
                )

                db.session.add(prod_item)

                product_cost = 0.0

                # Материальные затраты
                spec_mats = product.spec_materials

                for spec_mat in spec_mats:
                    mat_qty_per_unit = float(spec_mat.quantity_per_unit)
                    mat_qty = mat_qty_per_unit * quantity

                    price_stmt = select(MaterialPrice).where(
                        MaterialPrice.material_id == spec_mat.material_id
                    ).order_by(
                        MaterialPrice.effective_date.desc()
                    ).limit(1)

                    price_record = db.session.execute(
                        price_stmt
                    ).scalar_one_or_none()

                    mat_price = (
                        float(price_record.price) if price_record else 0.0
                    )

                    mat_total = mat_qty * mat_price
                    product_cost += mat_total

                # Затраты на операции
                spec_ops = product.spec_operations

                for spec_op in spec_ops:
                    time_norm = float(spec_op.time_norm)
                    op_qty = float(spec_op.op_quantity)
                    total_time = time_norm * op_qty * quantity

                    price_stmt = select(OperationPrice).where(
                        OperationPrice.operation_id == spec_op.operation_id
                    ).order_by(
                        OperationPrice.effective_date.desc()
                    ).limit(1)

                    price_record = db.session.execute(
                        price_stmt
                    ).scalar_one_or_none()

                    op_price = (
                        float(price_record.price) if price_record else 0.0
                    )

                    op_total = total_time * op_price
                    product_cost += op_total

                prod_item.total_price = product_cost
                total_production_cost += product_cost

            prod_order.total_amount = total_production_cost

            db.session.commit()

            production_order_id = str(prod_order.order_id)

            print(
                f"Created/updated production order "
                f"{production_order_id} with cost {total_production_cost}"
            )

        return self._success_response({
            "message": "Заказ создан",
            "sales_order_id": str(new_order.sales_order_id),
            "total_amount": total_amount,
            "production_order_id": production_order_id
        }, 201)


class SalesOrderDetailAPI(BaseAPIView):
    """Получение, обновление и удаление заказа."""

    def __init__(self):
        self.service = SalesOrderService()

    def get(self, sales_order_id):
        """Получение заказа."""
        try:
            order_uuid = uuid.UUID(sales_order_id)
        except (ValueError, AttributeError):
            return self._error_response("Неверный формат UUID")

        order = self.service.get_by_id(order_uuid)

        if not order:
            return self._not_found_response("Заказ")

        items = []

        for i in order.items:
            items.append({
                "sales_order_item_id": str(i.sales_order_item_id),
                "product_id": str(i.product_id),
                "product_name": i.product.name if i.product else "",
                "quantity": float(i.quantity),
                "unit_price": float(i.unit_price),
                "discount": float(i.discount),
            })

        return self._success_response({
            "sales_order": {
                "sales_order_id": str(order.sales_order_id),
                "order_number": order.order_number,
                "order_date": (
                    order.order_date.isoformat() if order.order_date else None
                ),
                "client_id": str(order.client_id),
                "executor_id": str(order.executor_id),
                "total_amount": (
                    float(order.total_amount) if order.total_amount else 0
                ),
                "items": items,
            }
        })

    def put(self, sales_order_id):
        """Обновление заказа."""
        from app.extensions import db

        try:
            order_uuid = uuid.UUID(sales_order_id)
        except (ValueError, AttributeError):
            return self._error_response("Неверный формат UUID")

        order = self.service.get_by_id(order_uuid)

        if not order:
            return self._not_found_response("Заказ")

        data = request.get_json()

        if not data:
            return self._error_response("Нет данных")

        # Обновляем основные поля
        if "order_date" in data:
            od = data["order_date"]
            order.order_date = (
                date.fromisoformat(od) if isinstance(od, str) else od
            )

        if "client_id" in data:
            try:
                order.client_id = uuid.UUID(data["client_id"])
            except (ValueError, AttributeError):
                return self._error_response("Неверный формат UUID клиента")

        if "executor_id" in data:
            try:
                order.executor_id = uuid.UUID(data["executor_id"])
            except (ValueError, AttributeError):
                return self._error_response(
                    "Неверный формат UUID исполнителя"
                )

        # Обновляем позиции
        if "items" in data:
            for item in order.items:
                db.session.delete(item)

            db.session.flush()

            total_amount = 0.0
            items_list = []

            for item_data in data["items"]:
                product_id_str = item_data.get("product_id")

                if not product_id_str:
                    continue

                try:
                    product_uuid = uuid.UUID(product_id_str)
                except (ValueError, AttributeError):
                    continue

                quantity = float(item_data.get("quantity", 1))
                unit_price = float(item_data.get("unit_price", 0))

                discount, error = validate_discount(item_data, db)

                if error:
                    return self._error_response(error)

                item = SalesOrderItem(
                    sales_order=order,
                    product_id=product_uuid,
                    quantity=quantity,
                    unit_price=unit_price,
                    discount=discount
                )

                db.session.add(item)

                items_list.append({
                    "product_uuid": product_uuid,
                    "quantity": quantity,
                    "unit_price": unit_price,
                    "discount": discount
                })

            # Пересчёт суммы
            for item_data in items_list:
                quantity = item_data["quantity"]
                unit_price = item_data["unit_price"]
                discount = item_data["discount"]

                item_total = quantity * unit_price * (1 - discount / 100)
                total_amount += item_total

            order.total_amount = total_amount

        # Обновляем связанный заказ на производство
        if data.get("auto_create_production", True):
            from app.models import (
                ProductionOrderItem,
                SpecificationMaterial,
                SpecificationOperation
            )
            from app.models import MaterialPrice, OperationPrice
            from sqlalchemy import select

            prod_order = db.session.query(ProductionOrder).filter_by(
                sales_order_id=order.sales_order_id
            ).first()

            if prod_order:
                for old_item in prod_order.items:
                    db.session.delete(old_item)

                total_production_cost = 0.0

                for item_data in items_list:
                    product_uuid = item_data.get("product_uuid")
                    quantity = item_data.get("quantity", 1)

                    print(
                        f"DEBUG: Calculating production cost "
                        f"for product_uuid={product_uuid}, quantity={quantity}, "
                        f"type={type(quantity)}"
                    )

                    product = db.session.get(Product, product_uuid)

                    if not product:
                        print(
                            f"DEBUG: Product not found for uuid={product_uuid}"
                        )
                        continue

                    prod_item = ProductionOrderItem(
                        production_order=prod_order,
                        product_id=product.product_id,
                        quantity=quantity,
                        completed_quantity=0,
                        unit_price=0,
                        total_price=0
                    )

                    db.session.add(prod_item)

                    product_cost = 0.0

                    # Материалы
                    for spec_mat in product.spec_materials:
                        mat_qty_per_unit = float(
                            spec_mat.quantity_per_unit
                        )
                        mat_qty = mat_qty_per_unit * quantity

                        price_stmt = select(MaterialPrice).where(
                            MaterialPrice.material_id == spec_mat.material_id
                        ).order_by(
                            MaterialPrice.effective_date.desc()
                        ).limit(1)

                        price_record = db.session.execute(
                            price_stmt
                        ).scalar_one_or_none()

                        mat_price = (
                            float(price_record.price) if price_record else 0.0
                        )

                        mat_total = mat_qty * mat_price
                        product_cost += mat_total

                        print(
                            f"DEBUG: Material {spec_mat.material.name}: "
                            f"qty_per_unit={mat_qty_per_unit}, qty={mat_qty}, "
                            f"price={mat_price}, total={mat_total}"
                        )

                    # Операции
                    for spec_op in product.spec_operations:
                        time_norm = float(spec_op.time_norm)
                        op_qty = float(spec_op.op_quantity)
                        total_time = time_norm * op_qty * quantity

                        price_stmt = select(OperationPrice).where(
                            OperationPrice.operation_id == spec_op.operation_id
                        ).order_by(
                            OperationPrice.effective_date.desc()
                        ).limit(1)

                        price_record = db.session.execute(
                            price_stmt
                        ).scalar_one_or_none()

                        op_price = (
                            float(price_record.price) if price_record else 0.0
                        )

                        op_total = total_time * op_price
                        product_cost += op_total

                        print(
                            f"DEBUG: Operation {spec_op.operation.name}: "
                            f"time_norm={time_norm}, op_qty={op_qty}, "
                            f"quantity={quantity}, total_time={total_time}, "
                            f"price={op_price}, total={op_total}"
                        )

                    prod_item.total_price = product_cost
                    total_production_cost += product_cost

                    print(
                        f"DEBUG: Product {product.name}: "
                        f"total_cost={product_cost}"
                    )

                prod_order.total_amount = total_production_cost

                print(
                    f"Updated production order {prod_order.order_id} "
                    f"with cost {total_production_cost}"
                )

        db.session.commit()

        return self._success_response({
            "message": "Заказ обновлён",
            "sales_order_id": str(order.sales_order_id),
            "total_amount": float(order.total_amount)
        })

    def delete(self, sales_order_id):
        """Удаление заказа."""
        from app.extensions import db
        from app.models import ProductionOrder

        try:
            order_uuid = uuid.UUID(sales_order_id)
        except (ValueError, AttributeError):
            return self._error_response("Неверный формат UUID")

        order = self.service.get_by_id(order_uuid)

        if not order:
            return self._not_found_response("Заказ")

        # Находим связанные заказы на производство
        prod_orders = db.session.query(ProductionOrder).filter_by(
            sales_order_id=order_uuid
        ).all()

        # Удаляем связанные позиции в заказах на производство
        for prod_order in prod_orders:
            for prod_item in prod_order.items:
                db.session.delete(prod_item)

        # Удаляем связанные заказы на производство
        for prod_order in prod_orders:
            db.session.delete(prod_order)

        # Удаляем связанные позиции заказа покупателя
        for item in order.items:
            db.session.delete(item)

        # Удаляем заказ покупателя
        db.session.delete(order)
        db.session.commit()

        return self._success_response({
            "message": f"Заказ {order.order_number} удалён"
        })


class SalesOrderCostCalculationAPI(BaseAPIView):
    """Расчёт стоимости заказа."""

    def __init__(self):
        self.service = SalesOrderService()

    def get(self, sales_order_id):
        """Расчёт стоимости."""
        try:
            order_uuid = uuid.UUID(sales_order_id)
        except (ValueError, AttributeError):
            return self._error_response("Неверный формат UUID")

        result = self.service.calculate_cost(order_uuid)

        if "error" in result:
            return self._not_found_response("Заказ")

        return self._success_response(result)


class SalesOrderProductionAPI(BaseAPIView):
    """Получение связанного заказа на производство."""

    def __init__(self):
        self.service = SalesOrderService()

    def get(self, sales_order_id):
        """Получение заказа на производство, связанного с заказом покупателя."""
        from app.extensions import db
        from app.services.production_order_service import ProductionOrderService

        try:
            order_uuid = uuid.UUID(sales_order_id)
        except (ValueError, AttributeError):
            return self._error_response("Неверный формат UUID")

        order = self.service.get_by_id(order_uuid)

        if not order:
            return self._not_found_response("Заказ")

        # Ищем связанный заказ на производство
        prod_order = db.session.query(ProductionOrder).filter_by(
            sales_order_id=order_uuid
        ).first()

        if not prod_order:
            return self._success_response({
                "message": (
                    "Для этого заказа ещё не создан заказ на производство"
                ),
                "production_order": None
            })

        # Получаем детали заказа на производство через сервис
        prod_service = ProductionOrderService()
        prod_details = prod_service.get_order_with_details(prod_order.order_id)

        if "error" in prod_details:
            return self._not_found_response("Заказ на производство")

        return self._success_response({
            "production_order": prod_details
        })


sales_orders_bp.add_url_rule(
    "/", view_func=SalesOrderListAPI.as_view("sales_orders_list")
)

sales_orders_bp.add_url_rule(
    "/<sales_order_id>",
    view_func=SalesOrderDetailAPI.as_view("sales_order_detail")
)

sales_orders_bp.add_url_rule(
    "/<sales_order_id>/cost-calculation",
    view_func=SalesOrderCostCalculationAPI.as_view("sales_order_cost")
)

sales_orders_bp.add_url_rule(
    "/<sales_order_id>/production-order",
    view_func=SalesOrderProductionAPI.as_view("sales_order_production")
)
