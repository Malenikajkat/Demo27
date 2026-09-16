# Документация: app/dtos/client_dto.py

## Назначение

Файл `app/dtos/client_dto.py` содержит **Dataclass ClientDTO** для сериализации данных клиента в словарь/JSON.

## Класс `ClientDTO`

### Поля

| Поле | Тип | По умолчанию | Описание |
|------|-----|-------------|----------|
| `client_id` | `str` | — | UUID клиента |
| `name` | `str` | — | Наименование |
| `inn` | `Optional[str]` | `None` | ИНН |
| `address` | `Optional[str]` | `None` | Адрес |
| `phone` | `Optional[str]` | `None` | Телефон |
| `client_type` | `str` | `""` | Тип: "Поставщик"/"Покупатель" |
| `created_at` | `Optional[str]` | `None` | Дата создания (ISO) |

### Методы

#### `from_model(cls, client) -> ClientDTO`

Создаёт DTO из SQLAlchemy-модели.

**Параметры**:
| Параметр | Тип | Описание |
|----------|-----|----------|
| `client` | `Client` | Объект модели |

**Пример**:
```python
dto = ClientDTO.from_model(client_obj)
# dto.client_id = "550e8400-..."
# dto.name = "ООО Поставка"
```

#### `to_dict(self) -> dict`

Конвертирует DTO в словарь через `dataclasses.asdict()`.

**Пример**:
```python
dto = ClientDTO.from_model(client_obj)
data = dto.to_dict()
# {"client_id": "...", "name": "...", ...}
```

## Зависимости и связи

| Элемент | Тип связи | Описание |
|---------|-----------|----------|
| `app/models.py` | Использует | Модель `Client` |
| `app/services/client_service.py` | Использует | `get_all_dto()`, `get_by_id_dto()` |
| `dataclasses` | Стандартная библиотека | `@dataclass`, `asdict` |

## Важные замечания

1. **UUID → str**: `client_id` конвертируется из UUID в строку.
2. **ISO дата**: `created_at` форматируется в ISO-строку.
3. **Optional поля**: `inn`, `address`, `phone` могут быть None.
