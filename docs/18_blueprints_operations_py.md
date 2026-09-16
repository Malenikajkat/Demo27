# Документация: app/blueprints/operations.py

## Назначение

Файл `app/blueprints/operations.py` реализует **API для управления технологическими операциями**. Структура идентична `products.py` и `materials.py`.

## Blueprint

```python
operations_bp = Blueprint("operations", __name__)
```

Регистрируется с префиксом `/api/operations`.

## Маршруты (Endpoints)

### 1. `GET /api/operations/` — Список операций

**Функция**: `list_operations()`

**Ответ 200**:
```json
{
    "operations": [
        {
            "operation_id": "550e8400-e29b-41d4-a716-446655440000",
            "name": "Токарная обработка",
            "code": "OP-TURN-001",
            "created_at": "2025-01-15T10:30:00"
        }
    ]
}
```

### 2. `POST /api/operations/` — Создание операции

**Функция**: `create_operation()`

**Тело запроса**:
```json
{
    "name": "Фрезерная обработка",
    "code": "OP-MILL-002"
}
```

**Обязательные поля**: `name`, `code`

**Ответ 201**:
```json
{
    "message": "Операция создана",
    "operation_id": "550e8400-e29b-41d4-a716-446655440001"
}
```

## Ключевая логика

Идентична `products.py` и `materials.py`:
- Только GET (список) и POST (создание)
- Нет авторизации
- UNIQUE code на уровне БД

## Зависимости и связи

| Элемент | Тип связи | Описание |
|---------|-----------|----------|
| `app/models.py` | Использует | Модель `Operation` |
| `app/extensions.py` | Использует | `db.session` |
| `web/operations.html` | Использует | Фронтенд |
