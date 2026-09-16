"""Сервис для работы с материалами."""
from typing import List, Optional
from app.services.base_service import BaseService
from app.repositories.material_repository import MaterialRepository
from app.dtos.material_dto import MaterialDTO


class MaterialService(BaseService):
    """Сервис для работы с материалами."""

    def __init__(self):
        super().__init__(MaterialRepository())

    def get_all_dto(self, skip: int = 0, limit: int = 100) -> List[MaterialDTO]:
        """Получить список материалов в формате DTO."""
        materials = self.get_all(skip, limit)
        return [MaterialDTO.from_model(m) for m in materials]

    def get_by_id_dto(self, material_id) -> Optional[MaterialDTO]:
        """Получить материал по ID в формате DTO."""
        material = self.get_by_id(material_id)
        return MaterialDTO.from_model(material) if material else None

    def create_material(self, name: str, code: str):
        """Создание материала."""
        return self.repository.create(name=name, code=code)

    def update_material(self, material_id, name=None, code=None):
        """Обновление материала."""
        return self.repository.update(material_id, name=name, code=code)
