# Документация: app/views/sales_order_view.py

## Назначение

Class-Based API для заказов покупателей: CRUD + расчёт стоимости.

## Классы

### `SalesOrderListAPI(BaseAPIView)`
| Метод | Маршрут | Описание |
|-------|---------|----------|
| `get()` | GET /api/sales-orders/ | Список заказов |
| `post()` | POST /api/sales-orders/ | Создание заказа с позициями |

### `SalesOrderDetailAPI(BaseAPIView)`
| Метод | Маршрут | Описание |
|-------|---------|----------|
| `get(sales_order_id)` | GET /api/sales-orders/<id> | Детали заказа с позициями |

### `SalesOrderCostCalculationAPI(BaseAPIView)`
| Метод | Маршрут | Описание |
|-------|---------|----------|
| `get(sales_order_id)` | GET /api/sales-orders/<id>/cost-calculation | Расчёт стоимости |

## Зависимости и связи

| Элемент | Тип связи |
|---------|-----------|
| `BaseAPIView` | Наследует |
| `SalesOrderService` | Использует |
| `SalesOrder`, `SalesOrderItem` | Создаёт напрямую |

## Важные замечания

1. **cost-calculation**: Отдельный маршрут для расчёта стоимости.
2. **Прямая работа с БД**: Создание заказа через `db.session`, а не через сервис.
