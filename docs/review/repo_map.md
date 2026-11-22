# Карта репозитория Demo27

## Запуск проекта

1. git clone https://github.com/Malenikajkat/Demo27
1. Создать venv интерпретатор Python в PyCharm
1. `pip install -r requirements.txt`
1. Создать `.env` с `DATABASE_URL` (или `DATABASE_*`), `SECRET_KEY`, `FLASK_ENV`
1. `python run.py` — приложение поднимется на `http://localhost:5000`
## Назначение папок

| Папка/файл | Назначение |
|---|---|
| `app/` | Код приложения (Flask factory + слои) |
| `app/__init__.py` | `create_app()`, регистрация blueprint'ов, error handlers |
| `app/config.py` | Конфиги: Development/Production/Testing, сборка `DATABASE_URL` |
| `app/extensions.py` | Инициализация `db`, `migrate`, `login_manager` (без app) |
| `app/models.py` | SQLAlchemy-модели (Client, Product, Material, Operation, Order'ы, User, Note) |
| `app/auth.py` | Хеширование/проверка паролей (PBKDF2) |
| `app/puzzle_captcha.py` | Пазл-капча (генерация фрагментов, verify) |
| `app/utils.py` | Форматтеры для API заметок |
| `app/blueprints/` | Функциональные blueprint'ы (auth, web, admin, CRUD-API) |
| `app/views/` | Class-Based Views (по сущностям + admin) |
| `app/services/` | Бизнес-логика (BaseService + сервисы сущностей, auth_service) |
| `app/repositories/` | Доступ к БД (BaseRepository + репозитории сущностей) |
| `app/dtos/` | Data Transfer Objects (dataclass + `from_model`/`to_dict`) |
| `database/` | `schema.sql`, `order_cost_query.sql` — DDL и аналитика |
| `docs/` | Документация проекта |
| `image/` | 4 PNG для пазл-капчи |
| `tests/` | `conftest.py`, `test_auth.py`, `test_notes.py` |
| `web/` | HTML-шаблоны + `styles.css` |
| `requirements.txt` | Зависимости |
| `run.py` | Точка входа |

## Архитектура (слои)

Поток запроса идёт сверху вниз:

1. **Blueprints / Views** — принимают HTTP-запрос, валидируют вход, вызывают сервис.
   Blueprints (`app/blueprints/`) — функции-хендлеры; Views (`app/views/`) — class-based (`MethodView`).
2. **Services** (`app/services/`) — бизнес-логика, оркестрация репозиториев, возврат JSON/HTTP-кода.
3. **Repositories** (`app/repositories/`) — доступ к БД через SQLAlchemy, без бизнес-логики.
4. **Models** (`app/models.py`) — ORM-маппинг таблиц, связи, `CheckConstraint`.

Отдельно: **DTO** (`app/dtos/`) — сериализация ORM-объектов в `dict` (`from_model`/`to_dict`), используются сервисами при формировании ответа.
