# Документация: app/blueprints/clients.py

## Назначение

Файл `app/blueprints/clients.py` реализует **полный CRUD API для управления клиентами** (заказчиками). Предоставляет эндпоинты для создания, чтения, обновления и удаления клиентов.

## Blueprint

```python
clients_bp = Blueprint("clients", __name__)
```

Регистрируется с префиксом `/api/clients`:
```python
app.register_blueprint(clients_bp, url_prefix="/api/clients")
```

## Маршруты (Endpoints)

### 1. `GET /api/clients/` — Список клиентов

**Функция**: `list_clients()`

**Ответ 200**:
```json
{
    "clients": [
        {
            "client_id": "550e8400-e29b-41d4-a716-446655440000",
            "name": "ООО Поставка",
            "inn": "1234567890",
            "address": "г. Москва",
            "phone": "+7(495)123-45-67",
            "client_type": "Поставщик",
            "created_at": "2025-01-15T10:30:00"
        }
    ]
}
```

**Логика**:
1. Загружает всех клиентов из БД
2. Конвертирует UUID в строки
3. Форматирует дату в ISO-формат

### 2. `POST /api/clients/` — Создание клиента

**Функция**: `create_client()`

**Тело запроса**:
```json
{
    "name": "ООО Ромашка",
    "inn": "0987654321",
    "address": "г. Санкт-Петербург",
    "phone": "+7(812)987-65-43",
    "client_type": "Покупатель"
}
```

**Обязательные поля**: `name`, `client_type`

**Ответ 201**:
```json
{
    "message": "Клиент создан",
    "client_id": "550e8400-e29b-41d4-a716-446655440001"
}
```

**Ответ 400**:
```json
{
    "error": "Bad Request",
    "message": "Необходимо указать name и client_type"
}
```

### 3. `GET /api/clients/<client_id>` — Получение клиента

**Функция**: `get_client(client_id)`

**Параметры**: `client_id` — UUID в строковом формате

**Ответ 200**:
```json
{
    "client_id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "ООО Поставка",
    "inn": "1234567890",
    "address": "г. Москва",
    "phone": "+7(495)123-45-67",
    "client_type": "Поставщик",
    "created_at": "2025-01-15T10:30:00"
}
```

**Ответ 400** (неверный UUID):
```json
{
    "error": "Bad Request",
    "message": "Неверный формат UUID"
}
```

**Ответ 404**:
```json
{
    "error": "Not Found",
    "message": "Клиент не найден"
}
```

### 4. `PUT /api/clients/<client_id>` — Обновление клиента

**Функция**: `update_client(client_id)`

**Тело запроса** (все поля опциональны):
```json
{
    "name": "ООО Ромашка (обновлён)",
    "phone": "+7(495)111-22-33"
}
```

**Логика**: Обновляет только переданные поля, остальные остаются без изменений.

**Ответ 200**:
```json
{
    "message": "Клиент обновлён"
}
```

### 5. `DELETE /api/clients/<client_id>` — Удаление клиента

**Функция**: `delete_client(client_id)`

**Ответ 200**:
```json
{
    "message": "Клиент удалён"
}
```

**Ответ 404**:
```json
{
    "error": "Not Found",
    "message": "Клиент не найден"
}
```

## Валидация UUID

Все эндпоинты, принимающие `client_id`, валидируют UUID:
```python
try:
    client_uuid = uuid.UUID(client_id)
except (ValueError, AttributeError):
    return jsonify({"error": "Bad Request", "message": "Неверный формат UUID"}), 400
```

## Примеры curl

### Создание клиента
```bash
curl -X POST http://localhost:5000/api/clients/ \
  -H "Content-Type: application/json" \
  -d '{"name":"ООО Тест","client_type":"Покупатель","inn":"1111111111"}'
```

### Получение клиента
```bash
curl http://localhost:5000/api/clients/550e8400-e29b-41d4-a716-446655440000
```

### Обновление клиента
```bash
curl -X PUT http://localhost:5000/api/clients/550e8400-e29b-41d4-a716-446655440000 \
  -H "Content-Type: application/json" \
  -d '{"name":"ООО Обновлённый"}'
```

### Удаление клиента
```bash
curl -X DELETE http://localhost:5000/api/clients/550e8400-e29b-41d4-a716-446655440000
```

## Ключевая логика

### Полный CRUD
В отличие от других CRUD-blueprint'ов (products, materials, operations), clients.py предоставляет **полный набор операций**: GET, POST, GET by ID, PUT, DELETE.

### Типы клиентов
| Значение | Описание |
|----------|----------|
| "Поставщик" | Поставщик материалов |
| "Покупатель" | Покупатель продукции |

### Отсутствие авторизации
Blueprint не использует `@login_required` — эндпоинты доступны без авторизации.

## Зависимости и связи

| Элемент | Тип связи | Описание |
|---------|-----------|----------|
| `app/models.py` | Использует | Модель `Client` |
| `app/extensions.py` | Использует | `db.session` |
| `web/clients.html` | Использует | Фронтенд для CRUD |
| `app/services/client_service.py` | Аналог | Сервисный слой с DTO |
| `app/dtos/client_dto.py` | Аналог | DTO-сериализация |
| `app/views/client_view.py` | Аналог | Class-Based View |

## Важные замечания

1. **Без авторизации**: Нет `@login_required` — любой может управлять клиентами.
2. **Полный CRUD**: Все 5 операций (vs 2 у products/materials/operations).
3. **UUID валидация**: Строгая проверка формата UUID.
4. **Частичное обновление**: PUT обновляет только переданные поля.
5. **Нет каскадного удаления**: Если клиент связан с заказами, удаление может вызвать ошибку FK.
