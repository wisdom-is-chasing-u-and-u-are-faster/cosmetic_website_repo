-- DDL Schema for Enterprise Online Cosmetic Store Platform (ARCH-5134)
-- Compliant with US FDA MoCRA & EU Cosmetics Regulation (EC) No 1223/2009

CREATE TABLE IF NOT EXISTS products (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    brand TEXT NOT NULL,
    category TEXT NOT NULL,
    price REAL NOT NULL,
    shade TEXT NOT NULL,
    skin_tone TEXT NOT NULL,
    undertone TEXT NOT NULL,
    finish TEXT NOT NULL,
    formulation TEXT NOT NULL, -- JSON string or comma-separated
    allergens TEXT NOT NULL,   -- JSON string or comma-separated
    ingredients TEXT NOT NULL, -- Full ingredient disclosure list
    fda_mocra_listed INTEGER DEFAULT 1,
    eu_1223_2009_compliant INTEGER DEFAULT 1,
    image_url TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS inventory (
    product_id TEXT PRIMARY KEY,
    available_stock INTEGER NOT NULL DEFAULT 0,
    reserved_stock INTEGER NOT NULL DEFAULT 0,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS reservations (
    reservation_id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    product_id TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'ACTIVE', -- ACTIVE, EXPIRED, CONVERTED
    expires_at DATETIME NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id)
);

CREATE TABLE IF NOT EXISTS promotions (
    code TEXT PRIMARY KEY,
    description TEXT NOT NULL,
    discount_type TEXT NOT NULL, -- PERCENTAGE, FIXED_AMOUNT, SHADE_BUNDLE
    discount_value REAL NOT NULL,
    minimum_cart_value REAL DEFAULT 0.0,
    is_active INTEGER DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS orders (
    id TEXT PRIMARY KEY,
    email TEXT NOT NULL,
    customer_name TEXT NOT NULL,
    is_guest INTEGER DEFAULT 1,
    total_amount REAL NOT NULL,
    discount_amount REAL DEFAULT 0.0,
    promo_code TEXT,
    status TEXT NOT NULL DEFAULT 'CONFIRMED', -- CONFIRMED, PROCESSING, SHIPPED, DELIVERED, CANCELLED
    tracking_number TEXT,
    carrier TEXT DEFAULT 'FedEx Logistics',
    shipping_address TEXT NOT NULL, -- JSON string
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id TEXT NOT NULL,
    product_id TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price REAL NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id)
);

CREATE TABLE IF NOT EXISTS returns (
    return_id TEXT PRIMARY KEY,
    order_id TEXT NOT NULL,
    product_id TEXT NOT NULL,
    target_shade_id TEXT,
    type TEXT NOT NULL, -- RETURN, SHADE_EXCHANGE
    status TEXT NOT NULL DEFAULT 'APPROVED', -- APPROVED, REJECTED, PROCESSING, COMPLETED
    reason TEXT NOT NULL,
    prepaid_label_url TEXT,
    exchange_order_id TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(id)
);

CREATE TABLE IF NOT EXISTS idempotency_keys (
    key TEXT PRIMARY KEY,
    request_path TEXT NOT NULL,
    response_code INTEGER NOT NULL,
    response_body TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type TEXT NOT NULL,
    entity_id TEXT,
    details TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
