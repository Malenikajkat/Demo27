# Документация: app/config.py

## Назначение

Файл `app/config.py` управляет **конфигурацией приложения** Demo27. Определяет классы для разных сред (разработка, продакшн, тестирование), собирает параметры подключения к базе данных из переменных окружения и предоставляет функцию для получения конфигурации по имени окружения.

## Структура

### 1. Загрузка переменных окружения
```python
load_dotenv(Path(__file__).parent.parent / ".env")
```
- Загружает `.env` файл из корня проекта
- Делает переменные доступными через `os.getenv()`

### 2. Константа `BASE_DIR`
```python
BASE_DIR = Path(__file__).parent.parent
```
- Указывает на корень проекта (папка выше `app/`)
- Используется для построения путей к `.env` и другим файлам

### 3. Функция `_build_database_url()`
```python
def _build_database_url():
    url = os.getenv("DATABASE_URL")
    if url:
        return url
    # Сборка из отдельных переменных
```
**Логика работы**:
1. Сначала проверяет `DATABASE_URL` (полный URI)
2. Если не найден, собирает URI из отдельных переменных:
   - `DATABASE_HOST` (по умолчанию: `localhost`)
   - `DATABASE_PORT` (по умолчанию: `5432`)
   - `DATABASE_NAME` (по умолчанию: `production_db`)
   - `DATABASE_USER` (по умолчанию: `postgres`)
   - `DATABASE_PASSWORD` (по умолчанию: `12345`)
3. Формирует строку: `postgresql://user:password@host:port/database`

### 4. Класс `BaseConfig`
Базовая конфигурация, наследуемая всеми остальными:

| Параметр | Значение по умолчанию | Описание |
|----------|----------------------|----------|
| `SECRET_KEY` | `"production-is-system-secret-key-change-me"` | Ключ для подписи сессий и CSRF |
| `SQLALCHEMY_TRACK_MODIFICATIONS` | `False` | Отключает предупреждения о слежении за изменениями |
| `PERMANENT_SESSION_LIFETIME` | `3600` (сек) | Время жизни сессии (1 час) |
| `SQLALCHEMY_DATABASE_URI` | из `_build_database_url()` | Строка подключения к БД |
| `SQLALCHEMY_POOL_SIZE` | `10` | Размер пула соединений |
| `SQLALCHEMY_MAX_OVERFLOW` | `20` | Макс. соединений сверх пула |
| `SQLALCHEMY_POOL_TIMEOUT` | `30` (сек) | Таймаут ожидания соединения |
| `SQLALCHEMY_POOL_RECYCLE` | `3600` (сек) | Пересоздание соединения |
| `SQLALCHEMY_ECHO` | `False` | Логирование SQL-запросов |

### 5. Классы сред

#### `DevelopmentConfig(BaseConfig)`
```python
DEBUG = True
```
- Режим отладки с подробными ошибками
- Автоперезагрузка при изменении кода

#### `ProductionConfig(BaseConfig)`
```python
DEBUG = False
```
- Безопасная конфигурация для продакшена
- Отключён режим отладки

#### `TestingConfig(BaseConfig)`
```python
TESTING = True
SQLALCHEMY_DATABASE_URI = os.getenv("TEST_DATABASE_URL", "postgresql://...")
```
- Для запуска unit-тестов
- Может использовать отдельную тестовую БД

### 6. Словарь `config_by_name`
```python
config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}
```
Маппинг имён окружений на классы конфигурации.

### 7. Функция `get_config()`
```python
def get_config():
    env = os.getenv("FLASK_ENV", "development")
    return config_by_name.get(env, DevelopmentConfig)
```
- Получает имя окружения из `FLASK_ENV`
- Возвращает соответствующий класс конфигурации
- По умолчанию — `DevelopmentConfig`

## Ключевая логика

### Гибкая конфигурация БД
Поддерживает два подхода:
1. **Полный URI**: `DATABASE_URL=postgresql://user:pass@host:5432/dbname`
2. **Отдельные переменные**: `DATABASE_HOST`, `DATABASE_PORT`, `DATABASE_NAME` и т.д.

### Безопасность по умолчанию
- `SECRET_KEY` имеет предупреждение в значении по умолчанию — нужно изменить для продакшена
- `DEBUG = False` в продакшене
- Параметры пула настроены для стабильной работы

### Паттерн Strategy для конфигурации
Разные классы конфигурации позволяют легко переключаться между средами без изменения кода.

## Переменные окружения

| Переменная | По умолчанию | Описание |
|------------|-------------|----------|
| `FLASK_ENV` | `development` | Имя окружения |
| `DATABASE_URL` | — | Полный URI БД |
| `DATABASE_HOST` | `localhost` | Хост БД |
| `DATABASE_PORT` | `5432` | Порт БД |
| `DATABASE_NAME` | `production_db` | Имя БД |
| `DATABASE_USER` | `postgres` | Пользователь БД |
| `DATABASE_PASSWORD` | `12345` | Пароль БД |
| `SECRET_KEY` | — | Ключ сессий |
| `SQLALCHEMY_POOL_SIZE` | `10` | Размер пула |
| `SQLALCHEMY_MAX_OVERFLOW` | `20` | Макс. соединений |
| `SQLALCHEMY_POOL_TIMEOUT` | `30` | Таймаут пула |
| `SQLALCHEMY_POOL_RECYCLE` | `3600` | Пересоздание |
| `SQLALCHEMY_ECHO` | `false` | Логирование SQL |
| `TEST_DATABASE_URL` | — | URI тестовой БД |

## Примеры использования

### .env файл
```env
FLASK_ENV=development
DATABASE_URL=postgresql://postgres:mypassword@localhost:5432/production_db
SECRET_KEY=my-super-secret-key-12345
```

### Переключение окружения
```bash
# Разработка
set FLASK_ENV=development

# Продакшн
set FLASK_ENV=production

# Тесты
set FLASK_ENV=testing
```

## Зависимости и связи

| Элемент | Тип связи | Описание |
|---------|-----------|----------|
| `app/__init__.py` | Вызов | Вызывает `get_config()` для загрузки настроек |
| `.env` | Загрузка | Переменные окружения |
| `os` | Стандартная библиотека | Доступ к переменным окружения |
| `dotenv` | Пакет | Загрузка `.env` файла |

## Важные замечания

1. **SECRET_KEY**: Никогда не храните реальный ключ в коде. Всегда используйте `.env`.
2. **Пароли в коде**: Значения по умолчанию для `DATABASE_PASSWORD` (`12345`) — только для разработки.
3. **SQLALCHEMY_ECHO**: Включайте только для отладки SQL-запросов — снижает производительность.
4. **Тестовая БД**: Рекомендуется использовать in-memory SQLite для тестов (как в `tests/conftest.py`).
