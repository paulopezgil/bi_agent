-- Demo data for portfolio questions.

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
