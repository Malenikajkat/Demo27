# Документация: app/views/operation_view.py

## Назначение

Class-Based API для управления операциями: полный CRUD.

## Классы

### `OperationListAPI(BaseAPIView)` — GET/POST /api/operations/
### `OperationDetailAPI(BaseAPIView)` — GET/PUT/DELETE /api/operations/<id>

## Зависимости и связи

| Элемент | Тип связи |
|---------|-----------|
| `BaseAPIView` | Наследует |
| `OperationService` | Использует |
