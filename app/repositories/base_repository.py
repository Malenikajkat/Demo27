"""Базовый репозиторий для работы с БД."""
from typing import List, Optional
from app.extensions import db


class BaseRepository:
    """Базовый класс репозитория."""

    def __init__(self, model):
        self.model = model

    def get_all(self, skip: int = 0, limit: int = 100) -> List:
        """Получить все записи."""
        return db.session.execute(db.select(self.model).offset(skip).limit(limit)).scalars().all()

    def get_by_id(self, item_id) -> Optional:
        """Получить запись по ID."""
        return db.session.get(self.model, item_id)

    def create(self, **kwargs):
        """Создать запись."""
        item = self.model(**kwargs)
        db.session.add(item)
        db.session.commit()
        return item

    def update(self, item_id, **kwargs):
        """Обновить запись."""
        item = self.get_by_id(item_id)
        if item:
            for key, value in kwargs.items():
                if value is not None:
                    setattr(item, key, value)
            db.session.commit()
        return item

    def delete(self, item_id):
        """Удалить запись."""
        item = self.get_by_id(item_id)
        if item:
            db.session.delete(item)
            db.session.commit()
            return True
        return False
