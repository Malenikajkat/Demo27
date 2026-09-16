# Документация: app/dtos/specification_dto.py

## Назначение

Содержит **Dataclass SpecificationMaterialDTO** и **SpecificationOperationDTO** для сериализации спецификаций.

## Класс `SpecificationMaterialDTO`

### Поля

| Поле | Тип | По умолчанию | Описание |
|------|-----|-------------|----------|
| `spec_mat_id` | `str` | — | UUID спецификации |
| `product_id` | `str` | — | UUID продукта |
| `material_id` | `str` | — | UUID материала |
| `quantity_per_unit` | `float` | — | Норма расхода |

### Методы

#### `from_model(cls, spec) -> SpecificationMaterialDTO`

Создаёт DTO из модели `SpecificationMaterial`.

#### `to_dict(self) -> dict`

Конвертирует в словарь.

## Класс `SpecificationOperationDTO`

### Поля

| Поле | Тип | По умолчанию | Описание |
|------|-----|-------------|----------|
| `spec_op_id` | `str` | — | UUID спецификации |
| `product_id` | `str` | — | UUID продукта |
| `operation_id` | `str` | — | UUID операции |
| `time_norm` | `float` | — | Нормо-часы |
| `op_quantity` | `float` | — | Количество операций |

### Методы

#### `from_model(cls, spec) -> SpecificationOperationDTO`

Создаёт DTO из модели `SpecificationOperation`.

#### `to_dict(self) -> dict`

Конвертирует в словарь.

## Зависимости и связи

| Элемент | Тип связи | Описание |
|---------|-----------|----------|
| `app/models.py` | Использует | `SpecificationMaterial`, `SpecificationOperation` |
| `app/services/specification_service.py` | Использует | DTO-методы |
