-- Schema + seed data for local portfolio demo.

CREATE TABLE IF NOT EXISTS customers (
    customer_id SERIAL PRIMARY KEY,
    full_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    country TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS products (
    product_id SERIAL PRIMARY KEY,
    sku TEXT UNIQUE NOT NULL,
    product_name TEXT NOT NULL,
    category TEXT NOT NULL,
    unit_price NUMERIC(12, 2) NOT NULL CHECK (unit_price >= 0)
);

CREATE TABLE IF NOT EXISTS orders (
    order_id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(customer_id),
    order_date DATE NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('pending', 'paid', 'shipped', 'cancelled')),
    total_amount NUMERIC(12, 2) NOT NULL CHECK (total_amount >= 0)
);

CREATE TABLE IF NOT EXISTS order_items (
    order_item_id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES orders(order_id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL REFERENCES products(product_id),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price NUMERIC(12, 2) NOT NULL CHECK (unit_price >= 0)
);

INSERT INTO customers (full_name, email, country)
VALUES
    ('Ana Perez', 'ana.perez@example.com', 'ES'),
    ('John Smith', 'john.smith@example.com', 'US'),
    ('Marta Rossi', 'marta.rossi@example.com', 'IT')
ON CONFLICT (email) DO NOTHING;

INSERT INTO products (sku, product_name, category, unit_price)
VALUES
    ('SKU-1001', 'Notebook Pro 14', 'laptops', 1499.00),
    ('SKU-2001', 'Wireless Mouse X', 'accessories', 49.90),
    ('SKU-3001', '4K Monitor 27', 'monitors', 379.00)
ON CONFLICT (sku) DO NOTHING;

INSERT INTO orders (customer_id, order_date, status, total_amount)
VALUES
    (1, CURRENT_DATE - INTERVAL '3 days', 'paid', 1548.90),
    (2, CURRENT_DATE - INTERVAL '2 days', 'shipped', 379.00)
ON CONFLICT DO NOTHING;

INSERT INTO order_items (order_id, product_id, quantity, unit_price)
VALUES
    (1, 1, 1, 1499.00),
    (1, 2, 1, 49.90),
    (2, 3, 1, 379.00)
ON CONFLICT DO NOTHING;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'bi_readonly') THEN
        CREATE ROLE bi_readonly LOGIN PASSWORD 'bi_readonly_pass';
    END IF;
END
$$;

GRANT USAGE ON SCHEMA public TO bi_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO bi_readonly;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO bi_readonly;
