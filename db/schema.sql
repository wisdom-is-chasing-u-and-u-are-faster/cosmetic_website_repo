-- Enterprise Online Cosmetic Store Database Schema
-- Supports FDA MoCRA & EU 1223/2009 disclosures, faceted shades, inventory locks, orders, and 3PL webhooks

CREATE TABLE IF NOT EXISTS products (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    brand TEXT NOT NULL,
    category TEXT NOT NULL,
    price REAL NOT NULL,
    rating REAL DEFAULT 4.8,
    description TEXT,
    finish TEXT,
    is_hero INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS product_shades (
    id TEXT PRIMARY KEY,
    product_id TEXT NOT NULL,
    sku TEXT UNIQUE NOT NULL,
    shade_name TEXT NOT NULL,
    hex_code TEXT NOT NULL,
    skin_tone TEXT NOT NULL,
    undertone TEXT NOT NULL,
    stock_quantity INTEGER NOT NULL DEFAULT 100,
    FOREIGN KEY(product_id) REFERENCES products(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS product_attributes (
    id TEXT PRIMARY KEY,
    product_id TEXT NOT NULL,
    formulations TEXT NOT NULL,
    allergens TEXT NOT NULL,
    ingredients TEXT NOT NULL,
    mocra_disclosures TEXT NOT NULL,
    eu_compliance TEXT NOT NULL,
    FOREIGN KEY(product_id) REFERENCES products(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS promotions (
    id TEXT PRIMARY KEY,
    code TEXT UNIQUE NOT NULL,
    description TEXT,
    discount_type TEXT NOT NULL,
    discount_value REAL NOT NULL,
    min_spend REAL DEFAULT 0.0,
    is_active INTEGER DEFAULT 1,
    expires_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS inventory_reservations (
    reservation_id TEXT PRIMARY KEY,
    sku TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT "active",
    expires_at TIMESTAMP NOT NULL,
    idempotency_key TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS customers (
    id TEXT PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    full_name TEXT NOT NULL,
    phone TEXT,
    skin_tone_profile TEXT,
    undertone_profile TEXT,
    is_pii_erased INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS orders (
    id TEXT PRIMARY KEY,
    order_number TEXT UNIQUE NOT NULL,
    customer_id TEXT,
    customer_email TEXT NOT NULL,
    is_guest INTEGER DEFAULT 1,
    total_amount REAL NOT NULL,
    discount_amount REAL DEFAULT 0.0,
    promo_code TEXT,
    payment_method TEXT NOT NULL,
    payment_status TEXT NOT NULL,
    tracking_carrier TEXT DEFAULT "FedEx Express",
    tracking_number TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT "confirmed",
    shipping_address TEXT NOT NULL,
    billing_address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS order_items (
    id TEXT PRIMARY KEY,
    order_id TEXT NOT NULL,
    sku TEXT NOT NULL,
    product_name TEXT NOT NULL,
    shade_name TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price REAL NOT NULL,
    subtotal REAL NOT NULL,
    FOREIGN KEY(order_id) REFERENCES orders(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS returns (
    id TEXT PRIMARY KEY,
    order_id TEXT NOT NULL,
    return_type TEXT NOT NULL,
    original_sku TEXT NOT NULL,
    exchange_sku TEXT,
    reason TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT "approved",
    return_label_url TEXT NOT NULL,
    exchange_order_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(order_id) REFERENCES orders(id)
);

CREATE TABLE IF NOT EXISTS tracking_events (
    id TEXT PRIMARY KEY,
    order_id TEXT NOT NULL,
    tracking_number TEXT NOT NULL,
    status TEXT NOT NULL,
    location TEXT NOT NULL,
    description TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(order_id) REFERENCES orders(id)
);

CREATE TABLE IF NOT EXISTS idempotency_records (
    key TEXT PRIMARY KEY,
    status_code INTEGER NOT NULL,
    response_body TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id TEXT PRIMARY KEY,
    event_type TEXT NOT NULL,
    entity_id TEXT NOT NULL,
    details TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
