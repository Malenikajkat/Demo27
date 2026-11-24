# Отчёт по ревью логики, работы с БД и тестами.

## 1. Маршруты и обработчики (логика)

### Дублирование проверки блокировки после неудачной попытки входа

Файл: app/blueprints/auth.py, app/blueprints/web.py
В обработчиках входа проверка is_blocked выполняется после проверки корректности пароля.
Поэтому пользователь узнает, что заблокирован, только после того как введёт верный пароль.

**Рекомендация**: сначала проверять user.is_blocked (→ 403), затем проверять пароль.

### Дублирование строки data = request.get_json() в register

Файл: app/blueprints/auth.py
В функции register строка data = request.get_json() продублирована дважды.
Функциональность не ломает.

**Рекомендация**: Удалить лишнию строчку

### ProductionOrderListAPI.post игнорирует ошибки парсинга items

Файл: app/views/production_order_view.py
В цикле for item_data in data["items"] при неверном UUID продукта выполняется continue — позиция молча пропускается.
Пользователь не узнает, что часть позиций не создана.

**Рекомендация**: Нужно аккумулировать ошибки и возвращать 400 со списком невалидных позиций.

### MaterialPriceAPI/OperationPriceAPI/ProductPriceAPI удаляют все старые цены

Файлы: app/views/material_view.py, operation_view.py, product_view.py
При обновлении цены удаляются все записи из *_prices для данной сущности и создаётся одна новая с effective_date = CURRENT_DATE.
Это уничтожает историю цен, что противоречит модели с effective_date (задумано для версионирования).
Кроме того, удаление и вставка не обёрнуты в явную транзакцию — при сбое можно потерять цены.

**Рекомендация**: вставлять новую запись с effective_date, не удаляя старые; либо удалять только записи с effective_date = CURRENT_DATE.


## 2. Работа с базой данных

### Риск SQL-инъекций
Везде параметризация. Прямых конкатенаций SQL нет. Риска SQL-инъекций нет.

### Расхождение схемы models.py и schema.sql

Файлы: app/models.py vs database/schema.sql

В models.py у ProductPrice/MaterialPrice/OperationPrice нет UniqueConstraint(product_id, effective_date),
а в schema.sql — есть (uq_product_price и т.д.). При create_all() ограничение не создастся.
    
В models.py у ProductionOrder есть sales_order_id с ondelete="CASCADE", а в schema.sql столбца sales_order_id в
production_orders вообще нет. То есть schema.sql не соответствует текущей модели — при развёртывании из SQL автоматическое
создание производственного заказа из SalesOrderListAPI.post упадёт.
    
В models.py у SpecificationMaterial/SpecificationOperation нет UniqueConstraint(product_id, material_id) / (product_id, operation_id), а в schema.sql — есть.

**Рекомендация**: синхронизировать schema.sql с моделями (или генерировать SQL из моделей).

## Тесты

### Покрытие

Покрыты только `auth` (7 тестов) и `notes` (7 тестов). **Не покрыты:** clients, products, materials, operations, specifications, production_orders, sales_orders, admin, puzzle_captcha. То есть ~90% API без тестов. 
**Рекомендация**: Создать отсутсвующий файл postman_collection.json и протестировать

### Запускаемость

Все тесты запускаются средствами PyCharm и завершаются без ошибок.