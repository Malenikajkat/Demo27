"""API для управления операциями."""
import uuid
from flask import request, Blueprint
from app.views.base_view import BaseAPIView
from app.services.operation_service import OperationService
from app.models import OperationPrice
from app.extensions import db
from sqlalchemy import select

operations_bp = Blueprint("operations", __name__)


class OperationListAPI(BaseAPIView):
    """Список и создание операций."""

    def __init__(self):
        self.service = OperationService()

    def get(self):
        """Список операций с текущей ценой."""
        operations = self.service.get_all_dto()
        result = []
        for o in operations:
            # Получаем текущую цену
            price_stmt = select(OperationPrice).where(
                OperationPrice.operation_id == o.operation_id
            ).order_by(OperationPrice.effective_date.desc()).limit(1)
            price_record = db.session.execute(price_stmt).scalar_one_or_none()
            current_price = float(price_record.price) if price_record else 0.0

            operation_data = o.to_dict()
            operation_data["current_price"] = current_price
            result.append(operation_data)
        return self._success_response({"operations": result})

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


class OperationPriceAPI(BaseAPIView):
    """Управление ценой операции."""

    def put(self, operation_id):
        """Обновление цены."""
        try:
            operation_uuid = uuid.UUID(operation_id)
        except (ValueError, AttributeError):
            return self._error_response("Неверный формат UUID")

        data = request.get_json()
        if not data or "price" not in data:
            return self._error_response("Укажите price")

        from app.models import Operation
        operation = db.session.get(Operation, operation_uuid)
        if not operation:
            return self._not_found_response("Операция")

        # Удаляем старые цены
        old_prices = db.session.execute(
            select(OperationPrice).where(OperationPrice.operation_id == operation_uuid)
        ).scalars().all()
        for old_price in old_prices:
            db.session.delete(old_price)

        # Создаём новую цену
        new_price = OperationPrice(
            operation_id=operation_uuid,
            price=data["price"]
        )
        db.session.add(new_price)
        db.session.commit()

        return self._success_response({"message": "Цена обновлена", "price": float(new_price.price)})


operations_bp.add_url_rule("/", view_func=OperationListAPI.as_view("operations_list"))
operations_bp.add_url_rule("/<operation_id>", view_func=OperationDetailAPI.as_view("operation_detail"))
operations_bp.add_url_rule("/<operation_id>/price", view_func=OperationPriceAPI.as_view("operation_price"))
