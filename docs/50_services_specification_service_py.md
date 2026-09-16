# Документация: app/services/specification_service.py

## Назначение

Сервисы для работы со спецификациями: простой `get_all()` без наследования от BaseService.

## Классы

### `SpecificationMaterialService`

```python
def get_all(self):
    return db.session.execute(db.select(SpecificationMaterial)).scalars().all()
```

### `SpecificationOperationService`

```python
def get_all(self):
    return db.session.execute(db.select(SpecificationOperation)).scalars().all()
```

## Зависимости и связи

| Элемент | Тип связи |
|---------|-----------|
| `db` | Использует напрямую |
| `SpecificationMaterial` | Запрашивает |
| `SpecificationOperation` | Запрашивает |

## Важные замечания

1. **Без BaseService**: Не наследуют базовый класс.
2. **Только get_all()**: Нет CRUD-методов.
3. **Прямой доступ к БД**: Не используют репозитории.
