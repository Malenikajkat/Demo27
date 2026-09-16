# Документация: app/repositories/operation_repository.py

## Назначение

Репозиторий для работы с таблицей `operations`. Наследует `BaseRepository`.

## Класс `OperationRepository`

```python
class OperationRepository(BaseRepository):
    def __init__(self):
        super().__init__(Operation)
```

**Модель**: `Operation`

**Наследуемые методы**: `get_all()`, `get_by_id()`, `create()`, `update()`, `delete()`

## Зависимости и связи

| Элемент | Тип связи | Описание |
|---------|-----------|----------|
| `base_repository.py` | Наследует | CRUD-методы |
| `app/models.py` | Использует | Модель `Operation` |
| `app/services/operation_service.py` | Использует | Сервисный слой |
