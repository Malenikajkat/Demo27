"""API для заказов покупателей."""
import uuid
from datetime import date
from flask import request, Blueprint
from app.views.base_view import BaseAPIView
from app.services.sales_order_service import SalesOrderService
from app.models import SalesOrder, SalesOrderItem

sales_orders_bp = Blueprint("sales_orders", __name__)


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
        data = request.get_json()
        required_fields = ["order_number", "order_date", "client_id", "executor_id"]
        if not data or not all(field in data for field in required_fields):
            return self._error_response("Укажите order_number, order_date, client_id, executor_id")

        try:
            client_uuid = uuid.UUID(data["client_id"])
            executor_uuid = uuid.UUID(data["executor_id"])
        except (ValueError, AttributeError):
            return self._error_response("Неверный формат UUID")

        od = data["order_date"]
        order_date = date.fromisoformat(od) if isinstance(od, str) else od

        new_order = SalesOrder(
            order_number=data["order_number"], order_date=order_date,
            client_id=client_uuid, executor_id=executor_uuid
        )
        from app.extensions import db
        db.session.add(new_order)
        db.session.commit()

        if "items" in data:
            for item_data in data["items"]:
                try:
                    product_uuid = uuid.UUID(item_data["product_id"])
                except (ValueError, AttributeError):
                    continue
                item = SalesOrderItem(
                    sales_order=new_order, product_id=product_uuid,
                    quantity=item_data.get("quantity", 1),
                    unit_price=item_data.get("unit_price", 0),
                    discount=item_data.get("discount", 0)
                )
                db.session.add(item)
        db.session.commit()

        return self._success_response({"message": "Заказ создан", "sales_order_id": str(new_order.sales_order_id)}, 201)


class SalesOrderDetailAPI(BaseAPIView):
    """Получение заказа."""

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
                "quantity": float(i.quantity),
                "unit_price": float(i.unit_price),
                "discount": float(i.discount),
            })

        return self._success_response({
            "sales_order_id": str(order.sales_order_id),
            "order_number": order.order_number,
            "order_date": order.order_date.isoformat() if order.order_date else None,
            "client_id": str(order.client_id),
            "executor_id": str(order.executor_id),
            "total_amount": float(order.total_amount) if order.total_amount else 0,
            "items": items,
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

        order = self.service.get_by_id(order_uuid)
        if not order:
            return self._not_found_response("Заказ")

        result = self.service.calculate_cost(sales_order_id)
        return self._success_response(result)


sales_orders_bp.add_url_rule("/", view_func=SalesOrderListAPI.as_view("sales_orders_list"))
sales_orders_bp.add_url_rule("/<sales_order_id>", view_func=SalesOrderDetailAPI.as_view("sales_order_detail"))
sales_orders_bp.add_url_rule(
    "/<sales_order_id>/cost-calculation",
    view_func=SalesOrderCostCalculationAPI.as_view("sales_order_cost")
)
