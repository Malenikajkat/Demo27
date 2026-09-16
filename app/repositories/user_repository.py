"""Репозиторий для пользователей."""
from app.repositories.base_repository import BaseRepository
from app.models import User
from app.extensions import db


class UserRepository(BaseRepository):
    """Репозиторий пользователей."""

    def __init__(self):
        super().__init__(User)

    def find_by_login(self, login: str):
        """Найти пользователя по логину."""
        from sqlalchemy import select
        return db.session.execute(select(User).where(User.login == login)).scalar_one_or_none()

    def increment_failed_attempts(self, user_id: int):
        """Увеличить счётчик неудачных попыток."""
        user = self.get_by_id(user_id)
        if user:
            user.failed_attempts += 1
            if user.failed_attempts >= 3:
                user.is_blocked = True
            db.session.commit()
