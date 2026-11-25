"""
Базовый сервис для работы с репозиторием.

Студенты: этот файл демонстрирует Паттерн "Service Layer".

Что такое Service Layer?
- Это промежуточный слой между контроллерами (Blueprint/Views) и репозиториями.
- Сервисы содержат бизнес-логику: валидацию, расчёты, вызовы внешних API.
- В текущем проекте сервисы — это тонкая обёртка над репозиториями.
  Это упрощение, которое можно расширить в будущем.

Зачем нужен Service, если есть Repository?
- Repository отвечает ЗА ДАННЫЕ (как получить/сохранить).
- Service отвечает ЗА БИЗНЕС-ЛОГИКУ (что делать с данными).
- Пример: при создании клиента сервис может проверить inn, отправить email,
  записать в лог. Репозиторий просто сохраняет в БД.

Паттерн Dependency Injection:
- Repository передаётся в конструктор сервиса.
- Это позволяет подменять репозиторий (например, на Mock при тестировании).
- Сервис не знает, откуда данные — из PostgreSQL, MongoDB или файла.
"""
from typing import Any, List, Optional


class BaseService:
    """Базовый класс сервиса.

    Студенты: self.repository — это экземпляр конкретного репозитория
    (например, ClientRepository). Методы здесь — это "проброс" (pass-through)
    запроса в репозиторий. В реальном проекте здесь была бы бизнес-логика.
    """

    def __init__(self, repository):
        self.repository = repository

    def get_all(self, skip: int = 0, limit: int = 100) -> List:
        """Получить все записи с пагинацией."""
        return self.repository.get_all(skip=skip, limit=limit)

    def get_by_id(self, item_id) -> Optional[Any]:
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
