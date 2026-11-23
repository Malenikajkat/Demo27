# Карта репозитория Demo27

Дата: 2026-11-23
Автор ревью: Новожилов
Ветка: review/Новожилов

## 1. Общее описание

Demo27 — веб-приложение на Flask с многослойной архитектурой.
Поток: HTTP → blueprints/views → services → repositories → models → PostgreSQL.
Паттерны: Application Factory (create_app), Configuration Hierarchy (BaseConfig → Dev/Prod/Test).

## 2. Назначение папок и файлов

| Путь | Назначение | Ключевые файлы | Примечание |
|---|---|---|---|
| run.py | Точка входа, порт 5000 | — | debug=True захардкожен |
| requirements.txt | Зависимости | 9 пакетов | Версии через >= |
| .gitignore | Исключения git | — | Исключены migrations/ и alembic/ — ошибка |
| app/__init__.py | create_app(), регистрация Blueprint, error-handlers | — | db.create_all() вместо миграций |
| app/config.py | Классы конфигурации | — | Дефолты SECRET_KEY и пароля 12345 |
| app/extensions.py | db, migrate, login_manager | — | Стандартный паттерн |
| app/models.py | ORM-модели | User и др. | Монолитный файл |
| app/auth.py, app/puzzle_captcha.py | Вспомогательные модули | — | Дублируют blueprints/auth.py, blueprints/puzzle_captcha.py |
| app/blueprints/ | HTTP-слой | 12 модулей | web, auth, admin, clients, materials, notes, operations, production_orders, products, puzzle_captcha, sales_orders, specifications |
| app/views/ | Class-Based Views | 9 блюпринтов + base | Регистрируются с url_prefix /api/... |
| app/services/ | Бизнес-логика | 10 модулей | Нет note_service.py |
| app/repositories/ | Доступ к БД | 9 модулей | Нет note_repository.py |
| app/dtos/ | DTO | 9 модулей | — |
| app/utils.py | Утилиты | — | — |
| database/ | SQL-схема | schema.sql, order_cost_query.sql | er_diagram.pdf отсутствует |
| web/ | HTML + CSS | 13 HTML + styles.css | — |
| tests/ | Тесты | conftest.py, test_auth.py, test_notes.py | Покрытие низкое |
| image/ | Скриншоты | 1.png … 4.png | — |
| docs/ | Отчёты ревью | — | Создана ревьюером |
| scripts/ | ОТСУТСТВУЕТ | — | Задание ссылается — замечание |

## 3. Запуск проекта

Требования: Python 3.10+, PostgreSQL 13+.

1. Клонирование и окружение:
   git clone https://github.com/Malenikajkat/Demo27.git
   cd Demo27
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt

2. Создать БД PostgreSQL (например, production_db).

3. Создать .env в корне:
   FLASK_ENV=development
   SECRET_KEY=<свой ключ>
   DATABASE_HOST=localhost
   DATABASE_PORT=5432
   DATABASE_NAME=production_db
   DATABASE_USER=postgres
   DATABASE_PASSWORD=<свой пароль>

4. Запуск: python run.py. Адрес: http://localhost:5000
5. При старте create_app() вызовет db.create_all().

## 4. Blueprint и префиксы URL

| Blueprint | Модуль | URL-префикс |
|---|---|---|
| web_bp | app.blueprints.web | / |
| auth_bp | app.blueprints.auth | /api/auth |
| clients_bp | app.views.client_view | /api/clients |
| products_bp | app.views.product_view | /api/products |
| materials_bp | app.views.material_view | /api/materials |
| operations_bp | app.views.operation_view | /api/operations |
| specifications_bp | app.views.specification_view | /api/specifications |
| sales_orders_bp | app.views.sales_order_view | /api/sales-orders |
| production_orders_bp | app.views.production_order_view | /api/production-orders |
| admin_bp | app.views.admin_view | /api/admin |
| notes_bp | app.views.note_view | /api/notes |

Error-handlers: 400, 404, 500.

## 5. Схема взаимодействия

HTTP → app/views/*.py и app/blueprints/*.py
     → app/services/*.py
     → app/repositories/*.py
     → app/models.py → PostgreSQL
     ← database/schema.sql, database/order_cost_query.sql

## 6. Замечания по инвентаризации

| № | Категория | Приоритет | Файл | Замечание |
|---|---|---|---|---|
| 1 | документация | важно | — | Нет docs/, scripts/, README.md, postman_collection.json |
| 2 | структура | важно | app/auth.py, app/puzzle_captcha.py | Дублируют файлы в blueprints/ |
| 3 | структура | важно | app/services/, app/repositories/ | Нет note_service.py и note_repository.py |
| 4 | конфигурация | критично | .gitignore | Исключены migrations/ и alembic/ |
| 5 | безопасность | критично | app/config.py | Дефолтные SECRET_KEY и DATABASE_PASSWORD=12345 |
| 6 | безопасность | критично | run.py | debug=True захардкожен |
| 7 | безопасность | важно | app/config.py | TestingConfig содержит пароль 12345 |
| 8 | логика | важно | app/__init__.py | db.create_all() вместо миграций |
| 9 | логика | важно | app/__init__.py | check_db_connection() — except Exception без указания класса |
| 10 | зависимости | важно | requirements.txt | Версии через >= |
| 11 | тесты | важно | tests/ | Покрыты только auth и notes |
| 12 | документация | важно | . | Нет конфигурации линтеров |
