# Отчёт по стилю и читаемости кода Demo27

**Дата:** 2026-11-23
**Автор ревью:** Новожилов
**Ветка:** review/Новожилов
**Задание:** День 2 — п. 2.1 (структура), 2.2 (PEP 8), 2.3 (докстринги/комментарии)

## 1. Методика

- Инструмент: **flake8 7.5.0** (mccabe 0.7.0, pycodestyle 2.15.0, pyflakes 4.1.0)
- Команда: `py -m flake8 app --max-line-length=100 --exclude=__pycache__,.venv`
- Полная выгрузка: `docs/review/style_report.txt`
- Охват: каталог `app/` (~50 Python-файлов).
- Ручной разбор структуры и докстрингов — по файлам `app/`.

## 2. Сводка

**Всего замечаний: 142.**

| Код | Описание | Кол-во | Приоритет по умолчанию |
|---|---|---:|---|
| E501 | line too long (> 100 символов) | 46 | рекомендация (для >130 симв. — важно) |
| W293 | blank line contains whitespace | 83 | рекомендация |
| F401 | imported but unused | 10 | **важно** |
| E303 | too many blank lines (3) | 2 | рекомендация |
| W291 | trailing whitespace | 1 | рекомендация |

## 3. Распределение по файлам

| Файл | Всего | E501 | W293 | F401 | E303 | W291 |
|---|---:|---:|---:|---:|---:|---:|
| app/views/sales_order_view.py | 72 | 10 | 56 | 5 | 0 | 1 |
| app/services/sales_order_service.py | 13 | 1 | 9 | 3 | 0 | 0 |
| app/services/production_order_service.py | 9 | 1 | 6 | 2 | 0 | 0 |
| app/views/product_view.py | 8 | 3 | 5 | 0 | 0 | 0 |
| app/views/operation_view.py | 7 | 5 | 1 | 0 | 1 | 0 |
| app/views/material_view.py | 6 | 4 | 1 | 0 | 1 | 0 |
| app/views/production_order_view.py | 6 | 3 | 3 | 0 | 0 | 0 |
| app/views/specification_view.py | 5 | 3 | 2 | 0 | 0 | 0 |
| app/models.py | 3 | 3 | 0 | 0 | 0 | 0 |
| app/views/admin_view.py | 2 | 2 | 0 | 0 | 0 | 0 |
| app/views/note_view.py | 1 | 1 | 0 | 0 | 0 | 0 |
| app/views/client_view.py | 1 | 1 | 0 | 0 | 0 | 0 |
| app/services/client_service.py | 1 | 1 | 0 | 0 | 0 | 0 |
| app/blueprints/admin.py | 1 | 1 | 0 | 0 | 0 | 0 |
| app/blueprints/production_orders.py | 1 | 1 | 0 | 0 | 0 | 0 |
| app/blueprints/specifications.py | 1 | 1 | 0 | 0 | 0 | 0 |
| app/dtos/material_dto.py | 1 | 1 | 0 | 0 | 0 | 0 |
| app/dtos/operation_dto.py | 1 | 1 | 0 | 0 | 0 | 0 |
| app/dtos/product_dto.py | 1 | 1 | 0 | 0 | 0 | 0 |
| app/dtos/production_order_dto.py | 1 | 1 | 0 | 0 | 0 | 0 |
| app/dtos/sales_order_dto.py | 1 | 1 | 0 | 0 | 0 | 0 |

## 4. Важные замечания (требуют исправления)

### 4.1. F401 — неиспользуемые импорты

Все 10 случаев — мусорные импорты, которые засоряют код.

| № | Файл:строка | Импорт | Предложение |
|---|---|---|---|
| 1 | app/services/production_order_service.py:26 | SpecificationMaterial | Удалить из import-строки |
| 2 | app/services/production_order_service.py:26 | SpecificationOperation | Удалить из import-строки |
| 3 | app/services/sales_order_service.py:33 | ProductPrice | Удалить |
| 4 | app/services/sales_order_service.py:33 | SpecificationMaterial | Удалить |
| 5 | app/services/sales_order_service.py:33 | SpecificationOperation | Удалить |
| 6 | app/views/sales_order_view.py:116 | SpecificationMaterial (локальный import) | Удалить |
| 7 | app/views/sales_order_view.py:116 | SpecificationOperation (локальный import) | Удалить |
| 8 | app/views/sales_order_view.py:280 | sqlalchemy.text | Удалить |
| 9 | app/views/sales_order_view.py:362 | SpecificationMaterial | Удалить |
| 10 | app/views/sales_order_view.py:362 | SpecificationOperation | Удалить |

Дополнительное наблюдение: в sales_order_view.py импорты моделей сделаны внутри функций (строки 116, 362) — признак обхода циклических импортов, стоит пересмотреть структуру модулей (День 3, категория «логика/структура»).

### 4.2. E501 — очень длинные строки (> 130 символов)

| № | Файл:строка | Длина | Предложение |
|---|---|---:|---|
| 1 | app/views/sales_order_view.py:431 | 197 | Разбить на несколько строк / вынести в переменную |
| 2 | app/views/sales_order_view.py:416 | 160 | То же |
| 3 | app/views/sales_order_view.py:382 | 140 | То же |
| 4 | app/models.py:250 | 125 | То же |

### 4.3. E501 — длинные строки (100–130 символов)

