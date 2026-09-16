# Документация: app/services/base_service.py

## Назначение

Базовый класс сервиса, делегирующий CRUD-операции репозиторию.

## Класс `BaseService`

### Инициализация

```python
def __init__(self, repository):
    self.repository = repository
```

### Методы

| Метод | Описание |
|-------|----------|
| `get_all(skip, limit)` | Делегирует `repository.get_all()` |
| `get_by_id(item_id)` | Делегирует `repository.get_by_id()` |
| `create(**kwargs)` | Делегирует `repository.create()` |
| `update(item_id, **kwargs)` | Делегирует `repository.update()` |
| `delete(item_id)` | Делегирует `repository.delete()` |

## Зависимости и связи

| Элемент | Тип связи |
|---------|-----------|
| Все сервисы | Наследуют |
| Все репозитории | Используют |
