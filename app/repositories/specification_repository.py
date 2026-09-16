"""Репозитории для спецификаций."""
from app.repositories.base_repository import BaseRepository
from app.models import SpecificationMaterial, SpecificationOperation


class SpecificationMaterialRepository(BaseRepository):
    """Репозиторий спецификаций материалов."""

    def __init__(self):
        super().__init__(SpecificationMaterial)


class SpecificationOperationRepository(BaseRepository):
    """Репозиторий спецификаций операций."""

    def __init__(self):
        super().__init__(SpecificationOperation)
