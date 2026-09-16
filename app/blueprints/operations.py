"""Blueprint для управления операциями."""
from flask import Blueprint, request, jsonify
from app.models import Operation
from app.extensions import db

operations_bp = Blueprint("operations", __name__)


@operations_bp.route("/", methods=["GET"])
def list_operations():
    """Список всех операций."""
    operations = db.session.execute(db.select(Operation)).scalars().all()
    return jsonify({
        "operations": [
            {
                "operation_id": str(o.operation_id),
                "name": o.name,
                "code": o.code,
                "created_at": o.created_at.isoformat() if o.created_at else None,
            }
            for o in operations
        ]
    }), 200


@operations_bp.route("/", methods=["POST"])
def create_operation():
    """Создание операции."""
    data = request.get_json()
    if not data or "name" not in data or "code" not in data:
        return jsonify({
            "error": "Bad Request",
            "message": "Необходимо указать name и code",
        }), 400

    new_operation = Operation(name=data["name"], code=data["code"])
    db.session.add(new_operation)
    db.session.commit()

    return jsonify({
        "message": "Операция создана",
        "operation_id": str(new_operation.operation_id),
    }), 201
