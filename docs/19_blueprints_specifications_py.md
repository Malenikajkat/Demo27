# Документация: app/blueprints/specifications.py

## Назначение

Файл `app/blueprints/specifications.py` реализует **API для управления спецификациями** — нормами расхода материалов и технологическими операциями для продукции.

## Blueprint

```python
specifications_bp = Blueprint("specifications", __name__)
```

Регистрируется с префиксом `/api/specifications`.

## Маршруты (Endpoints)

### 1. `GET /api/specifications/materials/` — Список спецификаций материалов

**Функция**: `list_spec_materials()`

**Ответ 200**:
```json
{
    "specifications": [
        {
            "spec_mat_id": "550e8400-e29b-41d4-a716-446655440000",
            "product_id": "...",
            "material_id": "...",
            "quantity_per_unit": 2.5
        }
    ]
}
```

### 2. `POST /api/specifications/materials/` — Создание спецификации материала

**Функция**: `create_spec_material()`

**Тело запроса**:
```json
{
    "product_id": "uuid-продукта",
    "material_id": "uuid-материала",
    "quantity_per_unit": 2.5
}
```

**Обязательные поля**: `product_id`, `material_id`, `quantity_per_unit`

**Ответ 201**:
```json
{
    "message": "Спецификация создана",
    "spec_mat_id": "550e8400-e29b-41d4-a716-446655440001"
}
```

### 3. `GET /api/specifications/operations/` — Список спецификаций операций

**Функция**: `list_spec_operations()`

**Ответ 200**:
```json
{
    "specifications": [
        {
            "spec_op_id": "550e8400-e29b-41d4-a716-446655440000",
            "product_id": "...",
            "operation_id": "...",
            "time_norm": 1.5,
            "op_quantity": 2.0
        }
    ]
}
```

### 4. `POST /api/specifications/operations/` — Создание спецификации операции

**Функция**: `create_spec_operation()`

**Тело запроса**:
```json
{
    "product_id": "uuid-продукта",
    "operation_id": "uuid-операции",
    "time_norm": 1.5,
    "op_quantity": 2.0
}
```

**Обязательные поля**: `product_id`, `operation_id`

**Опциональные поля**: `time_norm` (по умолчанию 1.0), `op_quantity` (по умолчанию 1.0)

## Ключевая логика

### Два типа спецификаций
| Тип | Назначение | Поля |
|-----|------------|------|
| Materials | Норма расхода материалов на 1 единицу | product_id, material_id, quantity_per_unit |
| Operations | Технологические операции для продукции | product_id, operation_id, time_norm, op_quantity |

### Отсутствие полного CRUD
Только GET (список) и POST (создание). Нет обновления и удаления.

## Зависимости и связи

| Элемент | Тип связи | Описание |
|---------|-----------|----------|
| `app/models.py` | Использует | `SpecificationMaterial`, `SpecificationOperation` |
| `app/extensions.py` | Использует | `db.session` |
| `web/specifications.html` | Использует | Фронтенд с двумя таблицами |
| `app/services/specification_service.py` | Аналог | Сервисный слой |

## Важные замечания

1. **Два подмаршрута**: `/materials/` и `/operations/` — разные типы спецификаций.
2. **Нет валидации FK**: UUID передаются как строки без проверки существования сущностей.
3. **Дефолтные значения**: time_norm и op_quantity по умолчанию 1.0.
