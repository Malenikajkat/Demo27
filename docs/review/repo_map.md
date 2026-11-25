# Карта репозитория Demo27

Дата: 24.11.2026. Проект: https://github.com/Malenikajkat/Demo27 (ветка `master`, 3 коммита, автор `malen`).

## 1. Что это за проект

Учебное веб-приложение «Производственный учёт»: клиенты, продукция, материалы, операции, спецификации (состав изделий), заказы покупателей и заказы на производство, заметки, админ-панель пользователей. Backend — Flask 3 + Flask-SQLAlchemy + Flask-Login, БД — PostgreSQL, фронтенд — Jinja-шаблоны с JavaScript (`fetch` к JSON API).

## 2. Структура папок

| Путь | Назначение |
|---|---|
| `run.py` | Точка входа: `create_app()` и запуск dev-сервера (порт 5000) |
| `app/__init__.py` | Фабрика приложения: конфигурация, расширения, регистрация blueprint'ов, обработчики ошибок 400/404/500, `db.create_all()` |
| `app/config.py` | Классы Development/Production/Testing, сборка `DATABASE_URL` из `.env` |
| `app/extensions.py` | Объекты `db`, `migrate`, `login_manager` без привязки к приложению |
| `app/models.py` | 15 ORM-моделей (Client, Product, Material, Operation, цены, спецификации, заказы и позиции, User, Note) |
| `app/auth.py` | Хеширование и проверка паролей (werkzeug PBKDF2) |
| `app/utils.py` | Форматирование заметок (`00001`, дата `ДД.ММ.ГГГГ`) |
| `app/puzzle_captcha.py` | Пазл-капча из 4 картинок `image/` (на данный момент отключена в `web.py`) |
| `app/blueprints/` | `web.py` (HTML-страницы, вход/выход), `auth.py` (JSON `/api/auth/*`), `puzzle_captcha.py` (не подключён). Остальные файлы — дубли `views/` (см. ST-02) |
| `app/views/` | Class-Based Views (`MethodView`) с REST-API ресурсов; регистрируются в `create_app()` |
| `app/services/` | Слой сервисов: тонкая обёртка над репозиториями + расчёты заказов |
| `app/repositories/` | Слой доступа к данным: `BaseRepository` (get_all/get_by_id/create/update/delete) |
| `app/dtos/` | DTO для сериализации моделей в JSON |
| `database/` | `schema.sql` (DDL, 295 строк) и `order_cost_query.sql` (запрос расчёта стоимости заказа) |
| `web/` | Шаблоны: `base-dashboard.html` (каркас), страницы ресурсов, `login.html`, `styles.css` |
| `image/` | 4 PNG (702×702) для пазл-капчи |
| `tests/` | pytest: `test_auth.py` (7 тестов), `test_notes.py` (7 тестов) |

Слои вызова: **view → service → repository → model**; сериализация — DTO.

## 3. Маршруты

| Префикс | Модуль | Защита |
|---|---|---|
| `/`, `/dashboard`, `/clients`, … `/notes`, `/admin/users`, `/logout` | `blueprints/web.py` | `@login_required` (кроме `/`, `/image/<f>`) |
| `/api/auth/` (login, me, register) | `blueprints/auth.py` | нет |
| `/api/clients/`, `/api/products/`, `/api/materials/`, `/api/operations/`, `/api/specifications/`, `/api/sales-orders/`, `/api/production-orders/`, `/api/notes/` | `views/*` | **нет** (см. S-01) |
| `/api/admin/users/` | `views/admin_view.py` | `login_required` + проверка роли |

## 4. Запуск проекта

1. `git clone https://github.com/Malenikajkat/Demo27.git && cd Demo27`
2. `python -m venv venv` и активация окружения.
3. `pip install -r requirements.txt`
4. Создать БД PostgreSQL и выполнить `database/schema.sql` (либо положиться на `db.create_all()` при старте).
5. Создать `.env` рядом с `run.py` (`DATABASE_URL` или `DATABASE_HOST/PORT/NAME/USER/PASSWORD`, `SECRET_KEY`).
6. `python run.py` → http://127.0.0.1:5000/
7. Тесты: `python -m pytest` (используют SQLite in-memory, PostgreSQL не нужен).

## 5. Что получилось при ознакомительном прогоне

- `pip install -r requirements.txt` — успешно (Flask 3.1.3, SQLAlchemy 2.1.9, Pillow 13.0).
- `pytest` — **14 passed**.
- `pip-audit -r requirements.txt` — известных уязвимостей нет.
- Приложение собрано на SQLite через `test_client` и проверено запросами к API (результаты — в `security_report.md` и `logic_report.md`).
- Не выполнено: запуск `run.py` на живом PostgreSQL и прогон Postman-коллекции — в репозитории нет `postman_collection.json`.

## 6. Чего не хватает относительно задания

В репозитории отсутствуют `docs/`, `scripts/`, `postman_collection.json`, `er_diagram.pdf`, `README.md`, `.env.example`. Сверку схемы БД с ER-диаграммой выполнить нельзя; вместо неё схема `schema.sql` сверена с `models.py` (совпадают таблицы, CHECK-ограничения клиента и роли).

| № | Дата | Описание | Файл:Строка | Категория | Приоритет | Предложение по исправлению |
|---|---|---|---|---|---|---|
| D-01 | 24.11.2026 | Нет README, .env.example, docs, scripts, Postman-коллекции и ER-диаграммы | `корень репозитория` | документация | **Важно** | Написать README с инструкцией запуска и .env.example |
