# Документация: generate_er_diagram.py

## Назначение

Файл `generate_er_diagram.py` содержит скрипт для **автоматической генерации ER-диаграммы** (Entity-Relationship Diagram) базы данных проекта Demo27. Использует библиотеку Graphviz для создания визуальной схемы всех 13 таблиц базы данных с полями, первичными ключами, внешними ключами и связями между таблицами. Результат сохраняется в PDF-файл.

## Зависимости

```python
from graphviz import Digraph
```
Требует установленной библиотеки `graphviz` (Python-пакет) и системы Graphviz.

## Структура

### Функция `create_er_diagram()`

Основная функция, выполняющая всю работу по генерации диаграммы.

#### 1. Инициализация графа
```python
dot = Digraph('ER Diagram', format='pdf')
dot.attr(rankdir='LR', size='20,30', dpi='150')
```
- **format='pdf'** — экспорт в PDF
- **rankdir='LR'** — направление слева направо (Left-to-Right)
- **size='20,30'** — размер холста
- **dpi='150'** — разрешение рендеринга

#### 2. Цветовая палитра
Каждому типу таблиц присвоен свой цвет для визуальной дифференциации:

| Цвет | Код | Тип таблиц |
|------|-----|------------|
| Голубой | `#E3F2FD` | Клиенты (`clients`) |
| Зелёный | `#E8F5E9` | Продукция (`products`) |
| Оранжевый | `#FFF3E0` | Материалы (`materials`) |
| Фиолетовый | `#F3E5F5` | Операции (`operations`) |
| Красный | `#FFEBEE` | Заказы (`production_orders`, `sales_orders`) |
| Бирюзовый | `#E0F7FA` | Спецификации (`specification_*`) |
| Розовый | `#FCE4EC` | Цены (`product_prices`, `material_prices`, `operation_prices`) |
| Жёлтый | `#FFF9C4` | Пользователи (`users`) |
| Лавандовый | `#E1BEE7` | Заметки (`notes`) |

#### 3. Вспомогательная функция `table_node()`
Создаёт HTML-таблицу для каждой узла диаграммы:
- Заголовок с названием таблицы (жирный, цветной фон)
- Поля первичного ключа (PK) с иконкой 🔑
- Обычные поля с отступом

#### 4. Определение таблиц (13 штук)

##### Основные сущности
| Таблица | PK | Основные поля |
|---------|-----|---------------|
| `clients` | client_id (UUID) | name, inn, address, phone, client_type |
| `products` | product_id (UUID) | name, code (UNIQUE) |
| `materials` | material_id (UUID) | name, code (UNIQUE) |
| `operations` | operation_id (UUID) | name, code (UNIQUE) |

##### Таблицы цен
| Таблица | PK | Основные поля |
|---------|-----|---------------|
| `product_prices` | product_price_id (UUID) | product_id (FK), price, effective_date |
| `material_prices` | material_price_id (UUID) | material_id (FK), price, effective_date |
| `operation_prices` | operation_price_id (UUID) | operation_id (FK), price, effective_date |

##### Спецификации
| Таблица | PK | Основные поля |
|---------|-----|---------------|
| `specification_materials` | spec_mat_id (UUID) | product_id (FK), material_id (FK), quantity_per_unit |
| `specification_operations` | spec_op_id (UUID) | product_id (FK), operation_id (FK), time_norm, op_quantity |

##### Заказы
| Таблица | PK | Основные поля |
|---------|-----|---------------|
| `production_orders` | order_id (UUID) | order_number, order_date, subdivision, status |
| `production_order_items` | order_item_id (UUID) | production_order_id (FK), product_id (FK), quantity |
| `sales_orders` | sales_order_id (UUID) | order_number, order_date, client_id (FK), executor_id (FK), total_amount |
| `sales_order_items` | sales_order_item_id (UUID) | sales_order_id (FK), product_id (FK), quantity, unit_price, discount |

##### Пользователи и заметки
| Таблица | PK | Основные поля |
|---------|-----|---------------|
| `users` | user_id (SERIAL) | login, password_hash, role, is_blocked, failed_attempts, blocked_until, created_at |
| `notes` | note_id (SERIAL) | title, content, id_user (FK), created_at |

#### 5. Определение связей (relationships)
Связи рисуются с подписями и цветовой кодировкой:

| Связь | Цвет | Подпись |
|-------|------|---------|
| clients → sales_orders | синий | покупатель 1..M |
| clients → sales_orders | зелёный (пунктир) | исполнитель 1..M |
| products/materials/operations → *_prices | фиолетовый | имеет цену 1..M |
| products + materials → specification_materials | оранжевый | содержит / включён 1..M |
| products + operations → specification_operations | darkviolet | требует / в спецификации 1..M |
| production_orders → production_order_items | красный | содержит 1..M |
| sales_orders → sales_order_items | darkred | содержит 1..M |
| users → notes | фиолетовый | содержит заметки 1..M |

#### 6. Рендеринг
```python
dot.render('er_diagram', cleanup=True)
```
- Генерирует PDF-файл `er_diagram.pdf`
- `cleanup=True` — удаляет промежуточные файлы (.gv)

## Ключевая логика

- **HTML-метки**: Каждая таблица рисуется как HTML-таблица внутри Graphviz, что обеспечивает читаемое форматирование полей
- **Цветовое кодирование**: Позволяет визуально группировать связанные таблицы
- **Автогенерация**: Не требует ручного создания диаграммы — достаточно запустить скрипт
- **Оригинальный порядок**: `correct_order: [0, 1, 2, 3]` — порядок фрагментов в исходном изображении

## Использование

### Запуск
```bash
python generate_er_diagram.py
```

### Результат
Создаётся файл `er_diagram.pdf` в текущей директории.

## Зависимости и связи

| Элемент | Тип связи | Описание |
|---------|-----------|----------|
| `app/models.py` | Источник данных | Описывает те же 13 таблиц |
| `database/schema.sql` | Источник данных | SQL-определение тех же таблиц |
| `image/` | Данные | Изображения для капчи (описаны в PuzzleCaptcha) |
| `graphviz` (пакет) | Зависимость | Библиотека для рендеринга |

## Важные замечания

1. **Актуальность**: ER-диаграмма должна обновляться при изменении схемы БД.
2. **Graphviz**: Требуется установка системы Graphviz на компьютер, а не только Python-пакета.
3. **Режимы капчи**: Скрипт описывает оба режима `pieces` (4 фрагмента) и `grid` (3×3 сетка).
4. **Тестовое изображение**: Если изображения не найдены, генерируется тестовое изображение с геометрическими фигурами.
