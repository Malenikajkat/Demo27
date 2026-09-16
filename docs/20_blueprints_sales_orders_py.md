# Документация: app/blueprints/sales_orders.py

## Назначение

Файл `app/blueprints/sales_orders.py` реализует **API для управления заказами покупателей**. Поддерживает создание заказов с вложенными позициями (товарами), получение списка и детальный просмотр заказа.

## Blueprint

```python
sales_orders_bp = Blueprint("sales_orders", __name__)
```

Регистрируется с префиксом `/api/sales-orders`.

## Маршруты (Endpoints)

### 1. `GET /api/sales-orders/` — Список заказов

**Функция**: `list_sales_orders()`

**Ответ 200**:
```json
{
    "sales_orders": [
        {
            "sales_order_id": "uuid",
            "order_number": "SO-2025-001",
            "order_date": "2025-01-15",
            "client_id": "uuid-покупателя",
            "executor_id": "uuid-исполнителя",
            "total_amount": 150000.00,
            "created_at": "2025-01-15T10:30:00"
        }
    ]
}
```

### 2. `POST /api/sales-orders/` — Создание заказа

**Функция**: `create_sales_order()`

**Тело запроса**:
```json
{
    "order_number": "SO-2025-001",
    "order_date": "2025-01-15",
    "client_id": "uuid-покупателя",
    "executor_id": "uuid-исполнителя",
    "items": [
        {
            "product_id": "uuid-продукта",
            "quantity": 10,
            "unit_price": 5000.00,
            "discount": 5.0
        }
    ]
}
```

**Обязательные поля**: `order_number`, `order_date`, `client_id`, `executor_id`

**Ответ 201**:
```json
{
    "message": "Заказ создан",
    "sales_order_id": "uuid"
}
```

**Логика**:
1. Валидация обязательных полей
2. Валидация UUID клиента и исполнителя
3. Парсинг даты заказа
4. Создание SalesOrder
5. Создание SalesOrderItem для каждой позиции (если есть)
6. Коммит транзакции

### 3. `GET /api/sales-orders/<sales_order_id>` — Детали заказа

**Функция**: `get_sales_order(sales_order_id)`

**Ответ 200**:
```json
{
    "sales_order_id": "uuid",
    "order_number": "SO-2025-001",
    "order_date": "2025-01-15",
    "client_id": "uuid",
    "executor_id": "uuid",
    "total_amount": 150000.00,
    "items": [
        {
            "sales_order_item_id": "uuid",
            "product_id": "uuid",
            "quantity": 10,
            "unit_price": 5000.00,
            "discount": 5.0
        }
    ]
}
```

## Валидация

### UUID
Все UUID валидируются через `uuid.UUID()`.

### Дата
Парсится из ISO-формата: `date.fromisoformat("2025-01-15")`.

## Ключевая логика

### Вложенные позиции
Заказ может содержать несколько позиций (`items`), каждая с количеством, ценой и скидкой.

### Двойная роль клиента
`client_id` (покупатель) и `executor_id` (исполнитель) — оба ссылаются на таблицу `clients`.

### Отсутствие авторизации
Нет `@login_required` — эндпоинты доступны без авторизации.

## Зависимости и связи

| Элемент | Тип связи | Описание |
|---------|-----------|----------|
| `app/models.py` | Использует | `SalesOrder`, `SalesOrderItem` |
| `app/extensions.py` | Использует | `db.session` |
| `web/sales-orders.html` | Использует | Фронтенд |
| `app/services/sales_order_service.py` | Аналог | Сервис с расчётом стоимости |
| `app/views/sales_order_view.py` | Аналог | Class-Based View |

## Важные замечания

1. **Нет расчёта total_amount**: При создании заказа общая сумма не вычисляется автоматически.
2. **Items опциональны**: Заказ можно создать без позиций.
3. **Пропуск ошибок items**: Если product_id невалиден, позиция пропускается (`continue`).
4. **Нет PUT/DELETE**: Обновление и удаление заказов не реализованы.
