# Документация: app/models.py

## Назначение

Файл `app/models.py` определяет **все модели базы данных** проекта Demo27 в виде SQLAlchemy-классов. Содержит 13 моделей, которые соответствуют 13 таблицам PostgreSQL. Каждая модель описывает структуру таблицы, типы полей, ограничения (constraints) и связи (relationships) с другими таблицами.

## Зависимости

```python
from sqlalchemy import Column, String, Integer, Boolean, Text, Date, DateTime, ForeignKey, Numeric, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.extensions import db
```

## Модели

### 1. Client — Заказчики

**Таблица**: `clients`

| Поле | Тип | Описание |
|------|-----|----------|
| `client_id` | UUID (PK) | Уникальный идентификатор |
| `name` | VARCHAR(255) | Наименование организации |
| `inn` | VARCHAR(20) | ИНН организации |
| `address` | VARCHAR(255) | Адрес |
| `phone` | VARCHAR(20) | Телефон |
| `client_type` | VARCHAR(20) | Тип: 'Поставщик' или 'Покупатель' |
| `created_at` | DateTime | Дата создания записи |

**Ограничения**:
- `chk_client_type`: client_type IN ('Поставщик', 'Покупатель')

**Связи**:
- `sales_orders_as_client` → SalesOrder (как покупатель)
- `sales_orders_as_executor` → SalesOrder (как исполнитель)

### 2. Product — Продукция

**Таблица**: `products`

| Поле | Тип | Описание |
|------|-----|----------|
| `product_id` | UUID (PK) | Уникальный идентификатор |
| `name` | VARCHAR(255) | Наименование продукции |
| `code` | VARCHAR(50) UNIQUE | Уникальный код продукции |
| `created_at` | DateTime | Дата создания |

**Связи**:
- `prices` → ProductPrice (каскадное удаление)
- `spec_materials` → SpecificationMaterial (каскадное удаление)
- `spec_operations` → SpecificationOperation (каскадное удаление)
- `prod_order_items` → ProductionOrderItem
- `sales_order_items` → SalesOrderItem

### 3. Material — Материалы

**Таблица**: `materials`

| Поле | Тип | Описание |
|------|-----|----------|
| `material_id` | UUID (PK) | Уникальный идентификатор |
| `name` | VARCHAR(255) | Наименование материала |
| `code` | VARCHAR(50) UNIQUE | Уникальный код материала |
| `created_at` | DateTime | Дата создания |

**Связи**:
- `prices` → MaterialPrice (каскадное удаление)
- `spec_materials` → SpecificationMaterial

### 4. Operation — Технологические операции

**Таблица**: `operations`

| Поле | Тип | Описание |
|------|-----|----------|
| `operation_id` | UUID (PK) | Уникальный идентификатор |
| `name` | VARCHAR(255) | Наименование операции |
| `code` | VARCHAR(50) UNIQUE | Уникальный код операции |
| `created_at` | DateTime | Дата создания |

**Связи**:
- `prices` → OperationPrice (каскадное удаление)
- `spec_operations` → SpecificationOperation

### 5. ProductPrice — Цены продукции

**Таблица**: `product_prices`

| Поле | Тип | Описание |
|------|-----|----------|
| `product_price_id` | UUID (PK) | Уникальный идентификатор |
| `product_id` | UUID (FK) | Ссылка на продукцию |
| `price` | DECIMAL(10,2) | Цена |
| `effective_date` | DATE | Дата начала действия цены |

**Ограничения**:
- `chk_product_price_positive`: price >= 0

**Внешний ключ**: `products.product_id` ON DELETE CASCADE

### 6. MaterialPrice — Цены материалов

**Таблица**: `material_prices`

| Поле | Тип | Описание |
|------|-----|----------|
| `material_price_id` | UUID (PK) | Уникальный идентификатор |
| `material_id` | UUID (FK) | Ссылка на материал |
| `price` | DECIMAL(10,2) | Цена |
| `effective_date` | DATE | Дата начала действия цены |

**Ограничения**:
- `chk_material_price_positive`: price >= 0

### 7. OperationPrice — Цены операций

**Таблица**: `operation_prices`

