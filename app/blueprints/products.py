"""Blueprint для управления продукцией."""
from flask import Blueprint, request, jsonify
from app.models import Product
from app.extensions import db

products_bp = Blueprint("products", __name__)


@products_bp.route("/", methods=["GET"])
def list_products():
    """Список всей продукции."""
    products = db.session.execute(db.select(Product)).scalars().all()
    return jsonify({
        "products": [
            {
                "product_id": str(p.product_id),
                "name": p.name,
                "code": p.code,
                "created_at": p.created_at.isoformat() if p.created_at else None,
            }
            for p in products
        ]
    }), 200


@products_bp.route("/", methods=["POST"])
def create_product():
    """Создание продукции."""
    data = request.get_json()
    if not data or "name" not in data or "code" not in data:
        return jsonify({
            "error": "Bad Request",
            "message": "Необходимо указать name и code",
        }), 400

    new_product = Product(name=data["name"], code=data["code"])
    db.session.add(new_product)
    db.session.commit()

    return jsonify({
        "message": "Продукция создана",
        "product_id": str(new_product.product_id),
    }), 201
