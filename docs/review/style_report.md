# Отчёт по стилю и структуре кода

## Сводка нарушений

| Код | Кол-во | Категория |
|---|---|---|
| E501 line too long | 272 | стиль |
| W293 blank line contains whitespace | 83 | стиль |
| F401 imported but unused | 10 | логика/чистота |
| E303 too many blank lines | 2 | стиль |
| W291 trailing whitespace | 1 | стиль |
| **Итого** | **368** | |

Вывод `flake8 app/ > docs/review/style_report.txt` — 368 замечаний. Ниже — только значимые (по категориям), полный список в `style_report.txt`.

## E501 — длинные строки (272)

Преобладает `E501`. Причина — длинные строки в:
- `app/views/sales_order_view.py` (самый проблемный: ~160 замечаний, включая строки >150 символов, напр. `:431` — 197 символов);
- `app/models.py` (докстринги и `CheckConstraint` в одну строку);
- `app/blueprints/production_orders.py`, `app/blueprints/specifications.py`;
- `app/dtos/*` (однострочные `from_model`, напр. `material_dto.py:19` — 108 символов).

**Предложение:** настроить `setup.cfg`/`.flake8` с `max-line-length = 100` (компромисс) или прогнать `black -l 79 app/` + `isort`. Для продакшена — `black -l 88` + `flake8 --max-line-length=88`. Зафиксировать в `pyproject.toml`.

## W293 — пустые строки с пробелами (83)

Сконцентрированы в `app/views/sales_order_view.py` (~40), `app/services/production_order_service.py`, `app/views/product_view.py`, `app/views/operation_view.py`.
**Предложение:** `sed -i 's/[[:space:]]*$//'` по файлам, либо `autopep8 --select=W293 -i`.

## F401 — неиспользуемые импорты (10)

| Файл | Строка | Импорт |
|---|---|---|
| `app/services/production_order_service.py` | 26 | `SpecificationMaterial`, `SpecificationOperation` |
| `app/services/sales_order_service.py` | 33 | `ProductPrice`, `SpecificationMaterial`, `SpecificationOperation` |
| `app/views/sales_order_view.py` | 116 | `SpecificationMaterial`, `SpecificationOperation` |
| `app/views/sales_order_view.py` | 362 | `SpecificationMaterial`, `SpecificationOperation` |
| `app/views/sales_order_view.py` | 280 | `sqlalchemy.text` |

**Предложение:** удалить. Признак копипасты между `services/` и `views/`.

## E303 / W291

- `app/views/material_view.py:139`, `app/views/operation_view.py:139` — 3 пустые строки подряд.
- `app/views/sales_order_view.py:230` — trailing whitespace.
**Предложение:** автофикс.

## Структура проекта

`app/auth.py` (работа с хешами паролей) vs `app/blueprints/auth.py` (API) — одинаковые имена модулей, путаница
`app/services/*` — `get_all_dto`/`get_by_id_dto` идентичны почти для всех модулей, можно вынести в базовый класс.
`image/` в корне вместо `web/static/img/`

Ну и главный слон в комнате - все файлы в папке blueprints, кроме `auth.py` и `web.py` - нигде не используются.
По факту это большая груда мёртвого кода.

## Комментарии и докстринги

**Плюсы:** докстринги есть почти везде, стиль выдержан (краткое описание + пояснения для студентов).

**Замечания:**
1. **Докстринги-«учебники»** — в `app/models.py`, `app/__init__.py`, `app/auth.py` докстринги на 20–40 строк объясняют паттерны. Для продакшена — избыточно; лучше вынести в `docs/` или `README`. Приоритет: рекомендация.
2. **Устаревшие докстринги**:
   - `app/__init__.py` — докстринг `create_app` говорит, что `config_name` не используется, но параметр принимается — либо использовать, либо убрать.
4. **Отсутствуют докстринги** у:
   - `app/views/base_view.py` — методы `_success_response`, `_error_response`, `_not_found_response`;
   - `app/repositories/*_repository.py` — специфичные методы (`find_by_login`, `increment_failed_attempts`).