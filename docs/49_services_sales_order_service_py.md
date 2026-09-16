# Документация: app/services/sales_order_service.py

## Назначение

Сервис для работы с заказами покупателей: CRUD + DTO + расчёт стоимости.

## Класс `SalesOrderService(BaseService)`

### Методы

| Метод | Описание |
|-------|----------|
| `get_all_dto(skip, limit)` | Список заказов в DTO |
| `get_by_id_dto(order_id)` | Заказ по ID в DTO |
| `calculate_cost(order_id)` | Расчёт стоимости заказа |

### `calculate_cost(self, order_id: str) -> dict`

**Логика**:
1. Получает заказ по ID
2. Для каждой позиции:
   - Берёт `unit_price` из позиции
   - Если нет — ищет последнюю `ProductPrice`
   - Применяет скидку: `quantity * unit_price * (1 - discount/100)`
3. Суммирует все позиции
4. Возвращает детальную разбивку

**Ответ**:
```json
{
    "sales_order_id": "...",
    "order_number": "SO-2025-001",
    "items": [
        {"product_id": "...", "quantity": 10, "unit_price": 5000, "discount": 5, "item_total": 47500}
    ],
    "total_amount": 150000.0
}
```

## Зависимости и связи

| Элемент | Тип связи |
|---------|-----------|
| `BaseService` | Наследует |
| `SalesOrderRepository` | Использует |
| `SalesOrderDTO` | Использует |
| `ProductPrice` | Запрашивает цены |

## Важные замечания

1. **Приоритет цены**: `item.unit_price` > `ProductPrice` > 0
2. **Формула**: `quantity * unit_price * (1 - discount/100)`
3. **SQL-запрос**: Находит последнюю цену по `effective_date DESC`
