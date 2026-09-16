# Документация: database/order_cost_query.sql

## Назначение

SQL-запросы для расчёта полной стоимости заказа покупателя с учётом материалов и операций.

## Варианты

### Вариант 1: Детальная разбивка
- JOIN с LATERAL для материалов и операций
- Себестоимость = (материалы + операции) * количество

### Вариант 2: Итоговая стоимость
- GROUP BY по заказу
- Суммирование по всем товарам
- Разница между заявленной и расчётной суммой

### Вариант 3: PL/pgSQL функция
```sql
CREATE FUNCTION calculate_order_cost(p_sales_order_id UUID)
RETURNS TABLE (...)
```

## Формула

`material_cost = SUM(quantity_per_unit * price)`
`operation_cost = SUM(time_norm * op_quantity * price)`
`total = (material_cost + operation_cost) * quantity`
