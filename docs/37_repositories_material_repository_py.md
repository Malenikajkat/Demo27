# Документация: app/repositories/material_repository.py

## Назначение

Репозиторий для работы с таблицей `materials`. Наследует `BaseRepository`.

## Класс `MaterialRepository`

```python
class MaterialRepository(BaseRepository):
    def __init__(self):
        super().__init__(Material)
```

**Модель**: `Material`

**Наследуемые методы**: `get_all()`, `get_by_id()`, `create()`, `update()`, `delete()`

## Зависимости и связи

| Элемент | Тип связи | Описание |
|---------|-----------|----------|
| `base_repository.py` | Наследует | CRUD-методы |
| `app/models.py` | Использует | Модель `Material` |
| `app/services/material_service.py` | Использует | Сервисный слой |
