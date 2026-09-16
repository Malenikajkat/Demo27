# Документация: app/views/material_view.py

## Назначение

Class-Based API для управления материалами: полный CRUD.

## Классы

### `MaterialListAPI(BaseAPIView)` — GET/POST /api/materials/
### `MaterialDetailAPI(BaseAPIView)` — GET/PUT/DELETE /api/materials/<id>

## Зависимости и связи

| Элемент | Тип связи |
|---------|-----------|
| `BaseAPIView` | Наследует |
| `MaterialService` | Использует |
