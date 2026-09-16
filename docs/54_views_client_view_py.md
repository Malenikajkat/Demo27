# Документация: app/views/client_view.py

## Назначение

Class-Based API для управления клиентами: полный CRUD.

## Классы

### `ClientListAPI(BaseAPIView)`

| Метод | Маршрут | Описание |
|-------|---------|----------|
| `get()` | GET /api/clients/ | Список клиентов |
| `post()` | POST /api/clients/ | Создание клиента |

### `ClientDetailAPI(BaseAPIView)`

| Метод | Маршрут | Описание |
|-------|---------|----------|
| `get(client_id)` | GET /api/clients/<id> | Получение клиента |
| `put(client_id)` | PUT /api/clients/<id> | Обновление клиента |
| `delete(client_id)` | DELETE /api/clients/<id> | Удаление клиента |

## Регистрация маршрутов

```python
clients_bp.add_url_rule("/", view_func=ClientListAPI.as_view("clients_list"))
clients_bp.add_url_rule("/<client_id>", view_func=ClientDetailAPI.as_view("client_detail"))
```

## Зависимости и связи

| Элемент | Тип связи |
|---------|-----------|
| `BaseAPIView` | Наследует |
| `ClientService` | Использует |
