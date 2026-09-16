"""Blueprint для управления клиентами."""
import uuid
from flask import Blueprint, request, jsonify
from app.models import Client
from app.extensions import db

clients_bp = Blueprint("clients", __name__)


@clients_bp.route("/", methods=["GET"])
def list_clients():
    """Список всех клиентов."""
    clients = db.session.execute(db.select(Client)).scalars().all()
    return jsonify({
        "clients": [
            {
                "client_id": str(c.client_id),
                "name": c.name,
                "inn": c.inn,
                "address": c.address,
                "phone": c.phone,
                "client_type": c.client_type,
                "created_at": c.created_at.isoformat() if c.created_at else None,
            }
            for c in clients
        ]
    }), 200


@clients_bp.route("/", methods=["POST"])
def create_client():
    """Создание клиента."""
    data = request.get_json()
    if not data or "name" not in data or "client_type" not in data:
        return jsonify({
            "error": "Bad Request",
            "message": "Необходимо указать name и client_type",
        }), 400

    new_client = Client(
        name=data["name"],
        inn=data.get("inn"),
        address=data.get("address"),
        phone=data.get("phone"),
        client_type=data["client_type"],
    )
    db.session.add(new_client)
    db.session.commit()

    return jsonify({
        "message": "Клиент создан",
        "client_id": str(new_client.client_id),
    }), 201


@clients_bp.route("/<client_id>", methods=["GET"])
def get_client(client_id):
    """Получение клиента по ID."""
    try:
        client_uuid = uuid.UUID(client_id)
    except (ValueError, AttributeError):
        return jsonify({"error": "Bad Request", "message": "Неверный формат UUID"}), 400

    client = db.session.get(Client, client_uuid)
    if not client:
        return jsonify({"error": "Not Found", "message": "Клиент не найден"}), 404

    return jsonify({
        "client_id": str(client.client_id),
        "name": client.name,
        "inn": client.inn,
        "address": client.address,
        "phone": client.phone,
        "client_type": client.client_type,
        "created_at": client.created_at.isoformat() if client.created_at else None,
    }), 200


@clients_bp.route("/<client_id>", methods=["PUT"])
def update_client(client_id):
    """Обновление клиента."""
    try:
        client_uuid = uuid.UUID(client_id)
    except (ValueError, AttributeError):
        return jsonify({"error": "Bad Request", "message": "Неверный формат UUID"}), 400

    client = db.session.get(Client, client_uuid)
    if not client:
        return jsonify({"error": "Not Found", "message": "Клиент не найден"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "Bad Request", "message": "Нет данных"}), 400

    client.name = data.get("name", client.name)
    client.inn = data.get("inn", client.inn)
    client.address = data.get("address", client.address)
    client.phone = data.get("phone", client.phone)
    client.client_type = data.get("client_type", client.client_type)

    db.session.commit()
    return jsonify({"message": "Клиент обновлён"}), 200


@clients_bp.route("/<client_id>", methods=["DELETE"])
def delete_client(client_id):
    """Удаление клиента."""
    try:
        client_uuid = uuid.UUID(client_id)
    except (ValueError, AttributeError):
        return jsonify({"error": "Bad Request", "message": "Неверный формат UUID"}), 400

    client = db.session.get(Client, client_uuid)
    if not client:
        return jsonify({"error": "Not Found", "message": "Клиент не найден"}), 404

    db.session.delete(client)
    db.session.commit()
    return jsonify({"message": "Клиент удалён"}), 200
