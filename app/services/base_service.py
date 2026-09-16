"""Базовый сервис для работы с репозиторием."""
from typing import List, Optional


class BaseService:
    """Базовый класс сервиса."""

    def __init__(self, repository):
        self.repository = repository

    def get_all(self, skip: int = 0, limit: int = 100) -> List:
        """Получить все записи."""
        return self.repository.get_all(skip=skip, limit=limit)

    def get_by_id(self, item_id) -> Optional:
        """Получить запись по ID."""
        return self.repository.get_by_id(item_id)

    def create(self, **kwargs):
        """Создать запись."""
        return self.repository.create(**kwargs)

    def update(self, item_id, **kwargs):
        """Обновить запись."""
        return self.repository.update(item_id, **kwargs)

    def delete(self, item_id):
        """Удалить запись."""
        return self.repository.delete(item_id)
