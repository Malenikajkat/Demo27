# Документация: app/dtos/sales_order_dto.py

## Назначение

Содержит **Dataclass SalesOrderDTO** и **SalesOrderItemDTO** для сериализации заказов покупателей с вложенными позициями.

## Класс `SalesOrderItemDTO`

### Поля

| Поле | Тип | По умолчанию | Описание |
|------|-----|-------------|----------|
| `sales_order_item_id` | `str` | — | UUID позиции |
| `product_id` | `str` | — | UUID продукта |
| `quantity` | `float` | — | Количество |
| `unit_price` | `float` | — | Цена за единицу |
| `discount` | `float` | — | Скидка |

### Методы

#### `from_model(cls, item) -> SalesOrderItemDTO`

Создаёт DTO из модели `SalesOrderItem`. Конвертирует Decimal в float.

#### `to_dict(self) -> dict`

Конвертирует в словарь.

## Класс `SalesOrderDTO`

### Поля

| Поле | Тип | По умолчанию | Описание |
|------|-----|-------------|----------|
| `sales_order_id` | `str` | — | UUID заказа |
| `order_number` | `str` | — | Номер заказа |
| `order_date` | `Optional[str]` | `None` | Дата (ISO) |
| `client_id` | `str` | `""` | UUID покупателя |
| `executor_id` | `str` | `""` | UUID исполнителя |
| `total_amount` | `float` | `0.0` | Общая сумма |
| `created_at` | `Optional[str]` | `None` | Дата создания (ISO) |
| `items` | `Optional[List[SalesOrderItemDTO]]` | `None` | Позиции заказа |

### Методы

#### `from_model(cls, order) -> SalesOrderDTO`

Создаёт DTO из модели `SalesOrder`. Рекурсивно конвертирует вложенные `items`.

**Логика**:
```python
items = [SalesOrderItemDTO.from_model(item) for item in order.items] if order.items else None
```

#### `to_dict(self) -> dict`

Конвертирует в словарь, включая вложенные items.

## Пример использования

```python
order = db.session.get(SalesOrder, order_id)
dto = SalesOrderDTO.from_model(order)
data = dto.to_dict()
# {
#     "sales_order_id": "...",
#     "order_number": "SO-2025-001",
#     "items": [
#         {"product_id": "...", "quantity": 10.0, "unit_price": 5000.0, ...}
#     ]
# }
```

## Зависимости и связи

| Элемент | Тип связи | Описание |
|---------|-----------|----------|
| `app/models.py` | Использует | `SalesOrder`, `SalesOrderItem` |
| `app/services/sales_order_service.py` | Использует | DTO-методы |

## Важные замечания

1. **Вложенность**: SalesOrderDTO содержит список SalesOrderItemDTO.
2. **Decimal → float**: Все числовые поля конвертируются в float для JSON.
3. **Optional items**: items может быть None, если у заказа нет позиций.
