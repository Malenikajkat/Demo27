"""API для заказов на производство."""
import uuid
from datetime import date
from flask import request, Blueprint
from app.views.base_view import BaseAPIView
from app.services.production_order_service import ProductionOrderService
from app.models import ProductionOrder, ProductionOrderItem

production_orders_bp = Blueprint("production_orders", __name__)


class ProductionOrderListAPI(BaseAPIView):
    """Список и создание заказов на производство."""

    def __init__(self):
        self.service = ProductionOrderService()

    def get(self):
        """Список заказов на производство."""
        orders = self.service.get_all_dto()
        return self._success_response({
            "production_orders": [o.to_dict() for o in orders]
        })

    def post(self):
        """Создание заказа на производство."""
        from app.extensions import db
        from sqlalchemy import text

        data = request.get_json()
        required_fields = ["order_date"]
        if not data or not all(field in data for field in required_fields):
            return self._error_response("Укажите order_date")

        od = data["order_date"]
        order_date = date.fromisoformat(od) if isinstance(od, str) else od

        client_uuid = None
        if data.get("client_id"):
            try:
                client_uuid = uuid.UUID(data["client_id"])
            except (ValueError, AttributeError):
                return self._error_response("Неверный формат UUID client_id")

        # Автоматическая генерация номера заказа
        order_number = data.get("order_number")
        if not order_number:
            # Получаем все номера заказов и извлекаем максимальный номер
            result = db.session.execute(text(
                "SELECT order_number FROM production_orders WHERE order_number IS NOT NULL AND order_number != ''"
            )).scalars().all()

            max_num = 0
            for on in result:
                try:
                    # Извлекаем число из формата "ЗП-000001"
                    num_part = on.split('-')[-1]
                    num = int(num_part)
                    if num > max_num:
                        max_num = num
                except (ValueError, IndexError):
                    continue

            order_number = f"ЗП-{max_num + 1:06d}"

        new_order = ProductionOrder(
            order_number=order_number,
            order_date=order_date,
            subdivision=data.get("subdivision"),
            client_id=client_uuid,
            status=data.get("status", "Новый"),
        )
        from app.extensions import db
        db.session.add(new_order)
        db.session.flush()

        if "items" in data:
            for item_data in data["items"]:
                try:
                    product_uuid = uuid.UUID(item_data["product_id"])
                except (ValueError, AttributeError):
                    continue

                item = ProductionOrderItem(
                    production_order=new_order,
                    product_id=product_uuid,
                    quantity=item_data.get("quantity", 1),
                    completed_quantity=item_data.get("completed_quantity", 0),
                    unit_price=item_data.get("unit_price", 0),
                    total_price=item_data.get("total_price", 0),
                )
                db.session.add(item)

        db.session.commit()

        return self._success_response(
            {"message": "Заказ на производство создан", "order_id": str(new_order.order_id)},
            201
        )


class ProductionOrderDetailAPI(BaseAPIView):
    """Получение заказа на производство."""

    def __init__(self):
        self.service = ProductionOrderService()

    def get(self, order_id):
        """Получение заказа на производство."""
        try:
            order_uuid = uuid.UUID(order_id)
        except (ValueError, AttributeError):
            return self._error_response("Неверный формат UUID")

        order_data = self.service.get_order_with_details(order_uuid)
        if "error" in order_data:
            return self._not_found_response("Заказ на производство")

        return self._success_response(order_data)

    def put(self, order_id):
        """Обновление заказа на производство."""
        try:
            order_uuid = uuid.UUID(order_id)
        except (ValueError, AttributeError):
            return self._error_response("Неверный формат UUID")

        from app.extensions import db
        order = db.session.get(ProductionOrder, order_uuid)
        if not order:
            return self._not_found_response("Заказ на производство")

        data = request.get_json()
        if not data:
            return self._error_response("Нет данных")

        if "order_number" in data:
            order.order_number = data["order_number"]
        if "order_date" in data:
            od = data["order_date"]
            order.order_date = date.fromisoformat(od) if isinstance(od, str) else od
        if "subdivision" in data:
            order.subdivision = data["subdivision"]
        if "status" in data:
            order.status = data["status"]

        db.session.commit()

        return self._success_response({"message": "Заказ на производство обновлён"})

    def delete(self, order_id):
        """Удаление заказа на производство."""
        try:
            order_uuid = uuid.UUID(order_id)
        except (ValueError, AttributeError):
            return self._error_response("Неверный формат UUID")

        from app.extensions import db
        order = db.session.get(ProductionOrder, order_uuid)
        if not order:
            return self._not_found_response("Заказ на производство")

        db.session.delete(order)
        db.session.commit()

        return self._success_response({"message": "Заказ на производство удалён"})


production_orders_bp.add_url_rule("/", view_func=ProductionOrderListAPI.as_view("production_orders_list"))
production_orders_bp.add_url_rule("/<order_id>", view_func=ProductionOrderDetailAPI.as_view("production_order_detail"))
