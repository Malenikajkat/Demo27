"""Репозиторий для операций."""
from app.repositories.base_repository import BaseRepository
from app.models import Operation


class OperationRepository(BaseRepository):
    """Репозиторий операций."""

    def __init__(self):
        super().__init__(Operation)
