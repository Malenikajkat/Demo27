-- ============================================================
-- Задание 3: Запрос расчёта полной стоимости заказа покупателя
-- ============================================================
-- Запрос вычисляет полную стоимость заказа с учётом:
-- - количества продукции в заказе
-- - стоимости всех материалов (с нормой расхода)
-- - стоимости технологических операций

-- ============================================================
-- Вариант 1: Детальная разбивка по товарам в заказе
-- ============================================================

SELECT
    so.sales_order_id,
    so.order_number,
    so.order_date,
    c.name AS customer_name,
    ex.name AS executor_name,
    soi.sales_order_item_id,
    p.name AS product_name,
    soi.quantity AS ordered_quantity,
    soi.unit_price AS unit_price,
    soi.discount AS line_discount,
    (soi.quantity * soi.unit_price - soi.discount) AS line_total,

    -- Стоимость материалов для данной продукции
    COALESCE(mat_cost.material_cost, 0) AS material_cost,

    -- Стоимость операций для данной продукции
    COALESCE(op_cost.operation_cost, 0) AS operation_cost,

    -- Полная себестоимость производства (материалы + операции) * количество
    (COALESCE(mat_cost.material_cost, 0) + COALESCE(op_cost.operation_cost, 0)) * soi.quantity AS total_production_cost,

    -- Полная стоимость заказа (цена * количество - скидка)
    (soi.quantity * soi.unit_price - soi.discount) AS order_line_total

FROM sales_order_items soi
JOIN sales_orders so ON so.sales_order_id = soi.sales_order_id
JOIN clients c ON c.client_id = so.client_id
JOIN clients ex ON ex.client_id = so.executor_id
JOIN products p ON p.product_id = soi.product_id

-- Подсчёт стоимости материалов для каждого продукта
LEFT JOIN LATERAL (
    SELECT COALESCE(SUM(
            sm.quantity_per_unit * mp.price
        ), 0) AS material_cost
    FROM specification_materials sm
    JOIN materials m ON m.material_id = sm.material_id
    JOIN material_prices mp ON mp.material_id = sm.material_id
        AND mp.effective_date = (
            SELECT MAX(mp2.effective_date)
            FROM material_prices mp2
            WHERE mp2.material_id = sm.material_id
        )
    WHERE sm.product_id = soi.product_id
) mat_cost ON true

-- Подсчёт стоимости операций для каждого продукта
LEFT JOIN LATERAL (
    SELECT COALESCE(SUM(
            (so2.time_norm * so2.op_quantity) * op.price
        ), 0) AS operation_cost
    FROM specification_operations so2
    JOIN operations o ON o.operation_id = so2.operation_id
    JOIN operation_prices op ON op.operation_id = so2.operation_id
        AND op.effective_date = (
            SELECT MAX(op2.effective_date)
            FROM operation_prices op2
            WHERE op2.operation_id = so2.operation_id
        )
    WHERE so2.product_id = soi.product_id
) op_cost ON true

ORDER BY so.order_number, soi.sales_order_item_id;


-- ============================================================
-- Вариант 2: Итоговая стоимость всего заказа
-- ============================================================

SELECT
    so.sales_order_id,
    so.order_number,
    so.order_date,
    c.name AS customer_name,
    ex.name AS executor_name,
    so.total_amount AS declared_total,

    -- Итоговая стоимость материалов по всем товарам
    SUM(mat_cost.material_cost * soi.quantity) AS total_material_cost,

    -- Итоговая стоимость операций по всем товарам
    SUM(op_cost.operation_cost * soi.quantity) AS total_operation_cost,

    -- Полная себестоимость производства
    SUM((COALESCE(mat_cost.material_cost, 0) + COALESCE(op_cost.operation_cost, 0)) * soi.quantity)
        AS total_production_cost,

    -- Итоговая сумма заказа (с учётом скидок)
    SUM(soi.quantity * soi.unit_price - soi.discount) AS calculated_total,

    -- Разница между заявленной и рассчитанной суммой
    SUM(soi.quantity * soi.unit_price - soi.discount) - so.total_amount AS difference

FROM sales_order_items soi
JOIN sales_orders so ON so.sales_order_id = soi.sales_order_id
JOIN clients c ON c.client_id = so.client_id
JOIN clients ex ON ex.client_id = so.executor_id

LEFT JOIN LATERAL (
    SELECT COALESCE(SUM(sm.quantity_per_unit * mp.price), 0) AS material_cost
    FROM specification_materials sm
    JOIN material_prices mp ON mp.material_id = sm.material_id
        AND mp.effective_date = (
            SELECT MAX(mp2.effective_date)
            FROM material_prices mp2
            WHERE mp2.material_id = sm.material_id
        )
    WHERE sm.product_id = soi.product_id
) mat_cost ON true

LEFT JOIN LATERAL (
    SELECT COALESCE(SUM((so2.time_norm * so2.op_quantity) * op.price), 0) AS operation_cost
    FROM specification_operations so2
    JOIN operation_prices op ON op.operation_id = so2.operation_id
        AND op.effective_date = (
            SELECT MAX(op2.effective_date)
            FROM operation_prices op2
            WHERE op2.operation_id = so2.operation_id
        )
    WHERE so2.product_id = soi.product_id
) op_cost ON true

GROUP BY so.sales_order_id, so.order_number, so.order_date,
         c.name, ex.name, so.total_amount;


-- ============================================================
-- Вариант 3: Функция для расчёта стоимости заказа
-- ============================================================

-- Создание функции для повторного использования
CREATE OR REPLACE FUNCTION calculate_order_cost(p_sales_order_id UUID)
RETURNS TABLE (
    product_name VARCHAR(255),
    ordered_quantity DECIMAL,
    material_cost_per_unit DECIMAL,
    operation_cost_per_unit DECIMAL,
    total_cost_per_unit DECIMAL,
    line_total DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        p.name::VARCHAR(255),
        soi.quantity,
        COALESCE(mat_cost.material_cost, 0) AS material_cost_per_unit,
        COALESCE(op_cost.operation_cost, 0) AS operation_cost_per_unit,
        COALESCE(mat_cost.material_cost, 0) + COALESCE(op_cost.operation_cost, 0) AS total_cost_per_unit,
        (COALESCE(mat_cost.material_cost, 0) + COALESCE(op_cost.operation_cost, 0)) * soi.quantity AS line_total
    FROM sales_order_items soi
    JOIN products p ON p.product_id = soi.product_id
    LEFT JOIN LATERAL (
        SELECT COALESCE(SUM(sm.quantity_per_unit * mp.price), 0) AS material_cost
        FROM specification_materials sm
        JOIN material_prices mp ON mp.material_id = sm.material_id
            AND mp.effective_date = (
                SELECT MAX(mp2.effective_date)
                FROM material_prices mp2
                WHERE mp2.material_id = sm.material_id
            )
        WHERE sm.product_id = soi.product_id
    ) mat_cost ON true
    LEFT JOIN LATERAL (
        SELECT COALESCE(SUM((so2.time_norm * so2.op_quantity) * op.price), 0) AS operation_cost
        FROM specification_operations so2
        JOIN operation_prices op ON op.operation_id = so2.operation_id
            AND op.effective_date = (
                SELECT MAX(op2.effective_date)
                FROM operation_prices op2
                WHERE op2.operation_id = so2.operation_id
            )
        WHERE so2.product_id = soi.product_id
    ) op_cost ON true
    WHERE soi.sales_order_id = p_sales_order_id;
END;
$$ LANGUAGE plpgsql;

-- Пример использования:
-- SELECT * FROM calculate_order_cost('sales_order_uuid_here');
