-- Baseline Seed Catalog for Enterprise Online Cosmetic Store Platform (ARCH-5134)

INSERT OR IGNORE INTO products (id, name, brand, category, price, shade, skin_tone, undertone, finish, formulation, allergens, ingredients, fda_mocra_listed, eu_1223_2009_compliant, image_url)
VALUES
(
    'PROD-FND-001',
    'Luminous Silk Featherweight Foundation',
    'Aura Luxury Beauty',
    'foundation',
    48.00,
    'Warm Honey 3.5',
    'Medium',
    'Warm',
    'Dewy',
    '["vegan", "cruelty-free", "hypoallergenic", "non-comedogenic"]',
    '["Fragrance Free", "Paraben Free", "Gluten Free"]',
    'Aqua/Water, Cyclopentasiloxane, Glycerin, Isododecane, Dimethicone, Polyglyceryl-4 Isostearate, Tocopherol (Vitamin E), Phenoxyethanol, Iron Oxides (CI 77491, CI 77492, CI 77499), Titanium Dioxide (CI 77891).',
    1,
    1,
    '/assets/images/foundation-warm-honey.png'
),
(
    'PROD-FND-002',
    'Velvet Matte Weightless Foundation',
    'Aura Luxury Beauty',
    'foundation',
    46.00,
    'Cool Porcelain 1.0',
    'Fair',
    'Cool',
    'Matte',
    '["vegan", "cruelty-free", "oil-free", "non-comedogenic"]',
    '["Fragrance Free", "Sulfate Free"]',
    'Aqua/Water, Isododecane, Silica, Dimethicone/Vinyl Dimethicone Crosspolymer, Niacinamide, Squalane, Titanium Dioxide (CI 77891), Iron Oxides.',
    1,
    1,
    '/assets/images/foundation-porcelain.png'
),
(
    'PROD-LIP-001',
    'Hydra-Glaze Satin Peptide Lipstick',
    'Aura Luxury Beauty',
    'lipstick',
    32.00,
    'Rose Petal Kiss',
    'Universal',
    'Neutral',
    'Satin',
    '["vegan", "cruelty-free", "clean-formula"]',
    '["Nut Oil Free", "Paraben Free"]',
    'Ricinus Communis (Castor) Seed Oil, Butyrospermum Parkii (Shea) Butter, Palmitoyl Tripeptide-1, Simmondsia Chinensis (Jojoba) Seed Oil, Red 7 Lake (CI 15850).',
    1,
    1,
    '/assets/images/lipstick-rose-petal.png'
),
(
    'PROD-CON-001',
    'Flawless Blur Hydrating Concealer',
    'Aura Luxury Beauty',
    'concealer',
    28.00,
    'Golden Sand 4.0',
    'Tan',
    'Golden',
    'Natural',
    '["vegan", "cruelty-free", "hypoallergenic"]',
    '["Fragrance Free", "Paraben Free"]',
    'Aqua/Water, Caprylic/Capric Triglyceride, Sodium Hyaluronate, Caffeine, Mica, Iron Oxides (CI 77492).',
    1,
    1,
    '/assets/images/concealer-golden-sand.png'
);

INSERT OR IGNORE INTO inventory (product_id, available_stock, reserved_stock)
VALUES
('PROD-FND-001', 150, 0),
('PROD-FND-002', 80, 0),
('PROD-LIP-001', 200, 0),
('PROD-CON-001', 120, 0);

INSERT OR IGNORE INTO promotions (code, description, discount_type, discount_value, minimum_cart_value, is_active)
VALUES
('BEAUTY20', '20% Off Storewide Discount', 'PERCENTAGE', 20.0, 50.0, 1),
('WELCOME10', '$10 Off Welcome Coupon', 'FIXED_AMOUNT', 10.0, 30.0, 1),
('SHADEBUNDLE', '15% Off Foundation + Concealer Bundle', 'SHADE_BUNDLE', 15.0, 70.0, 1);
