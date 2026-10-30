BEGIN;

-- Сети магазинов
CREATE TABLE IF NOT EXISTS retailers (
    id BIGSERIAL PRIMARY KEY,
    code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL
);

-- Магазины
CREATE TABLE IF NOT EXISTS stores (
    id BIGSERIAL PRIMARY KEY,
    retailer_id BIGINT NOT NULL REFERENCES retailers(id),
    external_id TEXT,
    city TEXT NOT NULL,
    address TEXT NOT NULL,
    latitude NUMERIC(9, 6),
    longitude NUMERIC(9, 6),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (retailer_id, external_id)
);

-- Категории
CREATE TABLE IF NOT EXISTS categories (
    id BIGSERIAL PRIMARY KEY,
    retailer_id BIGINT NOT NULL REFERENCES retailers(id),
    external_id TEXT NOT NULL,
    parent_id BIGINT REFERENCES categories(id),
    name TEXT NOT NULL,
    UNIQUE (retailer_id, external_id)
);

-- Товары
CREATE TABLE IF NOT EXISTS products (
    id BIGSERIAL PRIMARY KEY,
    retailer_id BIGINT NOT NULL REFERENCES retailers(id),
    external_id TEXT NOT NULL,
    name TEXT NOT NULL,
    brand TEXT,
    category_id BIGINT REFERENCES categories(id),
    weight_g NUMERIC(10, 3),
    unit TEXT,
    calories_per_100g NUMERIC(10, 3),
    protein_per_100g NUMERIC(10, 3),
    fat_per_100g NUMERIC(10, 3),
    carbs_per_100g NUMERIC(10, 3),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (retailer_id, external_id)
);

-- Предложения
CREATE TABLE IF NOT EXISTS store_offers (
    id BIGSERIAL PRIMARY KEY,
    store_id BIGINT NOT NULL REFERENCES stores(id),
    product_id BIGINT NOT NULL REFERENCES products(id),
    price NUMERIC(12, 2),
    is_available BOOLEAN NOT NULL DEFAULT TRUE,
    first_seen_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_seen_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (store_id, product_id)
);

-- История цен
CREATE TABLE IF NOT EXISTS price_history (
    id BIGSERIAL PRIMARY KEY,
    offer_id BIGINT NOT NULL REFERENCES store_offers(id),
    price NUMERIC(12, 2),
    collected_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Запуски парсера
CREATE TABLE IF NOT EXISTS parser_runs (
    id BIGSERIAL PRIMARY KEY,
    retailer_id BIGINT NOT NULL REFERENCES retailers(id),
    started_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    finished_at TIMESTAMPTZ,
    status TEXT NOT NULL CHECK (status IN ('running', 'success', 'partial', 'failed')),
    products_found INTEGER NOT NULL DEFAULT 0,
    error_message TEXT
);

-- Индексы
CREATE INDEX IF NOT EXISTS idx_stores_city_active ON stores (city, is_active);
CREATE INDEX IF NOT EXISTS idx_store_offers_available ON store_offers (store_id, is_available);
CREATE INDEX IF NOT EXISTS idx_price_history_offer_time ON price_history (offer_id, collected_at DESC);

-- ВкусВилл
INSERT INTO retailers (code, name)
VALUES ('vkusvill', 'ВкусВилл')
ON CONFLICT (code) DO NOTHING;

COMMIT;
