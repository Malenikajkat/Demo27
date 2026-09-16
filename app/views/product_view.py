"""API для управления продукцией."""
import uuid
from flask import request, Blueprint
from app.views.base_view import BaseAPIView
from app.services.product_service import ProductService

products_bp = Blueprint("products", __name__)


class ProductListAPI(BaseAPIView):
    """Список и создание продукции."""

    def __init__(self):
        self.service = ProductService()

    def get(self):
        """Список продукции."""
        products = self.service.get_all_dto()
        return self._success_response({"products": [p.to_dict() for p in products]})

    def post(self):
        """Создание продукции."""
        data = request.get_json()
        if not data or "name" not in data or "code" not in data:
            return self._error_response("Укажите name и code")

        try:
            product = self.service.create_product(name=data["name"], code=data["code"])
            return self._success_response({"message": "Продукция создана", "product_id": product.product_id}, 201)
        except ValueError as e:
            return self._error_response(str(e))


class ProductDetailAPI(BaseAPIView):
    """Получение, обновление, удаление продукции."""

    def __init__(self):
        self.service = ProductService()

    def get(self, product_id):
        """Получение продукции."""
        try:
            product_uuid = uuid.UUID(product_id)
        except (ValueError, AttributeError):
            return self._error_response("Неверный формат UUID")

        product = self.service.get_by_id_dto(product_uuid)
        if not product:
            return self._not_found_response("Продукция")
        return self._success_response(product.to_dict())

    def put(self, product_id):
        """Обновление продукции."""
        try:
            product_uuid = uuid.UUID(product_id)
        except (ValueError, AttributeError):
            return self._error_response("Неверный формат UUID")

        data = request.get_json()
        if not data:
            return self._error_response("Нет данных")

        try:
            product = self.service.update_product(product_uuid, name=data.get("name"), code=data.get("code"))
            if not product:
                return self._not_found_response("Продукция")
            return self._success_response({"message": "Продукция обновлена"})
        except ValueError as e:
            return self._error_response(str(e))

    def delete(self, product_id):
        """Удаление продукции."""
        try:
            product_uuid = uuid.UUID(product_id)
        except (ValueError, AttributeError):
            return self._error_response("Неверный формат UUID")

        product = self.service.get_by_id(product_uuid)
        if not product:
            return self._not_found_response("Продукция")

        self.service.delete(product_uuid)
        return self._success_response({"message": "Продукция удалена"})


products_bp.add_url_rule("/", view_func=ProductListAPI.as_view("products_list"))
products_bp.add_url_rule("/<product_id>", view_func=ProductDetailAPI.as_view("product_detail"))
