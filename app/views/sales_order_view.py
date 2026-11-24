"""API для заказов покупателей."""
import math
import uuid
from datetime import date
from flask import request, Blueprint
from app.views.base_view import BaseAPIView
from app.services.sales_order_service import SalesOrderService
from app.models import SalesOrder, SalesOrderItem, Product, ProductionOrder

sales_orders_bp = Blueprint("sales_orders", __name__)


_ORDER_DATE_ERROR = (
    "\u0414\u0430\u0442\u0430 \u0437\u0430\u043a\u0430\u0437\u0430 \u0434\u043e\u043b\u0436\u043d\u0430 \u0431\u044b\u0442\u044c \u0432 \u0444\u043e\u0440\u043c\u0430\u0442\u0435 YYYY-MM-DD"
)


def _parse_order_date(value):
    """Validates an ISO-8601 order date from the JSON API."""
    if not isinstance(value, str):
        raise ValueError(_ORDER_DATE_ERROR)
    try:
        return date.fromisoformat(value)
    except ValueError:
        raise ValueError(_ORDER_DATE_ERROR) from None


def _parse_order_item(item_data):
    """Проверяет позицию заказа и возвращает нормализованные значения."""
    if not isinstance(item_data, dict):
        raise ValueError("Каждая позиция заказа должна быть JSON-объектом")

    product_id = item_data.get("product_id")
    if not isinstance(product_id, str):
        raise ValueError("Для позиции требуется product_id в формате UUID")

    try:
        product_uuid = uuid.UUID(product_id)
        quantity = float(item_data.get("quantity", 1))
        unit_price = float(item_data.get("unit_price", 0))
        discount = float(item_data.get("discount", 0))
    except (TypeError, ValueError, AttributeError):
        raise ValueError("Поля позиции должны содержать корректные UUID и числа") from None

    if not all(math.isfinite(value) for value in (quantity, unit_price, discount)):
        raise ValueError("Числовые значения позиции должны быть конечными")
    if quantity <= 0:
        raise ValueError("Количество продукции должно быть больше нуля")
    if unit_price < 0:
        raise ValueError("Цена продукции не может быть отрицательной")
    if not 0 <= discount <= 100:
        raise ValueError("Скидка должна находиться в диапазоне от 0 до 100 процентов")

    return product_uuid, quantity, unit_price, discount


