"""Репозиторий для материалов."""
from app.repositories.base_repository import BaseRepository
from app.models import Material


class MaterialRepository(BaseRepository):
    """Репозиторий материалов."""

    def __init__(self):
        super().__init__(Material)
