# Документация: app/services/operation_service.py

## Назначение

Сервис для работы с операциями: CRUD + DTO.

## Класс `OperationService(BaseService)`

### Методы

| Метод | Описание |
|-------|----------|
| `get_all_dto(skip, limit)` | Список операций в DTO |
| `get_by_id_dto(operation_id)` | Операция по ID в DTO |
| `create_operation(name, code)` | Создание операции |
| `update_operation(operation_id, ...)` | Обновление операции |

## Зависимости и связи

| Элемент | Тип связи |
|---------|-----------|
| `BaseService` | Наследует |
| `OperationRepository` | Использует |
| `OperationDTO` | Использует |