| Поле | Тип | Описание |
|------|-----|----------|
| `operation_price_id` | UUID (PK) | Уникальный идентификатор |
| `operation_id` | UUID (FK) | Ссылка на операцию |
| `price` | DECIMAL(10,2) | Цена |
| `effective_date` | DATE | Дата начала действия цены |

**Ограничения**:
- `chk_operation_price_positive`: price >= 0

### 8. SpecificationMaterial — Спецификация материалов

**Таблица**: `specification_materials`

| Поле | Тип | Описание |
|------|-----|----------|
| `spec_mat_id` | UUID (PK) | Уникальный идентификатор |
| `product_id` | UUID (FK) | Ссылка на продукцию |
| `material_id` | UUID (FK) | Ссылка на материал |
| `quantity_per_unit` | DECIMAL(10,4) | Норма расхода на 1 единицу |

**Ограничения**:
- `chk_spec_mat_qty_positive`: quantity_per_unit > 0

**Назначение**: Определяет, какие материалы и в каком количестве нужны для производства 1 единицы продукции.

### 9. SpecificationOperation — Спецификация операций

**Таблица**: `specification_operations`

| Поле | Тип | Описание |
|------|-----|----------|
| `spec_op_id` | UUID (PK) | Уникальный идентификатор |
| `product_id` | UUID (FK) | Ссылка на продукцию |
| `operation_id` | UUID (FK) | Ссылка на операцию |
| `time_norm` | DECIMAL(10,2) | Нормо-часы (по умолчанию 1.0) |
| `op_quantity` | DECIMAL(10,2) | Количество операций (по умолчанию 1.0) |

**Назначение**: Определяет технологические операции, необходимые для производства продукции.

### 10. ProductionOrder — Заказы на производство

**Таблица**: `production_orders`

| Поле | Тип | Описание |
|------|-----|----------|
| `order_id` | UUID (PK) | Уникальный идентификатор |
| `order_number` | VARCHAR(50) UNIQUE | Номер заказа |
| `order_date` | DATE | Дата заказа |
| `subdivision` | VARCHAR(100) | Подразделение |
| `status` | VARCHAR(20) | Статус заказа |
| `created_at` | DateTime | Дата создания |

**Ограничения**:
- `chk_prod_order_status`: status IN ('Новый', 'В работе', 'Завершён', 'Отменён')

**Связи**:
- `items` → ProductionOrderItem (каскадное удаление)

### 11. ProductionOrderItem — Позиции заказа на производство

**Таблица**: `production_order_items`

| Поле | Тип | Описание |
|------|-----|----------|
| `order_item_id` | UUID (PK) | Уникальный идентификатор |
| `production_order_id` | UUID (FK) | Ссылка на заказ |
| `product_id` | UUID (FK) | Ссылка на продукцию |
| `quantity` | DECIMAL(10,2) | Количество |

**Ограничения**:
- `chk_prod_order_qty_positive`: quantity > 0
- FK: `products.product_id` ON DELETE RESTRICT (нельзя удалить продукт, если он в заказе)

### 12. SalesOrder — Заказы покупателей

**Таблица**: `sales_orders`

| Поле | Тип | Описание |
|------|-----|----------|
| `sales_order_id` | UUID (PK) | Уникальный идентификатор |
| `order_number` | VARCHAR(50) UNIQUE | Номер заказа |
| `order_date` | DATE | Дата заказа |
| `client_id` | UUID (FK) | Покупатель |
| `executor_id` | UUID (FK) | Исполнитель (тоже Client) |
| `total_amount` | DECIMAL(12,2) | Общая сумма (по умолчанию 0.00) |
| `created_at` | DateTime | Дата создания |

**Ограничения**:
- `chk_sales_client_neq_executor`: client_id <> executor_id (покупатель ≠ исполнитель)

**Связи**:
- `client` → Client (как покупатель)
- `executor` → Client (как исполнитель)
- `items` → SalesOrderItem (каскадное удаление)

### 13. SalesOrderItem — Позиции заказа покупателя

**Таблица**: `sales_order_items`

| Поле | Тип | Описание |
|------|-----|----------|
| `sales_order_item_id` | UUID (PK) | Уникальный идентификатор |
| `sales_order_id` | UUID (FK) | Ссылка на заказ |
| `product_id` | UUID (FK) | Ссылка на продукцию |
| `quantity` | DECIMAL(10,2) | Количество |
| `unit_price` | DECIMAL(10,2) | Цена за единицу |
| `discount` | DECIMAL(10,2) | Скидка (по умолчанию 0.00) |

