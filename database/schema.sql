-- ============================================================
-- Схема базы данных информационной системы
-- Задание 2: Создание таблиц на основании ER-диаграммы
-- СУБД: PostgreSQL
-- ============================================================

-- Создание базы данных (выполнить отдельно):
-- CREATE DATABASE production_db;

-- Подключение к базе данных:
-- \c production_db

-- ============================================================
-- Таблица: Заказчики (клиенты)
-- ============================================================
CREATE TABLE clients (
    client_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    inn VARCHAR(20),
    address VARCHAR(255),
    phone VARCHAR(20),
    client_type VARCHAR(20) NOT NULL CHECK (client_type IN ('Поставщик', 'Покупатель')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- Таблица: Продукция
-- ============================================================
CREATE TABLE products (
    product_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    code VARCHAR(50) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- Таблица: Материалы
-- ============================================================
CREATE TABLE materials (
    material_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    code VARCHAR(50) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- Таблица: Технологические операции
-- ============================================================
CREATE TABLE operations (
    operation_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    code VARCHAR(50) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- Таблица: Цены продукции
-- ============================================================
CREATE TABLE product_prices (
    product_price_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID NOT NULL REFERENCES products(product_id) ON DELETE CASCADE,
    price DECIMAL(10,2) NOT NULL CHECK (price >= 0),
    effective_date DATE NOT NULL DEFAULT CURRENT_DATE,
    CONSTRAINT uq_product_price UNIQUE (product_id, effective_date)
);

-- ============================================================
-- Таблица: Цены материалов
-- ============================================================
CREATE TABLE material_prices (
    material_price_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    material_id UUID NOT NULL REFERENCES materials(material_id) ON DELETE CASCADE,
    price DECIMAL(10,2) NOT NULL CHECK (price >= 0),
    effective_date DATE NOT NULL DEFAULT CURRENT_DATE,
    CONSTRAINT uq_material_price UNIQUE (material_id, effective_date)
);

-- ============================================================
-- Таблица: Цены операций
-- ============================================================
CREATE TABLE operation_prices (
    operation_price_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    operation_id UUID NOT NULL REFERENCES operations(operation_id) ON DELETE CASCADE,
    price DECIMAL(10,2) NOT NULL CHECK (price >= 0),
    effective_date DATE NOT NULL DEFAULT CURRENT_DATE,
    CONSTRAINT uq_operation_price UNIQUE (operation_id, effective_date)
);

-- ============================================================
-- Таблица: Спецификация материалов (норма расхода)
-- ============================================================
CREATE TABLE specification_materials (
    spec_mat_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID NOT NULL REFERENCES products(product_id) ON DELETE CASCADE,
    material_id UUID NOT NULL REFERENCES materials(material_id) ON DELETE CASCADE,
    quantity_per_unit DECIMAL(10,4) NOT NULL CHECK (quantity_per_unit > 0),
    CONSTRAINT uq_product_material UNIQUE (product_id, material_id)
);

-- ============================================================
-- Таблица: Спецификация операций (норма операций)
-- ============================================================
CREATE TABLE specification_operations (
    spec_op_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID NOT NULL REFERENCES products(product_id) ON DELETE CASCADE,
    operation_id UUID NOT NULL REFERENCES operations(operation_id) ON DELETE CASCADE,
    time_norm DECIMAL(10,2) NOT NULL DEFAULT 1.0,
    op_quantity DECIMAL(10,2) NOT NULL DEFAULT 1.0,
    CONSTRAINT uq_product_operation UNIQUE (product_id, operation_id)
);

-- ============================================================
-- Таблица: Заказы на производство
-- ============================================================
CREATE TABLE production_orders (
    order_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_number VARCHAR(50) UNIQUE NOT NULL,
    order_date DATE NOT NULL,
    subdivision VARCHAR(100),
    status VARCHAR(20) NOT NULL DEFAULT 'Новый' CHECK (status IN ('Новый', 'В работе', 'Завершён', 'Отменён')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- Таблица: Продукция в заказе на производство
-- ============================================================
CREATE TABLE production_order_items (
    order_item_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    production_order_id UUID NOT NULL REFERENCES production_orders(order_id) ON DELETE CASCADE,
    product_id UUID NOT NULL REFERENCES products(product_id) ON DELETE RESTRICT,
    quantity DECIMAL(10,2) NOT NULL CHECK (quantity > 0)
);

-- ============================================================
-- Таблица: Заказы покупателя
-- ============================================================
CREATE TABLE sales_orders (
    sales_order_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_number VARCHAR(50) UNIQUE NOT NULL,
    order_date DATE NOT NULL,
    client_id UUID NOT NULL REFERENCES clients(client_id),
    executor_id UUID NOT NULL REFERENCES clients(client_id),
    total_amount DECIMAL(12,2) DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_sales_client CHECK (client_id <> executor_id)
);

-- ============================================================
-- Таблица: Товары в заказе покупателя
-- ============================================================
CREATE TABLE sales_order_items (
    sales_order_item_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sales_order_id UUID NOT NULL REFERENCES sales_orders(sales_order_id) ON DELETE CASCADE,
    product_id UUID NOT NULL REFERENCES products(product_id) ON DELETE RESTRICT,
    quantity DECIMAL(10,2) NOT NULL CHECK (quantity > 0),
    unit_price DECIMAL(10,2) NOT NULL CHECK (unit_price >= 0),
    discount DECIMAL(10,2) NOT NULL DEFAULT 0.00 CHECK (discount >= 0)
);

-- ============================================================
-- Индексы для оптимизации запросов
-- ============================================================
CREATE INDEX idx_product_prices_product ON product_prices(product_id);
CREATE INDEX idx_material_prices_material ON material_prices(material_id);
CREATE INDEX idx_operation_prices_operation ON operation_prices(operation_id);
CREATE INDEX idx_spec_materials_product ON specification_materials(product_id);
CREATE INDEX idx_spec_materials_material ON specification_materials(material_id);
CREATE INDEX idx_spec_operations_product ON specification_operations(product_id);
CREATE INDEX idx_spec_operations_operation ON specification_operations(operation_id);
CREATE INDEX idx_prod_orders_date ON production_orders(order_date);
CREATE INDEX idx_sales_orders_date ON sales_orders(order_date);
CREATE INDEX idx_sales_orders_client ON sales_orders(client_id);
CREATE INDEX idx_sales_orders_executor ON sales_orders(executor_id);
CREATE INDEX idx_sales_order_items_order ON sales_order_items(sales_order_id);
CREATE INDEX idx_sales_order_items_product ON sales_order_items(product_id);
CREATE INDEX idx_prod_order_items_order ON production_order_items(production_order_id);
CREATE INDEX idx_prod_order_items_product ON production_order_items(product_id);

-- ============================================================
-- Вставка справочных данных из документов
-- ============================================================

-- Продукция
INSERT INTO products (name, code) VALUES
('Стол кухонный "Самобранка"', 'НФ-00000006');

-- Материалы
INSERT INTO materials (name, code) VALUES
('Столешница круглая', 'ФР-00000009'),
('Мебельная деталь 500x800', 'ФР-00000013'),
('Мебельная деталь 600x800', 'ФР-00000016'),
('Евровинт 6,5x5', 'ФР-00000027'),
('Опора', 'ФР-00000026');

-- Технологические операции
INSERT INTO operations (name, code) VALUES
('Сборка модулей', 'ФР-00000053'),
('Распил ДСП, МДФ и листового материала', 'ФР-00000052'),
('Упаковка', 'ФР-00000049');

-- Цены продукции
INSERT INTO product_prices (product_id, price)
SELECT product_id, 14120.00 FROM products WHERE code = 'НФ-00000006';

-- Цены материалов
INSERT INTO material_prices (material_id, price)
SELECT material_id, price FROM (VALUES
    ('Столешница круглая', 3250.00),
    ('Мебельная деталь 500x800', 95.00),
    ('Мебельная деталь 600x800', 140.00),
    ('Евровинт 6,5x5', 595.00),
    ('Опора', 245.00)
) AS v(name, price)
JOIN materials m ON m.name = v.name;

-- Цены операций
INSERT INTO operation_prices (operation_id, price)
SELECT operation_id, price FROM (VALUES
    ('Сборка модулей', 1400.00),
    ('Распил ДСП, МДФ и листового материала', 450.00),
    ('Упаковка', 950.00)
) AS v(name, price)
JOIN operations o ON o.name = v.name;

-- Спецификация материалов (на 1 единицу продукции)
INSERT INTO specification_materials (product_id, material_id, quantity_per_unit)
SELECT p.product_id, m.material_id, qty FROM (VALUES
    ('Столешница круглая', 1.0000),
    ('Мебельная деталь 500x800', 2.0000),
    ('Мебельная деталь 600x800', 4.0000),
    ('Евровинт 6,5x5', 0.0120),
    ('Опора', 4.0000)
) AS v(mat_name, qty)
JOIN products p ON p.name = 'Стол кухонный "Самобранка"'
JOIN materials m ON m.name = v.mat_name;

-- Спецификация операций (на 1 единицу продукции)
INSERT INTO specification_operations (product_id, operation_id, time_norm, op_quantity)
SELECT p.product_id, o.operation_id, tn, oq FROM (VALUES
    ('Сборка модулей', 0.75, 1.00),
    ('Распил ДСП, МДФ и листового материала', 1.50, 1.00),
    ('Упаковка', 0.50, 1.00)
) AS v(op_name, tn, oq)
JOIN products p ON p.name = 'Стол кухонный "Самобранка"'
JOIN operations o ON o.name = v.op_name;

-- ============================================================
-- Таблица: Пользователи (авторизация)
-- Задание 4: TZ.md - Система авторизации
-- ============================================================
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    login VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'Пользователь' CHECK (role IN ('Администратор', 'Пользователь')),
    is_blocked BOOLEAN NOT NULL DEFAULT FALSE,
    failed_attempts INTEGER NOT NULL DEFAULT 0,
    blocked_until TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- Таблица: Заметки
-- Задание 5: API.md - Таблица notes
-- ============================================================
CREATE TABLE notes (
    note_id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    id_user INTEGER NOT NULL REFERENCES users(user_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Индексы
CREATE INDEX idx_users_login ON users(login);
CREATE INDEX idx_notes_user ON notes(id_user);

-- Вставка тестовых пользователей (пароль: admin123, user123)
INSERT INTO users (login, password_hash, role) VALUES
('admin', 'pbkdf2:sha256:260000$admin$dummyhash', 'Администратор'),
('user1', 'pbkdf2:sha256:260000$user1$dummyhash', 'Пользователь'),
('user2', 'pbkdf2:sha256:260000$user2$dummyhash', 'Пользователь');

-- Вставка тестовых заметок
INSERT INTO notes (title, content, id_user) VALUES
('Конференция ИТ', 'Расписание конференции: 15 марта 2027, зал А', 2),
('Отчёт за Q1', 'Подготовить отчёт по продажам за первый квартал', 3),
('Закупка материалов', 'Заказать столешницы и мебельные детали', 2),
('Спецификация стола', 'Обновить спецификацию для Стол кухонный Самобранка', 3),
('Встреча с заказчиком', 'Обсудить новый заказ на 10 столов', 2);
