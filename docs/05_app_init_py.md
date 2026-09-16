# Документация: app/__init__.py

## Назначение

Файл `app/__init__.py` реализует **паттерн фабрики приложения** (Application Factory Pattern) для Flask. Это центральный файл инициализации, который создаёт, настраивает и собирает все компоненты приложения Demo27 в единое целое. Вызывается из `run.py` при запуске сервера.

## Структура

### 1. Импорт и загрузка окружения
```python
from dotenv import load_dotenv
from pathlib import Path
```
- Загружает `.env` файл из корня проекта до создания приложения
- Это обеспечивает доступ к переменным окружения (DATABASE_URL, SECRET_KEY и т.д.) для всей конфигурации

### 2. Фабрика `create_app(config_name=None)`

Основная функция, выполняющая пошаговую инициализацию:

#### Шаг 1: Определение окружения
```python
if config_name is None:
    config_name = os.getenv("FLASK_ENV", "development")
```
- Если окружение не указано, используется `FLASK_ENV` из `.env`
- По умолчанию — `development`

#### Шаг 2: Создание экземпляра Flask
```python
app = Flask(__name__,
    template_folder=str(base_dir / "web"),
    static_folder=str(base_dir / "web"),
    static_url_path="/static")
```
- **template_folder** — указывает на `web/` для HTML-шаблонов
- **static_folder** — указывает на `web/` для CSS/JS/изображений
- **static_url_path** — URL-путь для статических файлов

#### Шаг 3: Загрузка конфигурации
```python
config_class = get_config()
app.config.from_object(config_class)
```
- Получает класс конфигурации из `app/config.py`
- Загружает все настройки (DATABASE_URI, SECRET_KEY, параметры пула)

#### Шаг 4: Инициализация расширений
```python
db.init_app(app)
migrate.init_app(app, db)
login_manager.init_app(app)
```
- **db** — SQLAlchemy ORM
- **migrate** — Flask-Migrate (миграции БД)
- **login_manager** — Flask-Login (управление сессиями)

#### Шаг 5: Callback для Flask-Login
```python
@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    return db.session.get(User, int(user_id))
```
- Загружает пользователя из БД по ID для каждой сессии
- Внутренний импорт `User` избегает циклических зависимостей

#### Шаг 6: Регистрация Blueprint
Регистрирует 10 Blueprint с URL-префиксами:

| Blueprint | Префикс | Источник |
|-----------|---------|----------|
| `web_bp` | `/` | `app/blueprints/web` |
| `auth_bp` | `/api/auth` | `app/blueprints/auth` |
| `clients_bp` | `/api/clients` | `app/views/client_view` |
| `products_bp` | `/api/products` | `app/views/product_view` |
| `materials_bp` | `/api/materials` | `app/views/material_view` |
| `operations_bp` | `/api/operations` | `app/views/operation_view` |
| `specifications_bp` | `/api/specifications` | `app/views/specification_view` |
| `sales_orders_bp` | `/api/sales-orders` | `app/views/sales_order_view` |
| `admin_bp` | `/api/admin` | `app/views/admin_view` |
| `notes_bp` | `/api/notes` | `app/views/note_view` |

> **Примечание**: Функция регистрирует Blueprint из `app/views/` (Class-Based Views), а не из `app/blueprints/` (кроме web и auth).

#### Шаг 7: Обработчики ошибок
```python
@app.errorhandler(400)  # Bad Request
@app.errorhandler(404)  # Not Found
@app.errorhandler(500)  # Internal Server Error
```
- Все ошибки возвращают JSON-ответы
- При 500 ошибке выполняется `db.session.rollback()` для отката транзакции

#### Шаг 8: Проверка подключения к БД
```python
def check_db_connection():
    with app.app_context():
        db.engine.connect()
```
- Проверяет доступность PostgreSQL при запуске
- Логирует успех или ошибку

#### Шаг 9: Создание таблиц
```python
with app.app_context():
    check_db_connection()
    db.create_all()
```
- Создаёт все таблицы, которых ещё нет в БД
- Работает только для существующих моделей

### 3. Возврат приложения
```python
return app
```
Возвращает полностью настроенный экземпляр Flask.

## Ключевая логика

- **Factory Pattern**: Позволяет создавать несколько экземпляров приложения для тестирования
- **Внутренние импорты**: Избегают циклических зависимостей (например, `User` импортируется внутри `load_user`)
- **Контекст приложения**: `app.app_context()` создаёт контекст для работы с БД вне запроса
- **Два подхода к маршрутизации**: Одновременно поддерживаются `blueprints/` (web, auth) и `views/` (CRUD API)

## Зависимости и связи

| Элемент | Тип связи | Описание |
|---------|-----------|----------|
| `run.py` | Вызов | Вызывает `create_app()` |
| `app/config.py` | Конфигурация | Загружает классы конфигурации |
| `app/extensions.py` | Инициализация | Предоставляет экземпляры db, migrate, login_manager |
| `app/models.py` | Ссылается | `load_user()` импортирует модель User |
| `app/blueprints/` | Регистрация | web_bp, auth_bp |
| `app/views/` | Регистрация | Все CRUD views |
| `.env` | Загрузка | Переменные окружения |

## Важные замечания

1. **db.create_all()**: Создаёт таблицы только если они не существуют. Для миграций используется Flask-Migrate.
2. **Обработчики ошибок**: Все возвращают JSON, что подходит для API, но не для HTML-страниц.
3. **login_manager.login_view = "web.login_page"**: Указывает на функцию-представление в web_bp для перенаправления при неавторизованном доступе.
4. **Параметры пула БД**: SQLALCHEMY_POOL_SIZE, MAX_OVERFLOW и другие настраиваются через `.env`.