Категория рекомендация. Полный список — в style_report.txt. Файлы: app/views/operation_view.py, material_view.py, production_order_view.py, specification_view.py, admin_view.py, dtos/*, blueprints/*. Решение одно: перенос строк / разбивка f-string / вынесение констант.

## 5. Рекомендации (некритичные)

### 5.1. W293 — пробелы в пустых строках (83 случая)

Самая массовая категория. Пробелы в пустых строках не видны глазу, но ломают diff и мешают мержу.

Файлы: app/views/sales_order_view.py (56), app/services/sales_order_service.py (9), app/services/production_order_service.py (6), app/views/product_view.py (5), app/views/production_order_view.py (3), app/views/specification_view.py (2), app/views/material_view.py (1), app/views/operation_view.py (1).

Полные номера строк — в style_report.txt.

Предложение: удалить пробельные символы в пустых строках. Автоматически: py -m autopep8 --in-place --select=W291,W293,E303 app/ или настроить trim whitespace on save в редакторе.

### 5.2. E303 — лишние пустые строки (2 случая)

| Файл:строка | Предложение |
|---|---|
| app/views/material_view.py:139 | Оставить не более 2 пустых строк между функциями |
| app/views/operation_view.py:139 | То же |

### 5.3. W291 — trailing whitespace (1 случай)

| Файл:строка | Предложение |
|---|---|
| app/views/sales_order_view.py:230 | Удалить пробелы в конце строки |

## 6. Ревью структуры проекта (п. 2.1)

| № | Замечание | Файл | Приоритет | Предложение |
|---|---|---|---|---|
| С1 | Модуль sales_order_view.py раздут: 72 замечания, 554+ строки. Смешаны HTTP-логика, бизнес-логика и SQL-запросы (sqlalchemy.text на строке 280) | app/views/sales_order_view.py | важно | Разделить на view + service + repository, вынести запросы в repository |
| С2 | Дубли app/auth.py ↔ app/blueprints/auth.py и app/puzzle_captcha.py ↔ app/blueprints/puzzle_captcha.py | app/, app/blueprints/ | важно | Проверить, какая версия используется; оставить одну |
| С3 | Отсутствуют note_service.py и note_repository.py, при этом есть notes-blueprint, note_view.py и note_dto.py | app/services/, app/repositories/ | важно | Дополнить слой |
| С4 | Монолитный app/models.py | app/models.py | рекомендация | Разбить на пакет app/models/ по сущностям |
| С5 | Нет конфигурации линтеров | корень репозитория | важно | Добавить .flake8 с max-line-length=100, exclude=__pycache__,.venv |
| С6 | В app/ есть и blueprints/, и views/ с разными соглашениями о наименовании | — | рекомендация | Унифицировать слои |

## 7. Ревью докстрингов и комментариев (п. 2.3)

Проанализированы доступные файлы: run.py, app/__init__.py, app/config.py.

### Положительное
- У всех публичных модулей и функций есть докстринги.
- Есть объяснение «почему» (паттерны Factory, Configuration Hierarchy).
- Комментарии внутри кода объясняют назначение блоков.

### Замечания

| № | Файл:строка | Категория | Приоритет | Замечание | Предложение |
|---|---|---|---|---|---|
| Д1 | app/__init__.py:1–40 | документация | рекомендация | Докстринг модуля ~40 строк, содержит учебные пояснения («Студенты: ...»), уместные в методичке, но не в production-коде | Сократить до 5–7 строк |
| Д2 | app/config.py:1–38 | документация | рекомендация | То же — многострочная «лекция» с «Студенты: ...» | Сократить; подробности в docs/ |
| Д3 | app/__init__.py:110 | документация | рекомендация | «Студенты: обратите внимание…» — учебная лексика | Убрать перед релизом |
| Д4 | app/config.py:_build_database_url | документация | рекомендация | Дефолт password="12345" — подсказка, опасная в production | Убрать дефолт (День 4) |
| Д5 | app/config.py:BaseConfig | документация | рекомендация | SECRET_KEY с дефолтом, комментарий предупреждает, но код не падает | Сделать обязательным (День 4) |
| Д6 | app/__init__.py:bad_request, not_found | стиль | рекомендация | Параметр e не используется | Переименовать в _e — не критично |
| Д7 | app/__init__.py:check_db_connection | логика | важно | except Exception as e — слишком широко; ловит KeyboardInterrupt и SystemExit | Сузить до SQLAlchemyError / OperationalError |

## 8. Предлагаемый план исправлений (по убыванию приоритета)

1. F401 (10 случаев) — удалить неиспользуемые импорты.
2. E501 > 130 (4 случая) — разбить длинные строки.
3. W293 (83) + E303 (2) + W291 (1) — автоформаттер:
   py -m pip install autopep8
   py -m autopep8 --in-place --select=W291,W293,E303 app/
4. E501 100–130 (42) — постепенно.
5. Структурные (С1–С6) — в День 5.
6. Докстринги (Д1–Д5) — сократить.

## 9. Заключение

Стиль кода в целом соответствует PEP 8 — серьёзных нарушений (неопределённые имена, синтаксические проблемы, ошибки уровня F821/F811) не обнаружено. Основная масса замечаний (129 из 142) — механические: длинные строки и пробелы в пустых строках. Они легко устраняются одним прогоном автоформаттера и не влияют на работоспособность.

Наиболее значимые для code review:
- неиспользуемые импорты (F401) — 10 случаев;
- раздутый sales_order_view.py со смешением слоёв;
- отсутствие конфигурации линтеров в репозитории.

Все замечания категории «важно» вынесены в сводную таблицу review_report.md (День 5).
