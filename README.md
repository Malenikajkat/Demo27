# Demo27 — Производственный учёт

Flask-приложение: клиенты, продукция, материалы, операции, спецификации, заказы, заметки, админ-панель.

## Запуск
1. `python -m venv venv` и активировать окружение
2. `pip install -r requirements.txt` (для разработки — `requirements-dev.txt`)
3. Создать БД PostgreSQL и выполнить `database/schema.sql`
4. Скопировать `.env.example` в `.env` и заполнить значения
5. `python run.py` → http://127.0.0.1:5000/

## Тесты и проверки
- `python -m pytest`
- `flake8 app tests run.py` (настройки в `setup.cfg`)
- `bandit -r app run.py`

## Документация
Структура проекта и результаты ревью — в `docs/review/` (`repo_map.md`, `review_report.md`).
