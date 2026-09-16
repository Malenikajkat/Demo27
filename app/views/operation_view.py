"""API для управления операциями."""
import uuid
from flask import request, Blueprint
from app.views.base_view import BaseAPIView
from app.services.operation_service import OperationService

operations_bp = Blueprint("operations", __name__)


class OperationListAPI(BaseAPIView):
    """Список и создание операций."""

    def __init__(self):
        self.service = OperationService()

    def get(self):
        """Список операций."""
        operations = self.service.get_all_dto()
        return self._success_response({"operations": [o.to_dict() for o in operations]})

    def post(self):
        """Создание операции."""
        data = request.get_json()
        if not data or "name" not in data or "code" not in data:
            return self._error_response("Укажите name и code")

        try:
            operation = self.service.create_operation(name=data["name"], code=data["code"])
            return self._success_response({"message": "Операция создана", "operation_id": operation.operation_id}, 201)
        except ValueError as e:
            return self._error_response(str(e))


class OperationDetailAPI(BaseAPIView):
    """Получение, обновление, удаление операции."""

    def __init__(self):
        self.service = OperationService()

    def get(self, operation_id):
        """Получение операции."""
        try:
            operation_uuid = uuid.UUID(operation_id)
        except (ValueError, AttributeError):
            return self._error_response("Неверный формат UUID")

        operation = self.service.get_by_id_dto(operation_uuid)
        if not operation:
            return self._not_found_response("Операция")
        return self._success_response(operation.to_dict())

    def put(self, operation_id):
        """Обновление операции."""
        try:
            operation_uuid = uuid.UUID(operation_id)
        except (ValueError, AttributeError):
            return self._error_response("Неверный формат UUID")

        data = request.get_json()
        if not data:
            return self._error_response("Нет данных")

        try:
            operation = self.service.update_operation(operation_uuid, name=data.get("name"), code=data.get("code"))
            if not operation:
                return self._not_found_response("Операция")
            return self._success_response({"message": "Операция обновлена"})
        except ValueError as e:
            return self._error_response(str(e))

    def delete(self, operation_id):
        """Удаление операции."""
        try:
            operation_uuid = uuid.UUID(operation_id)
        except (ValueError, AttributeError):
            return self._error_response("Неверный формат UUID")

        operation = self.service.get_by_id(operation_uuid)
        if not operation:
            return self._not_found_response("Операция")

        self.service.delete(operation_uuid)
        return self._success_response({"message": "Операция удалена"})


operations_bp.add_url_rule("/", view_func=OperationListAPI.as_view("operations_list"))
operations_bp.add_url_rule("/<operation_id>", view_func=OperationDetailAPI.as_view("operation_detail"))