class SalesOrderListAPI(BaseAPIView):
    """Список и создание заказов."""

    def __init__(self):
        self.service = SalesOrderService()

    def get(self):
        """Список заказов."""
        orders = self.service.get_all_dto()
        return self._success_response({"sales_orders": [o.to_dict() for o in orders]})

    def post(self):
        """Создание заказа."""
        from app.extensions import db
        from sqlalchemy import text
        
        data = request.get_json(silent=True)
        required_fields = ["order_date", "client_id", "executor_id"]
        if not isinstance(data, dict) or not all(field in data for field in required_fields):
            return self._error_response("Укажите order_date, client_id, executor_id")

        try:
            client_uuid = uuid.UUID(data["client_id"])
            executor_uuid = uuid.UUID(data["executor_id"])
        except (ValueError, AttributeError):
            return self._error_response("Неверный формат UUID")

        try:
            order_date = _parse_order_date(data["order_date"])
        except ValueError as error:
            return self._error_response(str(error))

        # Автоматическая генерация номера заказа
        order_number = data.get("order_number")
        if not order_number:
            # Получаем все номера заказов и извлекаем максимальный номер
            result = db.session.execute(text(
                "SELECT order_number FROM sales_orders WHERE order_number IS NOT NULL AND order_number != ''"
            )).scalars().all()
            
            max_num = 0
            for on in result:
                try:
                    # Извлекаем число из формата "ЗК-000001"
                    num_part = on.split('-')[-1]
                    num = int(num_part)
                    if num > max_num:
                        max_num = num
                except (ValueError, IndexError):
                    continue
            
            order_number = f"ЗК-{max_num + 1:06d}"

        new_order = SalesOrder(
            order_number=order_number, order_date=order_date,
            client_id=client_uuid, executor_id=executor_uuid
        )
        db.session.add(new_order)
        db.session.flush()  # Получаем ID заказа без коммита

        # Создаём позиции и сразу считаем сумму.
        total_amount = 0.0
        items_list = []

        if "items" in data and not isinstance(data["items"], list):
            db.session.rollback()
            return self._error_response("Поле items должно быть массивом")

        if "items" in data:
            for item_data in data["items"]:
                try:
                    product_uuid, quantity, unit_price, discount = _parse_order_item(item_data)
                except ValueError as error:
                    db.session.rollback()
                    return self._error_response(str(error))

                item = SalesOrderItem(
                    sales_order=new_order, product_id=product_uuid,
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
        
        # Пересчёт суммы заказа из переданных данных
        for item_data in items_list:
            quantity = item_data["quantity"]
            unit_price = item_data["unit_price"]
            discount = item_data["discount"]
            item_total = quantity * unit_price * (1 - discount / 100)
            total_amount += item_total
        
        new_order.total_amount = total_amount
        db.session.commit()

        # Автоматическое создание или обновление заказа на производство
        production_order_id = None
        if data.get("auto_create_production", True):
            from app.models import ProductionOrder, ProductionOrderItem, SpecificationMaterial, SpecificationOperation
            from app.models import MaterialPrice, OperationPrice
            from sqlalchemy import select
            
            # Проверяем, существует ли уже связанный заказ на производство
            existing_prod_order = db.session.query(ProductionOrder).filter_by(
                sales_order_id=new_order.sales_order_id
            ).first()
            
            if existing_prod_order:
                # Обновляем существующий заказ на производство
                prod_order = existing_prod_order
                # Удаляем старые позиции
                for old_item in prod_order.items:
                    db.session.delete(old_item)
            else:
                # Генерация номера заказа на производство
                prod_result = db.session.execute(text(
                    "SELECT order_number FROM production_orders WHERE order_number IS NOT NULL AND order_number != ''"
                )).scalars().all()
                
                prod_max_num = 0
                for on in prod_result:
                    try:
                        num_part = on.split('-')[-1]
                        num = int(num_part)
                        if num > prod_max_num:
                            prod_max_num = num
                    except (ValueError, IndexError):
                        continue
                
                prod_order_number = f"ЗП-{prod_max_num + 1:06d}"
                
                # Создание заказа на производство
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
            
            # Расчёт себестоимости и добавление позиций с материалами и операциями
            total_production_cost = 0.0
            
            for item_data in items_list:
                product_uuid = item_data["product_uuid"]
                quantity = item_data["quantity"]
                
                # Получаем продукт
                product = db.session.get(Product, product_uuid)
                if not product:
                    continue
                
                # Создаём позицию в заказе на производство
                prod_item = ProductionOrderItem(
                    production_order=prod_order,
                    product_id=product_uuid,
                    quantity=quantity,
                    completed_quantity=0,
                    unit_price=0,
                    total_price=0
                )
                db.session.add(prod_item)
                
                # Рассчитываем себестоимость на основе спецификаций
                product_cost = 0.0
                
                # 1. Материальные затраты
                spec_mats = product.spec_materials
                for spec_mat in spec_mats:
                    mat_qty_per_unit = float(spec_mat.quantity_per_unit)
                    mat_qty = mat_qty_per_unit * quantity
                    
                    # Получаем актуальную цену материала
                    price_stmt = select(MaterialPrice).where(
                        MaterialPrice.material_id == spec_mat.material_id
                    ).order_by(MaterialPrice.effective_date.desc()).limit(1)
                    price_record = db.session.execute(price_stmt).scalar_one_or_none()
                    mat_price = float(price_record.price) if price_record else 0.0
                    mat_total = mat_qty * mat_price
                    product_cost += mat_total
                
                # 2. Затраты на операции
                spec_ops = product.spec_operations
                for spec_op in spec_ops:
                    time_norm = float(spec_op.time_norm)
                    op_qty = float(spec_op.op_quantity)
                    total_time = time_norm * op_qty * quantity
                    
                    # Получаем актуальную цену операции
                    price_stmt = select(OperationPrice).where(
                        OperationPrice.operation_id == spec_op.operation_id
                    ).order_by(OperationPrice.effective_date.desc()).limit(1)
                    price_record = db.session.execute(price_stmt).scalar_one_or_none()
                    op_price = float(price_record.price) if price_record else 0.0
                    op_total = total_time * op_price
                    product_cost += op_total
                
                # Обновляем total_price позиции
                prod_item.total_price = product_cost
                total_production_cost += product_cost
            
            # Обновляем общую сумму заказа на производство
            prod_order.total_amount = total_production_cost
            
            db.session.commit()
            production_order_id = str(prod_order.order_id)
            print(f"Created/updated production order {production_order_id} with cost {total_production_cost}")

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
                "order_date": order.order_date.isoformat() if order.order_date else None,
                "client_id": str(order.client_id),
                "executor_id": str(order.executor_id),
                "total_amount": float(order.total_amount) if order.total_amount else 0,
                "items": items,
            }
        })

    def put(self, sales_order_id):
        """Обновление заказа."""
        from app.extensions import db
        from sqlalchemy import text
        
        try:
            order_uuid = uuid.UUID(sales_order_id)
        except (ValueError, AttributeError):
            return self._error_response("Неверный формат UUID")

        order = self.service.get_by_id(order_uuid)
        if not order:
            return self._not_found_response("Заказ")

        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return self._error_response("Ожидается JSON-объект")
        if "items" in data and not isinstance(data["items"], list):
            return self._error_response("Поле items должно быть массивом")

        # Обновляем основные поля
        if "order_date" in data:
            od = data["order_date"]
            order.order_date = date.fromisoformat(od) if isinstance(od, str) else od
        
        if "client_id" in data:
            try:
                order.client_id = uuid.UUID(data["client_id"])
            except (ValueError, AttributeError):
                return self._error_response("Неверный формат UUID клиента")
        
        if "executor_id" in data:
            try:
                order.executor_id = uuid.UUID(data["executor_id"])
            except (ValueError, AttributeError):
                return self._error_response("Неверный формат UUID исполнителя")

        # Обновляем позиции
        if "items" in data:
            # Удаляем старые позиции
            for item in order.items:
                db.session.delete(item)
            db.session.flush()

            # Создаём новые позиции
            total_amount = 0.0
            items_list = []
            
            for item_data in data["items"]:
                try:
                    product_uuid, quantity, unit_price, discount = _parse_order_item(item_data)
                except ValueError as error:
                    db.session.rollback()
                    return self._error_response(str(error))

                item = SalesOrderItem(
                    sales_order=order, product_id=product_uuid,
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
            from app.models import ProductionOrderItem, SpecificationMaterial, SpecificationOperation
            from app.models import MaterialPrice, OperationPrice
            from sqlalchemy import select
            
            prod_order = db.session.query(ProductionOrder).filter_by(
                sales_order_id=order.sales_order_id
            ).first()
            
            if prod_order:
                # Удаляем старые позиции
                for old_item in prod_order.items:
                    db.session.delete(old_item)
                
                # Пересчитываем себестоимость
                total_production_cost = 0.0
                
                for item_data in items_list:
                    product_uuid = item_data.get("product_uuid")
                    quantity = item_data.get("quantity", 1)
                    
                    print(f"DEBUG: Calculating production cost for product_uuid={product_uuid}, quantity={quantity}, type={type(quantity)}")
                    
                    # Получаем продукт напрямую
                    product = db.session.get(Product, product_uuid)
                    if not product:
                        print(f"DEBUG: Product not found for uuid={product_uuid}")
                        continue
                    
                    # Создаём позицию в заказе на производство
                    prod_item = ProductionOrderItem(
                        production_order=prod_order,
                        product_id=product.product_id,
                        quantity=quantity,
                        completed_quantity=0,
                        unit_price=0,
                        total_price=0
                    )
                    db.session.add(prod_item)
                    
                    # Рассчитываем себестоимость
                    product_cost = 0.0
                    
                    # Материалы
                    for spec_mat in product.spec_materials:
                        mat_qty_per_unit = float(spec_mat.quantity_per_unit)
                        mat_qty = mat_qty_per_unit * quantity
                        
                        price_stmt = select(MaterialPrice).where(
                            MaterialPrice.material_id == spec_mat.material_id
                        ).order_by(MaterialPrice.effective_date.desc()).limit(1)
                        price_record = db.session.execute(price_stmt).scalar_one_or_none()
                        mat_price = float(price_record.price) if price_record else 0.0
                        mat_total = mat_qty * mat_price
                        product_cost += mat_total
                        print(f"DEBUG: Material {spec_mat.material.name}: qty_per_unit={mat_qty_per_unit}, qty={mat_qty}, price={mat_price}, total={mat_total}")
                    
                    # Операции
                    for spec_op in product.spec_operations:
                        time_norm = float(spec_op.time_norm)
                        op_qty = float(spec_op.op_quantity)
                        total_time = time_norm * op_qty * quantity
                        
                        price_stmt = select(OperationPrice).where(
                            OperationPrice.operation_id == spec_op.operation_id
                        ).order_by(OperationPrice.effective_date.desc()).limit(1)
                        price_record = db.session.execute(price_stmt).scalar_one_or_none()
                        op_price = float(price_record.price) if price_record else 0.0
                        op_total = total_time * op_price
                        product_cost += op_total
                        print(f"DEBUG: Operation {spec_op.operation.name}: time_norm={time_norm}, op_qty={op_qty}, quantity={quantity}, total_time={total_time}, price={op_price}, total={op_total}")
                    
                    prod_item.total_price = product_cost
                    total_production_cost += product_cost
                    print(f"DEBUG: Product {product.name}: total_cost={product_cost}")
                
                prod_order.total_amount = total_production_cost
                print(f"Updated production order {prod_order.order_id} with cost {total_production_cost}")
        
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
                "message": "Для этого заказа ещё не создан заказ на производство",
                "production_order": None
            })

        # Получаем детали заказа на производство через сервис
        prod_service = ProductionOrderService()
        prod_details = prod_service.get_order_with_details(prod_order.order_id)
        
        if "error" in prod_details:
            return self._not_found_response("Заказ на производство")

        # Возвращаем детали заказа на производство
        return self._success_response({
            "production_order": prod_details
        })


sales_orders_bp.add_url_rule("/", view_func=SalesOrderListAPI.as_view("sales_orders_list"))
sales_orders_bp.add_url_rule("/<sales_order_id>", view_func=SalesOrderDetailAPI.as_view("sales_order_detail"))
sales_orders_bp.add_url_rule(
    "/<sales_order_id>/cost-calculation",
    view_func=SalesOrderCostCalculationAPI.as_view("sales_order_cost")
)
sales_orders_bp.add_url_rule(
    "/<sales_order_id>/production-order",
    view_func=SalesOrderProductionAPI.as_view("sales_order_production")
)
