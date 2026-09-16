# Документация: app/dtos/material_dto.py

## Назначение

Содержит **Dataclass MaterialDTO** для сериализации данных материалов.

## Класс `MaterialDTO`

### Поля

| Поле | Тип | По умолчанию | Описание |
|------|-----|-------------|----------|
| `material_id` | `str` | — | UUID материала |
| `name` | `str` | — | Наименование |
| `code` | `str` | — | Уникальный код |
| `created_at` | `Optional[str]` | `None` | Дата создания (ISO) |

### Методы

#### `from_model(cls, material) -> MaterialDTO`

Создаёт DTO из модели `Material`.

#### `to_dict(self) -> dict`

Конвертирует в словарь.

## Зависимости и связи

| Элемент | Тип связи | Описание |
|---------|-----------|----------|
| `app/models.py` | Использует | Модель `Material` |
| `app/services/material_service.py` | Использует | DTO-методы |
