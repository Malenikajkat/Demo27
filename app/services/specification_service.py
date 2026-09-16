"""Сервисы для работы со спецификациями."""
from app.extensions import db
from app.models import SpecificationMaterial, SpecificationOperation


class SpecificationMaterialService:
    """Сервис для спецификаций материалов."""

    def get_all(self):
        """Получить все спецификации."""
        return db.session.execute(db.select(SpecificationMaterial)).scalars().all()


class SpecificationOperationService:
    """Сервис для спецификаций операций."""

    def get_all(self):
        """Получить все спецификации."""
        return db.session.execute(db.select(SpecificationOperation)).scalars().all()
