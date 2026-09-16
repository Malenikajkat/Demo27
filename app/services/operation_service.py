"""Сервис для работы с операциями."""
from typing import List, Optional
from app.services.base_service import BaseService
from app.repositories.operation_repository import OperationRepository
from app.dtos.operation_dto import OperationDTO


class OperationService(BaseService):
    """Сервис для работы с операциями."""

    def __init__(self):
        super().__init__(OperationRepository())

    def get_all_dto(self, skip: int = 0, limit: int = 100) -> List[OperationDTO]:
        """Получить список операций в формате DTO."""
        operations = self.get_all(skip, limit)
        return [OperationDTO.from_model(o) for o in operations]

    def get_by_id_dto(self, operation_id) -> Optional[OperationDTO]:
        """Получить операцию по ID в формате DTO."""
        operation = self.get_by_id(operation_id)
        return OperationDTO.from_model(operation) if operation else None

    def create_operation(self, name: str, code: str):
        """Создание операции."""
        return self.repository.create(name=name, code=code)

    def update_operation(self, operation_id, name=None, code=None):
        """Обновление операции."""
        return self.repository.update(operation_id, name=name, code=code)
