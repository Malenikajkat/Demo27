# Отчёт: зависимости

Дата: 24.11.2026. Файл: `requirements.txt` (9 пакетов).

| Пакет | Ограничение | Где используется | Комментарий |
|---|---|---|---|
| Flask | `>=3.0.0` | везде | основной фреймворк |
| Flask-SQLAlchemy | `>=3.1.0` | `extensions.py`, модели | ок |
| Flask-Login | `>=0.6.0` | аутентификация | ок |
| Flask-Migrate | `>=4.0.0` | `extensions.py` | подключён, но миграции в `.gitignore` (B-01) |
| Werkzeug | `>=3.0.0` | `app/auth.py` | приходит вместе с Flask |
| Pillow | `>=10.0.0` | `app/puzzle_captcha.py` | нужен капче |
| psycopg2-binary | `>=2.9.0` | драйвер PostgreSQL | для продакшена лучше `psycopg2` |
| python-dotenv | `>=1.0.0` | `config.py`, `__init__.py` | ок |
| alembic | `>=1.13.0` | не импортируется | приходит с Flask-Migrate |

Установлено при ревью: Flask 3.1.3, Flask-SQLAlchemy 3.1.1, Flask-Login 0.6.3, Flask-Migrate 4.1.0, Werkzeug 3.1.9, SQLAlchemy 2.1.9, Pillow 13.0.0.

**`pip-audit -r requirements.txt` → No known vulnerabilities found.**

## Таблица замечаний

| № | Дата | Описание | Файл:Строка | Категория | Приоритет | Предложение по исправлению |
|---|---|---|---|---|---|---|
| P-01 | 24.11.2026 | В requirements.txt у всех пакетов только >=, верхней границы нет | `requirements.txt:1-9` | безопасность (зависимости) | **Важно** | Указать диапазоны версий |
