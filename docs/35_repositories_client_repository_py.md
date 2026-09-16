# Документация: app/repositories/client_repository.py

## Назначение

Репозиторий для работы с таблицей `clients`. Наследует `BaseRepository`.

## Класс `ClientRepository`

```python
class ClientRepository(BaseRepository):
    def __init__(self):
        super().__init__(Client)
```

**Модель**: `Client`

**Наследуемые методы**: `get_all()`, `get_by_id()`, `create()`, `update()`, `delete()`

## Зависимости и связи

| Элемент | Тип связи | Описание |
|---------|-----------|----------|
| `base_repository.py` | Наследует | CRUD-методы |
| `app/models.py` | Использует | Модель `Client` |
| `app/services/client_service.py` | Использует | Сервисный слой |
