"""API для управления продукцией."""
import uuid
from flask import request, Blueprint
from app.views.base_view import BaseAPIView
from app.services.product_service import ProductService
from app.models import ProductPrice
from app.extensions import db
from sqlalchemy import select

products_bp = Blueprint("products", __name__)


class ProductListAPI(BaseAPIView):
    """Список и создание продукции."""

    def __init__(self):
        self.service = ProductService()

    def get(self):
        """Список продукции с текущей ценой."""
        products = self.service.get_all_dto()
        result = []
        for p in products:
            # Получаем текущую цену
            price_stmt = select(ProductPrice).where(
                ProductPrice.product_id == p.product_id
            ).order_by(ProductPrice.effective_date.desc()).limit(1)
            price_record = db.session.execute(price_stmt).scalar_one_or_none()
            current_price = float(price_record.price) if price_record else 0.0

            product_data = p.to_dict()
            product_data["current_price"] = current_price
            result.append(product_data)
        return self._success_response({"products": result})

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


class ProductPriceAPI(BaseAPIView):
    """Управление ценой продукции."""

    def get(self, product_id):
        """Получение текущей цены."""
        try:
            product_uuid = uuid.UUID(product_id)
        except (ValueError, AttributeError):
            return self._error_response("Неверный формат UUID")

        stmt = select(ProductPrice).where(
            ProductPrice.product_id == product_uuid
        ).order_by(ProductPrice.effective_date.desc()).limit(1)
        price_record = db.session.execute(stmt).scalar_one_or_none()

        if not price_record:
            return self._success_response({"product_id": str(product_uuid), "price": 0.0})

        return self._success_response({
            "product_id": str(product_uuid),
            "price": float(price_record.price)
        })

    def put(self, product_id):
        """Обновление цены."""
        try:
            product_uuid = uuid.UUID(product_id)
        except (ValueError, AttributeError):
            return self._error_response("Неверный формат UUID")

        data = request.get_json()
        if not data or "price" not in data:
            return self._error_response("Укажите price")

        from app.models import Product
        product = db.session.get(Product, product_uuid)
        if not product:
            return self._not_found_response("Продукция")

        # Удаляем старые цены
        old_prices = db.session.execute(
            select(ProductPrice).where(ProductPrice.product_id == product_uuid)
        ).scalars().all()
        for old_price in old_prices:
            db.session.delete(old_price)

        # Создаём новую цену
        new_price = ProductPrice(
            product_id=product_uuid,
            price=data["price"]
        )
        db.session.add(new_price)
        db.session.commit()

        return self._success_response({"message": "Цена обновлена", "price": float(new_price.price)})


class ProductPriceListAPI(BaseAPIView):
    """Список цен продукции."""

    def get(self):
        """Список всех цен."""
        prices = db.session.execute(
            select(ProductPrice).order_by(ProductPrice.effective_date.desc())
        ).scalars().all()

        result = []
        for p in prices:
            result.append({
                "product_price_id": str(p.product_price_id),
                "product_id": str(p.product_id),
                "product_name": p.product.name if p.product else "",
                "price": float(p.price),
                "effective_date": p.effective_date.isoformat() if p.effective_date else None
            })

        return self._success_response({"prices": result})


products_bp.add_url_rule("/", view_func=ProductListAPI.as_view("products_list"))
products_bp.add_url_rule("/<product_id>", view_func=ProductDetailAPI.as_view("product_detail"))
products_bp.add_url_rule("/<product_id>/price", view_func=ProductPriceAPI.as_view("product_price"))
