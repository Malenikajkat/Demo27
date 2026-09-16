"""Репозиторий для заказов."""
from app.repositories.base_repository import BaseRepository
from app.models import SalesOrder


class SalesOrderRepository(BaseRepository):
    """Репозиторий заказов."""

    def __init__(self):
        super().__init__(SalesOrder)
