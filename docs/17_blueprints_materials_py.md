# Документация: app/blueprints/materials.py

## Назначение

Файл `app/blueprints/materials.py` реализует **API для управления материалами**. Структура идентична `products.py` — предоставляет эндпоинты для получения списка и создания материалов.

## Blueprint

```python
materials_bp = Blueprint("materials", __name__)
```

Регистрируется с префиксом `/api/materials`.

## Маршруты (Endpoints)

### 1. `GET /api/materials/` — Список материалов

**Функция**: `list_materials()`

**Ответ 200**:
```json
{
    "materials": [
        {
            "material_id": "550e8400-e29b-41d4-a716-446655440000",
            "name": "Сталь 20",
            "code": "ST-020",
            "created_at": "2025-01-15T10:30:00"
        }
    ]
}
```

### 2. `POST /api/materials/` — Создание материала

**Функция**: `create_material()`

**Тело запроса**:
```json
{
    "name": "Медь М1",
    "code": "CU-M1"
}
```

**Обязательные поля**: `name`, `code`

**Ответ 201**:
```json
{
    "message": "Материал создан",
    "material_id": "550e8400-e29b-41d4-a716-446655440001"
}
```

## Ключевая логика

Идентична `products.py`:
- Только GET (список) и POST (создание)
- Нет авторизации
- UNIQUE code на уровне БД

## Зависимости и связи

| Элемент | Тип связи | Описание |
|---------|-----------|----------|
| `app/models.py` | Использует | Модель `Material` |
| `app/extensions.py` | Использует | `db.session` |
| `web/materials.html` | Использует | Фронтенд |
