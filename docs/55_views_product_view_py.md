# Документация: app/views/product_view.py

## Назначение

Class-Based API для управления продукцией: полный CRUD.

## Классы

### `ProductListAPI(BaseAPIView)` — GET/POST /api/products/
### `ProductDetailAPI(BaseAPIView)` — GET/PUT/DELETE /api/products/<id>

## Зависимости и связи

| Элемент | Тип связи |
|---------|-----------|
| `BaseAPIView` | Наследует |
| `ProductService` | Использует |
