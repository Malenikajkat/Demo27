# Документация: app/dtos/user_dto.py

## Назначение

Содержит **Dataclass UserDTO** для сериализации данных пользователя.

## Класс `UserDTO`

### Поля

| Поле | Тип | По умолчанию | Описание |
|------|-----|-------------|----------|
| `user_id` | `int` | — | Целочисленный ID |
| `login` | `str` | — | Логин |
| `role` | `str` | — | Роль |
| `is_blocked` | `bool` | `False` | Заблокирован |
| `failed_attempts` | `int` | `0` | Попыток входа |
| `created_at` | `Optional[str]` | `None` | Дата создания (ISO) |

### Методы

#### `from_model(cls, user) -> UserDTO`

Создаёт DTO из модели `User`.

#### `to_dict(self) -> dict`

Конвертирует в словарь.

### Пример

```python
dto = UserDTO.from_model(user_obj)
# dto.user_id = 1
# dto.login = "admin"
# dto.role = "Администратор"
```

## Зависимости и связи

| Элемент | Тип связи | Описание |
|---------|-----------|----------|
| `app/models.py` | Использует | Модель `User` |
| `app/services/user_service.py` | Использует | DTO-методы |
