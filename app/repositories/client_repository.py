"""Репозиторий для клиентов."""
from app.repositories.base_repository import BaseRepository
from app.models import Client


class ClientRepository(BaseRepository):
    """Репозиторий клиентов."""

    def __init__(self):
        super().__init__(Client)
