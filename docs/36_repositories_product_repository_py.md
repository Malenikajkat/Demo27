# Документация: app/repositories/product_repository.py

## Назначение

Репозиторий для работы с таблицей `products`. Наследует `BaseRepository`.

## Класс `ProductRepository`

```python
class ProductRepository(BaseRepository):
    def __init__(self):
        super().__init__(Product)
```

**Модель**: `Product`

**Наследуемые методы**: `get_all()`, `get_by_id()`, `create()`, `update()`, `delete()`

## Зависимости и связи

| Элемент | Тип связи | Описание |
|---------|-----------|----------|
| `base_repository.py` | Наследует | CRUD-методы |
| `app/models.py` | Использует | Модель `Product` |
| `app/services/product_service.py` | Использует | Сервисный слой |
