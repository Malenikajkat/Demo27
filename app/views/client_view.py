"""API для управления клиентами."""
import uuid
from flask import request, Blueprint
from app.views.base_view import BaseAPIView
from app.services.client_service import ClientService

clients_bp = Blueprint("clients", __name__)


class ClientListAPI(BaseAPIView):
    """Список и создание клиентов."""

    def __init__(self):
        self.service = ClientService()

    def get(self):
        """Список клиентов."""
        clients = self.service.get_all_dto()
        return self._success_response({"clients": [c.to_dict() for c in clients]})

    def post(self):
        """Создание клиента."""
        data = request.get_json()
        if not data or "name" not in data or "client_type" not in data:
            return self._error_response("Укажите name и client_type")

        try:
            client = self.service.create_client(
                name=data["name"], client_type=data["client_type"],
                inn=data.get("inn"), address=data.get("address"), phone=data.get("phone")
            )
            return self._success_response({"message": "Клиент создан", "client_id": client.client_id}, 201)
        except ValueError as e:
            return self._error_response(str(e))


class ClientDetailAPI(BaseAPIView):
    """Получение, обновление, удаление клиента."""

    def __init__(self):
        self.service = ClientService()

    def get(self, client_id):
        """Получение клиента."""
        try:
            client_uuid = uuid.UUID(client_id)
        except (ValueError, AttributeError):
            return self._error_response("Неверный формат UUID")

        client = self.service.get_by_id_dto(client_uuid)
        if not client:
            return self._not_found_response("Клиент")
        return self._success_response(client.to_dict())

    def put(self, client_id):
        """Обновление клиента."""
        try:
            client_uuid = uuid.UUID(client_id)
        except (ValueError, AttributeError):
            return self._error_response("Неверный формат UUID")

        data = request.get_json()
        if not data:
            return self._error_response("Нет данных")

        try:
            client = self.service.update_client(
                client_uuid, name=data.get("name"), inn=data.get("inn"),
                address=data.get("address"), phone=data.get("phone"),
                client_type=data.get("client_type")
            )
            if not client:
                return self._not_found_response("Клиент")
            return self._success_response({"message": "Клиент обновлён"})
        except ValueError as e:
            return self._error_response(str(e))

    def delete(self, client_id):
        """Удаление клиента."""
        try:
            client_uuid = uuid.UUID(client_id)
        except (ValueError, AttributeError):
            return self._error_response("Неверный формат UUID")

        client = self.service.get_by_id(client_uuid)
        if not client:
            return self._not_found_response("Клиент")

        self.service.delete(client_uuid)
        return self._success_response({"message": "Клиент удалён"})


clients_bp.add_url_rule("/", view_func=ClientListAPI.as_view("clients_list"))
clients_bp.add_url_rule("/<client_id>", view_func=ClientDetailAPI.as_view("client_detail"))
