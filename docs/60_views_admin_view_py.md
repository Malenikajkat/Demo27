# Документация: app/views/admin_view.py

## Назначение

Class-Based API для админ-панели: CRUD пользователей с проверкой роли "Администратор".

## Классы

### `AdminUserListAPI(BaseAPIView)`
| Метод | Маршрут | Описание |
|-------|---------|----------|
| `get()` | GET /api/admin/users/ | Список пользователей |

### `AdminUserCreateAPI(BaseAPIView)`
| Метод | Маршрут | Описание |
|-------|---------|----------|
| `post()` | POST /api/admin/users/ | Создание пользователя |

### `AdminUserDetailAPI(BaseAPIView)`
| Метод | Маршрут | Описание |
|-------|---------|----------|
| `put(user_id)` | PUT /api/admin/users/<id> | Обновление |
| `delete(user_id)` | DELETE /api/admin/users/<id> | Удаление |

## Защита

- `decorators = [login_required]` — авторизация
- `_require_admin()` — проверка роли

## Зависимости и связи

| Элемент | Тип связи |
|---------|-----------|
| `BaseAPIView` | Наследует |
| `UserService` | Использует |
| `flask_login` | `@login_required`, `current_user` |

## Важные замечания

1. **Защита ролей**: Все методы проверяют роль "Администратор".
2. **Нельзя удалить себя**: Защита в `delete()`.
3. **Сброс failed_attempts**: При разблокировке.
