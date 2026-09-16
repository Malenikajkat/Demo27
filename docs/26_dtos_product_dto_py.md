# Документация: app/dtos/product_dto.py

## Назначение

Содержит **Dataclass ProductDTO** для сериализации данных продукции.

## Класс `ProductDTO`

### Поля

| Поле | Тип | По умолчанию | Описание |
|------|-----|-------------|----------|
| `product_id` | `str` | — | UUID продукции |
| `name` | `str` | — | Наименование |
| `code` | `str` | — | Уникальный код |
| `created_at` | `Optional[str]` | `None` | Дата создания (ISO) |

### Методы

#### `from_model(cls, product) -> ProductDTO`

Создаёт DTO из модели `Product`.

#### `to_dict(self) -> dict`

Конвертирует в словарь.

## Зависимости и связи

| Элемент | Тип связи | Описание |
|---------|-----------|----------|
| `app/models.py` | Использует | Модель `Product` |
| `app/services/product_service.py` | Использует | DTO-методы |
