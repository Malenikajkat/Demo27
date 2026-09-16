"""Сервис для работы с пользователями."""
from typing import List
from app.services.base_service import BaseService
from app.repositories.user_repository import UserRepository
from app.dtos.user_dto import UserDTO
from app.auth import hash_password


class UserService(BaseService):
    """Сервис для работы с пользователями."""

    def __init__(self):
        super().__init__(UserRepository())

    def get_all_dto(self) -> List[UserDTO]:
        """Получить список пользователей в формате DTO."""
        users = self.get_all()
        return [UserDTO.from_model(u) for u in users]

    def create_user(self, login: str, password: str, role: str = "Пользователь"):
        """Создание пользователя."""
        return self.repository.create(
            login=login, password_hash=hash_password(password), role=role
        )

    def update_user(self, user_id, role=None, is_blocked=None):
        """Обновление пользователя."""
        return self.repository.update(user_id, role=role, is_blocked=is_blocked)
