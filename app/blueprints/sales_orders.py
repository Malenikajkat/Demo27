"""Blueprint для заказов покупателей."""
import uuid
from datetime import date
from flask import Blueprint, request, jsonify
from app.models import SalesOrder, SalesOrderItem
from app.extensions import db

sales_orders_bp = Blueprint("sales_orders", __name__)


@sales_orders_bp.route("/", methods=["GET"])
def list_sales_orders():
    """Список заказов."""
    orders = db.session.execute(db.select(SalesOrder)).scalars().all()
    return jsonify({
        "sales_orders": [
            {
                "sales_order_id": str(o.sales_order_id),
                "order_number": o.order_number,
                "order_date": o.order_date.isoformat() if o.order_date else None,
                "client_id": str(o.client_id),
                "executor_id": str(o.executor_id),
                "total_amount": float(o.total_amount) if o.total_amount else 0,
                "created_at": o.created_at.isoformat() if o.created_at else None,
            }
            for o in orders
        ]
    }), 200


@sales_orders_bp.route("/", methods=["POST"])
def create_sales_order():
    """Создание заказа."""
    data = request.get_json()
    required_fields = ["order_number", "order_date", "client_id", "executor_id"]
    if not data or not all(field in data for field in required_fields):
        return jsonify({
            "error": "Bad Request",
            "message": "Укажите order_number, order_date, client_id, executor_id",
        }), 400

    try:
        client_uuid = uuid.UUID(data["client_id"])
        executor_uuid = uuid.UUID(data["executor_id"])
    except (ValueError, AttributeError):
        return jsonify({"error": "Bad Request", "message": "Неверный формат UUID"}), 400

    order_date = date.fromisoformat(data["order_date"]) if isinstance(data["order_date"], str) else data["order_date"]

    new_order = SalesOrder(
        order_number=data["order_number"],
        order_date=order_date,
        client_id=client_uuid,
        executor_id=executor_uuid,
    )
    db.session.add(new_order)
    db.session.commit()

    if "items" in data:
        for item_data in data["items"]:
            try:
                product_uuid = uuid.UUID(item_data["product_id"])
            except (ValueError, AttributeError):
                continue

            item = SalesOrderItem(
                sales_order=new_order,
                product_id=product_uuid,
                quantity=item_data.get("quantity", 1),
                unit_price=item_data.get("unit_price", 0),
                discount=item_data.get("discount", 0),
            )
            db.session.add(item)

    db.session.commit()

    return jsonify({
        "message": "Заказ создан",
        "sales_order_id": str(new_order.sales_order_id),
    }), 201


@sales_orders_bp.route("/<sales_order_id>", methods=["GET"])
def get_sales_order(sales_order_id):
    """Получение заказа по ID."""
    try:
        order_uuid = uuid.UUID(sales_order_id)
    except (ValueError, AttributeError):
        return jsonify({"error": "Bad Request", "message": "Неверный формат UUID"}), 400

    order = db.session.get(SalesOrder, order_uuid)
    if not order:
        return jsonify({"error": "Not Found", "message": "Заказ не найден"}), 404

    items = [
        {
            "sales_order_item_id": str(i.sales_order_item_id),
            "product_id": str(i.product_id),
            "quantity": float(i.quantity),
            "unit_price": float(i.unit_price),
            "discount": float(i.discount),
        }
        for i in order.items
    ]

    return jsonify({
        "sales_order_id": str(order.sales_order_id),
        "order_number": order.order_number,
        "order_date": order.order_date.isoformat() if order.order_date else None,
        "client_id": str(order.client_id),
        "executor_id": str(order.executor_id),
        "total_amount": float(order.total_amount) if order.total_amount else 0,
        "items": items,
    }), 200
