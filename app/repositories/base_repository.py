"""
Базовый репозиторий для работы с БД.

Студенты: этот файл демонстрирует Паттерн "Repository".

Что такое Repository Pattern?
- Это абстракция над слоем данных (database).
- Вместо того чтобы писать SQL/SQLAlchemy запросы в каждом сервисе,
  мы выносим их в репозиторий.
- Сервисы работают с репозиторием как с "коллекцией объектов в памяти",
  не зная, что данные хранятся в PostgreSQL.

Зачем нужен базовый класс?
- Все сущности (Client, Product, Order) имеют одинаковые CRUD-операции.
- BaseRepository предоставляет общий интерфейс: get_all, get_by_id, create, update, delete.
- Конкретные репозитории наследуются от BaseRepository и добавляют
  специфичную логику (например, get_by_name, get_active).

Преимущества:
1. Тестируемость: можно подменить репозиторий моком (Mock) при тестировании.
2. Переиспользование: общий код написан один раз.
3. Чистота: сервисы содержат бизнес-логику, а не SQL-запросы.

**kwargs — это словарь произвольных именованных аргументов.
Например: repository.update(id, name="New Name", price=100)
внутри превращается в: kwargs = {"name": "New Name", "price": 100}

setattr(obj, key, value) — динамически устанавливает атрибут объекта.
Эквивалентно: obj.name = "New Name"
"""
from typing import Any, List, Optional
from app.extensions import db


class BaseRepository:
    """Базовый класс репозитория.

    Студенты: self.model — это ORM-класс (например, Client, Product).
    Мы не создаём экземпляр модели, а работаем с классом, потому что
    SQLAlchemy использует классы для построения SQL-запросов.
    """

    def __init__(self, model):
        self.model = model

    def get_all(self, skip: int = 0, limit: int = 100) -> List:
        """Получить все записи с пагинацией (skip/limit)."""
        return db.session.execute(db.select(self.model).offset(skip).limit(limit)).scalars().all()

    def get_by_id(self, item_id) -> Optional[Any]:
        """Получить запись по ID. Возвращает None, если не найдена."""
        return db.session.get(self.model, item_id)

    def create(self, **kwargs):
        """Создать новую запись.

        kwargs — это словарь полей для создания объекта.
        Например: {"name": "Client A", "client_type": "Покупатель"}
        """
        item = self.model(**kwargs)
        db.session.add(item)
        db.session.commit()
        return item

    def update(self, item_id, **kwargs):
        """Обновить запись по ID.

        Студенты: мы обновляем только те поля, которые переданы в kwargs,
        И только если их значение не None. Это позволяет частично обновлять объект.
        """
        item = self.get_by_id(item_id)
        if item:
            for key, value in kwargs.items():
                if value is not None:
                    setattr(item, key, value)
            db.session.commit()
        return item

    def delete(self, item_id):
        """Удалить запись по ID. Возвращает True, если удалено, False если не найдено."""
        item = self.get_by_id(item_id)
        if item:
            db.session.delete(item)
            db.session.commit()
            return True
        return False
