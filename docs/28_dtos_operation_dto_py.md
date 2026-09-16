# Документация: app/dtos/operation_dto.py

## Назначение

Содержит **Dataclass OperationDTO** для сериализации данных технологических операций.

## Класс `OperationDTO`

### Поля

| Поле | Тип | По умолчанию | Описание |
|------|-----|-------------|----------|
| `operation_id` | `str` | — | UUID операции |
| `name` | `str` | — | Наименование |
| `code` | `str` | — | Уникальный код |
| `created_at` | `Optional[str]` | `None` | Дата создания (ISO) |

### Методы

#### `from_model(cls, operation) -> OperationDTO`

Создаёт DTO из модели `Operation`.

#### `to_dict(self) -> dict`

Конвертирует в словарь.

## Зависимости и связи

| Элемент | Тип связи | Описание |
|---------|-----------|----------|
| `app/models.py` | Использует | Модель `Operation` |
| `app/services/operation_service.py` | Использует | DTO-методы |