**Ограничения**:
- `chk_sales_qty_positive`: quantity > 0
- `chk_sales_price_positive`: unit_price >= 0
- `chk_sales_discount_positive`: discount >= 0

### 14. User — Пользователи системы

**Таблица**: `users`

| Поле | Тип | Описание |
|------|-----|----------|
| `user_id` | INTEGER (PK, SERIAL) | Автоинкрементный ID |
| `login` | VARCHAR(50) UNIQUE | Логин (уникальный) |
| `password_hash` | VARCHAR(255) | Хеш пароля |
| `role` | VARCHAR(20) | Роль: 'Администратор' или 'Пользователь' |
| `is_blocked` | BOOLEAN | Заблокирован ли |
| `failed_attempts` | INTEGER | Количество неудачных попыток |
| `blocked_until` | DateTime | До какого времени заблокирован |
| `created_at` | DateTime | Дата создания |

**Ограничения**:
- `chk_user_role`: role IN ('Администратор', 'Пользователь')

**Связи**:
- `notes` → Note

**Свойства Flask-Login**:
| Свойство | Значение | Описание |
|----------|----------|----------|
| `is_authenticated` | `True` | Пользователь всегда аутентифицирован |
| `is_active` | `not is_blocked` | Активен, если не заблокирован |
| `is_anonymous` | `False` | Не анонимный |
| `get_id()` | `str(user_id)` | Строковое представление ID |

### 15. Note — Заметки пользователей

**Таблица**: `notes`

| Поле | Тип | Описание |
|------|-----|----------|
| `note_id` | INTEGER (PK, SERIAL) | Автоинкрементный ID |
| `title` | VARCHAR(255) | Заголовок заметки |
| `content` | TEXT | Текст заметки |
| `id_user` | INTEGER (FK) | Ссылка на пользователя |
| `created_at` | DateTime | Да��а создания |

**Связи**:
- `user` → User

## Диаграмма связей

```
clients (1) ──────┐
                  ├──────► sales_orders (M)
clients (1) ──────┘

products (1) ────► product_prices (M)
products (1) ────► specification_materials (M)
materials (1) ───► specification_materials (M)
products (1) ────► specification_operations (M)
operations (1) ──► specification_operations (M)

production_orders (1) ───► production_order_items (M)
products (1) ────────────► production_order_items (M)

sales_orders (1) ────► sales_order_items (M)
products (1) ────────► sales_order_items (M)

users (1) ────► notes (M)
users (1) ────► sales_orders (как executor)
```

## Ключевые особенности

1. **UUID для основных сущностей**: Client, Product, Material, Operation, SalesOrder используют UUID как PK — это безопасно и не раскрывает информацию о количестве записей.
2. **SERIAL для User и Note**: user_id и note_id — обычные целые числа с автоинкрементом.
3. **Каскадное удаление**: При удалении продукта удаляются все связанные цены и спецификации.
4. **RESTRICT для заказов**: Нельзя удалить продукт, если он используется в заказах.
5. **CHECK-ограничения**: Данные на уровне БД (положительные цены, валидные статусы).
6. **Двойная роль Client**: Один и тот же клиент может быть и покупателем, и исполнителем.

## Зависимости и связи

| Элемент | Тип связи | Описание |
|---------|-----------|----------|
| `app/extensions.py` | Импорт | Использует `db` для определения моделей |
| `app/repositories/` | Используют | Все репозитории ссылаются на модели |
| `app/services/` | Используют | Сервисы работают с моделями через репозитории |
| `app/dtos/` | Конвертируют | DTO преобразуют модели в словари |
| `database/schema.sql` | Синхронность | SQL-схема соответствует моделям |

## Важные замечания

1. **func.now() / func.current_date()**: Значения по умолчанию задаются на уровне БД (server_default).
2. **cascade="all, delete-orphan"**: При удалении родителя удаляются все дети, и ребёнок не может существовать без родителя.
3. **foreign_keys в SalesOrder**: Два FK на одну таблицу clients — нужно явно указать `foreign_keys`.
4. **Только модели**: Бизнес-логика и валидация находятся в сервисах, а не в моделях.
