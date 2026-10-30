-- ==============================================================================
-- DDL Schema — Personalized Skincare & Decoupled Commerce Engine
-- ==============================================================================

-- Skin Types Catalog
CREATE TABLE IF NOT EXISTS skin_types (
    id VARCHAR(50) PRIMARY KEY,
    label VARCHAR(100) NOT NULL,
    description TEXT NOT NULL
);

-- Skin Concerns Catalog
CREATE TABLE IF NOT EXISTS skin_concerns (
    id VARCHAR(50) PRIMARY KEY,
    label VARCHAR(100) NOT NULL,
    icon VARCHAR(50) NOT NULL,
    description TEXT
);

-- Categories
CREATE TABLE IF NOT EXISTS categories (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(100) NOT NULL UNIQUE
);

-- Products Catalog
CREATE TABLE IF NOT EXISTS products (
    id VARCHAR(50) PRIMARY KEY,
    slug VARCHAR(150) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    category_id VARCHAR(50) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    rating DECIMAL(3, 2) DEFAULT 5.0,
    reviews_count INTEGER DEFAULT 0,
    description TEXT NOT NULL,
    inci_ingredients TEXT NOT NULL,
    clinical_results TEXT,
    image_url VARCHAR(255) NOT NULL,
    has_shade_swatches BOOLEAN DEFAULT FALSE,
    routine_step VARCHAR(50) NOT NULL, -- cleanse, treat, hydrate, protect
    suitable_skin_types TEXT NOT NULL, -- JSON or comma-separated
    target_concerns TEXT NOT NULL,     -- JSON or comma-separated
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id)
);

-- Shade Swatch Matrix (Photorealistic shade fidelity for complexion & tint products)
CREATE TABLE IF NOT EXISTS shade_swatches (
    id VARCHAR(50) PRIMARY KEY,
    product_id VARCHAR(50) NOT NULL,
    shade_id VARCHAR(50) NOT NULL,
    shade_name VARCHAR(100) NOT NULL,
    hex_color VARCHAR(10) NOT NULL,
    undertone VARCHAR(50) NOT NULL, -- cool, warm, neutral, olive
    sku VARCHAR(100) NOT NULL UNIQUE,
    stock_quantity INTEGER NOT NULL DEFAULT 50,
    image_url VARCHAR(255),
    FOREIGN KEY (product_id) REFERENCES products(id)
);

-- Inventory Stock Table
CREATE TABLE IF NOT EXISTS inventory (
    sku VARCHAR(100) PRIMARY KEY,
    product_id VARCHAR(50) NOT NULL,
    available_stock INTEGER NOT NULL DEFAULT 0,
    reserved_stock INTEGER NOT NULL DEFAULT 0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id)
);

-- Atomic Inventory Holds / Reservations (10-minute hold TTL)
CREATE TABLE IF NOT EXISTS inventory_reservations (
    reservation_id VARCHAR(100) PRIMARY KEY,
    sku VARCHAR(100) NOT NULL,
    quantity INTEGER NOT NULL,
    session_id VARCHAR(100) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'RESERVED', -- RESERVED, COMMITTED, EXPIRED, RELEASED
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sku) REFERENCES inventory(sku)
);

-- Orders Table
CREATE TABLE IF NOT EXISTS orders (
    order_id VARCHAR(100) PRIMARY KEY,
    customer_email VARCHAR(255) NOT NULL,
    customer_name VARCHAR(255) NOT NULL,
    shipping_address TEXT NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(10) DEFAULT 'USD',
    status VARCHAR(50) NOT NULL DEFAULT 'CONFIRMED', -- PENDING, CONFIRMED, FULFILLED, CANCELLED
    psp_routed VARCHAR(50) NOT NULL, -- stripe, adyen
    transaction_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Order Items
CREATE TABLE IF NOT EXISTS order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id VARCHAR(100) NOT NULL,
    sku VARCHAR(100) NOT NULL,
    product_id VARCHAR(50) NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);

-- Transactional Outbox Events (CDC & Event Publishing)
CREATE TABLE IF NOT EXISTS outbox_events (
    event_id VARCHAR(100) PRIMARY KEY,
    aggregate_type VARCHAR(100) NOT NULL,
    aggregate_id VARCHAR(100) NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    payload TEXT NOT NULL,
    status VARCHAR(50) DEFAULT 'PENDING',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
