"""Сервис для работы с клиентами."""
from typing import List, Optional
from app.services.base_service import BaseService
from app.repositories.client_repository import ClientRepository
from app.dtos.client_dto import ClientDTO


class ClientService(BaseService):
    """Сервис для работы с клиентами."""

    def __init__(self):
        super().__init__(ClientRepository())

    def get_all_dto(self, skip: int = 0, limit: int = 100) -> List[ClientDTO]:
        """Получить список клиентов в формате DTO."""
        clients = self.get_all(skip, limit)
        return [ClientDTO.from_model(c) for c in clients]

    def get_by_id_dto(self, client_id) -> Optional[ClientDTO]:
        """Получить клиента по ID в формате DTO."""
        client = self.get_by_id(client_id)
        return ClientDTO.from_model(client) if client else None

    def create_client(self, name: str, client_type: str, inn=None, address=None, phone=None):
        """Создание клиента."""
        return self.repository.create(
            name=name, client_type=client_type, inn=inn, address=address, phone=phone
        )

    def update_client(self, client_id, name=None, inn=None, address=None, phone=None, client_type=None):
        """Обновление клиента."""
        return self.repository.update(
            client_id, name=name, inn=inn, address=address, phone=phone, client_type=client_type
        )
