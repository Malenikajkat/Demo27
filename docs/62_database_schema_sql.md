# Документация: database/schema.sql

## Назначение

Полная SQL-схема для PostgreSQL с 13 таблицами, ограничениями, индексами и тестовыми данными.

## Таблицы

| Таблица | PK | Описание |
|---------|-----|----------|
| `clients` | UUID | Заказчики |
| `products` | UUID | Продукция |
| `materials` | UUID | Материалы |
| `operations` | UUID | Операции |
| `product_prices` | UUID | Цены продукции |
| `material_prices` | UUID | Цены материалов |
| `operation_prices` | UUID | Цены операций |
| `specification_materials` | UUID | Спецификации материалов |
| `specification_operations` | UUID | Спецификации операций |
| `production_orders` | UUID | Заказы на производство |
| `production_order_items` | UUID | Позиции заказов |
| `sales_orders` | UUID | Заказы покупателей |
| `sales_order_items` | UUID | Позиции заказов |
| `users` | SERIAL | Пользователи |
| `notes` | SERIAL | Заметки |

## Ограничения

- **CHECK**: client_type, status, role, positive prices/quantities
- **FK CASCADE**: Цены, спецификации удаляются с родителя
- **FK RESTRICT**: Продукция не удаляется из заказов
- **UNIQUE**: code, order_number, login

## Индексы

14 индексов для оптимизации запросов по product_id, material_id, order_date, client_id и т.д.

## Тестовые данные

Вставка справочных данных: 1 продукт, 5 материалов, 3 операции, цены, спецификации, 3 пользователя, 5 заметок.
