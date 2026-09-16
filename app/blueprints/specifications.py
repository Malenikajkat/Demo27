"""Blueprint для управления спецификациями."""
from flask import Blueprint, request, jsonify
from app.models import SpecificationMaterial, SpecificationOperation
from app.extensions import db

specifications_bp = Blueprint("specifications", __name__)


@specifications_bp.route("/materials/", methods=["GET"])
def list_spec_materials():
    """Список спецификаций материалов."""
    specs = db.session.execute(db.select(SpecificationMaterial)).scalars().all()
    return jsonify({
        "specifications": [
            {
                "spec_mat_id": str(s.spec_mat_id),
                "product_id": str(s.product_id),
                "material_id": str(s.material_id),
                "quantity_per_unit": float(s.quantity_per_unit),
            }
            for s in specs
        ]
    }), 200


@specifications_bp.route("/materials/", methods=["POST"])
def create_spec_material():
    """Создание спецификации материала."""
    data = request.get_json()
    if not data or "product_id" not in data or "material_id" not in data or "quantity_per_unit" not in data:
        return jsonify({
            "error": "Bad Request",
            "message": "Укажите product_id, material_id, quantity_per_unit",
        }), 400

    new_spec = SpecificationMaterial(
        product_id=data["product_id"],
        material_id=data["material_id"],
        quantity_per_unit=data["quantity_per_unit"],
    )
    db.session.add(new_spec)
    db.session.commit()

    return jsonify({
        "message": "Спецификация создана",
        "spec_mat_id": str(new_spec.spec_mat_id),
    }), 201


@specifications_bp.route("/operations/", methods=["GET"])
def list_spec_operations():
    """Список спецификаций операций."""
    specs = db.session.execute(db.select(SpecificationOperation)).scalars().all()
    return jsonify({
        "specifications": [
            {
                "spec_op_id": str(s.spec_op_id),
                "product_id": str(s.product_id),
                "operation_id": str(s.operation_id),
                "time_norm": float(s.time_norm),
                "op_quantity": float(s.op_quantity),
            }
            for s in specs
        ]
    }), 200


@specifications_bp.route("/operations/", methods=["POST"])
def create_spec_operation():
    """Создание спецификации операции."""
    data = request.get_json()
    if not data or "product_id" not in data or "operation_id" not in data:
        return jsonify({
            "error": "Bad Request",
            "message": "Укажите product_id и operation_id",
        }), 400

    new_spec = SpecificationOperation(
        product_id=data["product_id"],
        operation_id=data["operation_id"],
        time_norm=data.get("time_norm", 1.0),
        op_quantity=data.get("op_quantity", 1.0),
    )
    db.session.add(new_spec)
    db.session.commit()

    return jsonify({
        "message": "Спецификация создана",
        "spec_op_id": str(new_spec.spec_op_id),
    }), 201
