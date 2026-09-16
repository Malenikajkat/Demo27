"""Репозиторий для продукции."""
from app.repositories.base_repository import BaseRepository
from app.models import Product


class ProductRepository(BaseRepository):
    """Репозиторий продукции."""

    def __init__(self):
        super().__init__(Product)
