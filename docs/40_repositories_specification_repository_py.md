# Документация: app/repositories/specification_repository.py

## Назначение

Содержит два репозитория для работы со спецификациями.

## Классы

### `SpecificationMaterialRepository`

```python
class SpecificationMaterialRepository(BaseRepository):
    def __init__(self):
        super().__init__(SpecificationMaterial)
```

**Модель**: `SpecificationMaterial`

### `SpecificationOperationRepository`

```python
class SpecificationOperationRepository(BaseRepository):
    def __init__(self):
        super().__init__(SpecificationOperation)
```

**Модель**: `SpecificationOperation`

## Зависимости и связи

| Элемент | Тип связи | Описание |
|---------|-----------|----------|
| `base_repository.py` | Наследуют | CRUD-методы |
| `app/models.py` | Используют | `SpecificationMaterial`, `SpecificationOperation` |
| `app/services/specification_service.py` | Используют | Сервисный слой |
