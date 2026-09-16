# Документация: app/services/material_service.py

## Назначение

Сервис для работы с материалами: CRUD + DTO.

## Класс `MaterialService(BaseService)`

### Методы

| Метод | Описание |
|-------|----------|
| `get_all_dto(skip, limit)` | Список материалов в DTO |
| `get_by_id_dto(material_id)` | Материал по ID в DTO |
| `create_material(name, code)` | Создание материала |
| `update_material(material_id, ...)` | Обновление материала |

## Зависимости и связи

| Элемент | Тип связи |
|---------|-----------|
| `BaseService` | Наследует |
| `MaterialRepository` | Использует |
| `MaterialDTO` | Использует |
