"""API для управления материалами."""
import uuid
from flask import request, Blueprint
from app.views.base_view import BaseAPIView
from app.services.material_service import MaterialService

materials_bp = Blueprint("materials", __name__)


class MaterialListAPI(BaseAPIView):
    """Список и создание материалов."""

    def __init__(self):
        self.service = MaterialService()

    def get(self):
        """Список материалов."""
        materials = self.service.get_all_dto()
        return self._success_response({"materials": [m.to_dict() for m in materials]})

    def post(self):
        """Создание материала."""
        data = request.get_json()
        if not data or "name" not in data or "code" not in data:
            return self._error_response("Укажите name и code")

        try:
            material = self.service.create_material(name=data["name"], code=data["code"])
            return self._success_response({"message": "Материал создан", "material_id": material.material_id}, 201)
        except ValueError as e:
            return self._error_response(str(e))


class MaterialDetailAPI(BaseAPIView):
    """Получение, обновление, удаление материала."""

    def __init__(self):
        self.service = MaterialService()

    def get(self, material_id):
        """Получение материала."""
        try:
            material_uuid = uuid.UUID(material_id)
        except (ValueError, AttributeError):
            return self._error_response("Неверный формат UUID")

        material = self.service.get_by_id_dto(material_uuid)
        if not material:
            return self._not_found_response("Материал")
        return self._success_response(material.to_dict())

    def put(self, material_id):
        """Обновление материала."""
        try:
            material_uuid = uuid.UUID(material_id)
        except (ValueError, AttributeError):
            return self._error_response("Неверный формат UUID")

        data = request.get_json()
        if not data:
            return self._error_response("Нет данных")

        try:
            material = self.service.update_material(material_uuid, name=data.get("name"), code=data.get("code"))
            if not material:
                return self._not_found_response("Материал")
            return self._success_response({"message": "Материал обновлён"})
        except ValueError as e:
            return self._error_response(str(e))

    def delete(self, material_id):
        """Удаление материала."""
        try:
            material_uuid = uuid.UUID(material_id)
        except (ValueError, AttributeError):
            return self._error_response("Неверный формат UUID")

        material = self.service.get_by_id(material_uuid)
        if not material:
            return self._not_found_response("Материал")

        self.service.delete(material_uuid)
        return self._success_response({"message": "Материал удалён"})


materials_bp.add_url_rule("/", view_func=MaterialListAPI.as_view("materials_list"))
materials_bp.add_url_rule("/<material_id>", view_func=MaterialDetailAPI.as_view("material_detail"))
