# Документация: app/services/product_service.py

## Назначение

Сервис для работы с продукцией: CRUD + DTO.

## Класс `ProductService(BaseService)`

### Методы

| Метод | Описание |
|-------|----------|
| `get_all_dto(skip, limit)` | Список продукции в DTO |
| `get_by_id_dto(product_id)` | Продукция по ID в DTO |
| `create_product(name, code)` | Создание продукции |
| `update_product(product_id, ...)` | Обновление продукции |

## Зависимости и связи

| Элемент | Тип связи |
|---------|-----------|
| `BaseService` | Наследует |
| `ProductRepository` | Использует |
| `ProductDTO` | Использует |
