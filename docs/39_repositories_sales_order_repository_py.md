# Документация: app/repositories/sales_order_repository.py

## Назначение

Репозиторий для работы с таблицей `sales_orders`. Наследует `BaseRepository`.

## Класс `SalesOrderRepository`

```python
class SalesOrderRepository(BaseRepository):
    def __init__(self):
        super().__init__(SalesOrder)
```

**Модель**: `SalesOrder`

**Наследуемые методы**: `get_all()`, `get_by_id()`, `create()`, `update()`, `delete()`

## Зависимости и связи

| Элемент | Тип связи | Описание |
|---------|-----------|----------|
| `base_repository.py` | Наследует | CRUD-методы |
| `app/models.py` | Использует | Модель `SalesOrder` |
| `app/services/sales_order_service.py` | Использует | Сервисный слой |
