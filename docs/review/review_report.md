#Сводная таблица замечаний и итоговый отчёт

| № | Приоритет | Категория | Затронутый файл / место | Замечание | Предложение по исправлению |
|---|---|---|---|---|---|
| 1 | 🔴 Критично | Безопасность / доступ | CRUD-эндпоинты: clients, products, materials, operations, specifications, orders | Нет `@login_required` и проверки роли — аноним может создавать/изменять/удалять данные | Добавить `@login_required` на все state-changing маршруты + проверку `current_user.role` |
| 2 | 🔴 Критично | Безопасность / доступ | `app/blueprints/auth.py` — `POST /api/auth/register` | `role` берётся из тела запроса — любой может зарегистрироваться как «Администратор» | Убрать `role` из публичного register (всегда «Пользователь») либо требовать администратора |
| 3 | 🔴 Критично | Безопасность / аутентификация | `app/blueprints/auth.py`, `app/blueprints/web.py` | `is_blocked` проверяется после пароля — возможен бесконечный перебор паролей | Сначала проверять `user.is_blocked` (→ 403), затем пароль |
| 4 | 🔴 Критично | Безопасность / XSS | `admin-dashboard.html` и др. шаблоны с `innerHTML` | Сборка HTML через `innerHTML` + шаблонные строки с пользовательскими данными (напр. `editUser(${user.login})`) — инъекции в атрибуты/разметку | Использовать `textContent`, `createElement`, экранирование; `addEventListener` вместо `onclick` с интерполяцией |
| 5 | 🔴 Критично | Безопасность / CSRF | `requirements.txt`, все state-changing маршруты | Нет Flask-WTF / Flask-SeaSurf — POST/DELETE без CSRF-токена | Подключить `CSRFProtect`, включить для всех POST/PUT/PATCH/DELETE, передавать токен в шаблоны/заголовки |
| 6 | 🔴 Критично | БД / схема | `app/models.py` vs `database/schema.sql` | Расхождения: нет `UniqueConstraint` у цен и спецификаций; `ProductionOrder.sales_order_id` есть в модели, но нет в SQL — создание произв. заказа упадёт | Синхронизировать `schema.sql` с моделями или генерировать SQL из моделей |
| 7 | 🟠 Важно | Логика / БД | `material_view.py`, `operation_view.py`, `product_view.py` (PriceAPI) | Удаляются все старые цены — уничтожается история; удаление+вставка без явной транзакции | Вставлять новую запись с `effective_date`, не удаляя старые; обернуть в транзакцию |
| 8 | 🟠 Важно | Логика / API | `app/views/production_order_view.py` — `ProductionOrderListAPI.post` | Неверный UUID продукта молча пропускается (`continue`) — часть позиций не создаётся | Аккумулировать ошибки и возвращать 400 со списком невалидных позиций |
| 9 | 🟠 Важно | Логика / чистота | `app/blueprints/auth.py` — `register` | Дублирование `data = request.get_json()` | Удалить лишнюю строку |
| 10 | 🟠 Важно | Тесты | Весь API (clients, products, materials, operations, specifications, production_orders, sales_orders, admin, puzzle_captcha) | ~90% API без тестов; покрыты только auth и notes | Создать `postman_collection.json` и покрыть отсутствующие эндпоинты |
| 11 | 🟠 Важно | Структура / мёртвый код | `app/blueprints/*` (кроме `auth.py`, `web.py`) | Файлы нигде не используются — груда мёртвого кода | Удалить неиспользуемые blueprint-файлы |
| 12 | 🟡 Рекомендация | Стиль / E501 | `sales_order_view.py` (~160), `models.py`, `production_orders.py`, `specifications.py`, `dtos/*` | 272 длинных строки (до 197 символов) | Настроить `.flake8`/`pyproject.toml` (`max-line-length = 100` или 88), прогнать `black` + `isort` |
| 13 | 🟡 Рекомендация | Стиль / W293 | `sales_order_view.py` (~40), `production_order_service.py`, `product_view.py`, `operation_view.py` | 83 пустые строки с пробелами | `sed -i 's/[[:space:]]*$//'` или `autopep8 --select=W293 -i` |
| 14 | 🟡 Рекомендация | Стиль / F401 | `production_order_service.py`, `sales_order_service.py`, `sales_order_view.py` | 10 неиспользуемых импортов (признак копипасты между services/ и views/) | Удалить неиспользуемые импорты |
| 15 | 🟡 Рекомендация | Стиль / E303, W291 | `material_view.py:139`, `operation_view.py:139`, `sales_order_view.py:230` | 3 пустые строки подряд; trailing whitespace | Автофикс |
| 16 | 🟡 Рекомендация | Фронтенд / CSS | `production-orders.html`, `sales-orders.html`, `base-dashboard.html` | Дублирование и локальные переопределения CSS (`.status-badge`, `.modal-body` и т.д.) | Вынести общие стили в `styles.css` или `base-dashboard.html` |
| 17 | 🟡 Рекомендация | Фронтенд / UI | Шаблоны (иконки) | Иконки — эмодзи (✏️ 💰 🗑️ 👁️), неконсистентно с UI | Использовать SVG или иконочный шрифт |
| 18 | 🟡 Рекомендация | Документация | Корень проекта / `docs/` | Нет README, скрипта тестовых данных, описания API | Добавить README, скрипт заполнения тестовыми данными, документацию API |
| 19 | 🟡 Рекомендация | Структура | `app/auth.py` vs `app/blueprints/auth.py`; `app/services/*`; `image/` | Одинаковые имена модулей — путаница; `get_all_dto`/`get_by_id_dto` дублируются; `image/` в корне вместо `web/static/img/` | Переименовать модули, вынести общие методы в базовый класс, перенести `image/` |
| 20 | 🟡 Рекомендация | Документация / докстринги | `app/models.py`, `app/__init__.py`, `app/auth.py`; `app/__init__.py` (`create_app`); `base_view.py`; `repositories/*` | Докстринги-«учебники» на 20–40 строк; устаревший докстринг про `config_name`; отсутствуют докстринги у ряда методов | Вынести учебные пояснения в `docs/`/README; исправить/дополнить докстринги |

Итоговый вывод:

Видно, что проект сделан в учебных целях, но для выпуска в продакшен требуются серьёзные исправления.
Особенно в сфере безопасности.