"""Blueprint для управления материалами."""
from flask import Blueprint, request, jsonify
from app.models import Material
from app.extensions import db

materials_bp = Blueprint("materials", __name__)


@materials_bp.route("/", methods=["GET"])
def list_materials():
    """Список всех материалов."""
    materials = db.session.execute(db.select(Material)).scalars().all()
    return jsonify({
        "materials": [
            {
                "material_id": str(m.material_id),
                "name": m.name,
                "code": m.code,
                "created_at": m.created_at.isoformat() if m.created_at else None,
            }
            for m in materials
        ]
    }), 200


@materials_bp.route("/", methods=["POST"])
def create_material():
    """Создание материала."""
    data = request.get_json()
    if not data or "name" not in data or "code" not in data:
        return jsonify({
            "error": "Bad Request",
            "message": "Необходимо указать name и code",
        }), 400

    new_material = Material(name=data["name"], code=data["code"])
    db.session.add(new_material)
    db.session.commit()

    return jsonify({
        "message": "Материал создан",
        "material_id": str(new_material.material_id),
    }), 201
