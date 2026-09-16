"""Сервис для работы с продукцией."""
from typing import List, Optional
from app.services.base_service import BaseService
from app.repositories.product_repository import ProductRepository
from app.dtos.product_dto import ProductDTO


class ProductService(BaseService):
    """Сервис для работы с продукцией."""

    def __init__(self):
        super().__init__(ProductRepository())

    def get_all_dto(self, skip: int = 0, limit: int = 100) -> List[ProductDTO]:
        """Получить список продукции в формате DTO."""
        products = self.get_all(skip, limit)
        return [ProductDTO.from_model(p) for p in products]

    def get_by_id_dto(self, product_id) -> Optional[ProductDTO]:
        """Получить продукцию по ID в формате DTO."""
        product = self.get_by_id(product_id)
        return ProductDTO.from_model(product) if product else None

    def create_product(self, name: str, code: str):
        """Создание продукции."""
        return self.repository.create(name=name, code=code)

    def update_product(self, product_id, name=None, code=None):
        """Обновление продукции."""
        return self.repository.update(product_id, name=name, code=code)
