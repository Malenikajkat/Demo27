# Документация: app/services/client_service.py

## Назначение

Сервис для работы с клиентами: CRUD + DTO-преобразование.

## Класс `ClientService(BaseService)`

### Инициализация

```python
def __init__(self):
    super().__init__(ClientRepository())
```

### Методы

| Метод | Описание |
|-------|----------|
| `get_all_dto(skip, limit)` | Список клиентов в формате DTO |
| `get_by_id_dto(client_id)` | Клиент по ID в формате DTO |
| `create_client(name, client_type, ...)` | Создание клиента |
| `update_client(client_id, ...)` | Обновление клиента |

## Зависимости и связи

| Элемент | Тип связи |
|---------|-----------|
| `BaseService` | Наследует |
| `ClientRepository` | Использует |
| `ClientDTO` | Использует |
