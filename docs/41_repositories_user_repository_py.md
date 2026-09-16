# Документация: app/repositories/user_repository.py

## Назначение

Репозиторий для работы с таблицей `users`. Наследует `BaseRepository` и добавляет специфичные методы для аутентификации.

## Класс `UserRepository`

### Инициализация

```python
class UserRepository(BaseRepository):
    def __init__(self):
        super().__init__(User)
```

**Модель**: `User`

### Наследуемые методы

`get_all()`, `get_by_id()`, `create()`, `update()`, `delete()`

### Специальные методы

#### `find_by_login(self, login: str)`

Находит пользователя по логину.

**Параметры**:
| Параметр | Тип | Описание |
|----------|-----|----------|
| `login` | `str` | Логин пользователя |

**SQL**: `SELECT * FROM users WHERE login = login`

**Возвращает**: Объект `User` или `None`

**Пример**:
```python
repo = UserRepository()
user = repo.find_by_login("admin")
```

#### `increment_failed_attempts(self, user_id: int)`

Увеличивает счётчик неудачных попыток входа.

**Параметры**:
| Параметр | Тип | Описание |
|----------|-----|----------|
| `user_id` | `int` | ID пользователя |

**Логика**:
1. Получает пользователя по ID
2. Увеличивает `failed_attempts` на 1
3. При 3+ попытках устанавливает `is_blocked = True`
4. Коммитит изменения

## Зависимости и связи

| Элемент | Тип связи | Описание |
|---------|-----------|----------|
| `base_repository.py` | Наследует | CRUD-методы |
| `app/models.py` | Использует | Модель `User` |
| `app/services/user_service.py` | Использует | Сервисный слой |
| `app/services/auth_service.py` | Использует | Метод `find_by_login()` |

## Важные замечания

1. **find_by_login**: Альтернатива `get_by_id()` — поиск по логину, а не по ID.
2. **Блокировка**: `increment_failed_attempts()` реализует логику блокировки аккаунта.
3. **Коммит внутри**: Метод сразу коммитит изменения.
