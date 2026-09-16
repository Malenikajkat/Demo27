# Документация: app/services/user_service.py

## Назначение

Сервис для работы с пользователями: CRUD + DTO + хеширование паролей.

## Класс `UserService(BaseService)`

### Методы

| Метод | Описание |
|-------|----------|
| `get_all_dto()` | Список пользователей в DTO |
| `create_user(login, password, role)` | Создание с хешированием |
| `update_user(user_id, role, is_blocked)` | Обновление |

### `create_user(self, login, password, role="Пользователь")`

**Логика**:
1. Хеширует пароль через `hash_password()`
2. Создаёт запись в БД

## Зависимости и связи

| Элемент | Тип связи |
|---------|-----------|
| `BaseService` | Наследует |
| `UserRepository` | Использует |
| `UserDTO` | Использует |
| `app/auth.py` | Использует `hash_password()` |
