-- ==============================================================================
-- DML Seed Data — Personalized Skincare & Decoupled Commerce Engine
-- ==============================================================================

-- Skin Types
INSERT OR REPLACE INTO skin_types (id, label, description) VALUES
('oily', 'Oily', 'Excess sebum production, shine across T-zone, enlarged pores.'),
('dry', 'Dry', 'Tightness, rough texture, flakiness, requires deep lipid barrier hydration.'),
('combination', 'Combination', 'Oily T-zone (forehead, nose, chin) with normal to dry cheeks.'),
('sensitive', 'Sensitive', 'Prone to stinging, redness, reactivity to fragrances and active acids.'),
('normal', 'Normal', 'Balanced moisture and sebum levels, resilient skin barrier.');

-- Skin Concerns
INSERT OR REPLACE INTO skin_concerns (id, label, icon, description) VALUES
('acne', 'Acne & Blemishes', 'acne', 'Breakouts, blackheads, congested sebum follicles.'),
('aging', 'Fine Lines & Wrinkles', 'sparkles', 'Loss of elasticity, collagen depletion, expression lines.'),
('hyperpigmentation', 'Dark Spots & Uneven Tone', 'sun', 'Post-inflammatory marks, sun damage, melasma.'),
('redness', 'Redness & Rosacea', 'shield', 'Erythema, compromised barrier, vascular reactivity.'),
('dryness', 'Dehydration & Flakiness', 'droplet', 'Trans-epidermal water loss, compromised barrier function.'),
('pores', 'Large Pores & Texture', 'grid', 'Enlarged pores, uneven skin texture, excess congestion.');

-- Categories
INSERT OR REPLACE INTO categories (id, name, slug) VALUES
('cleansers', 'Cleansers', 'cleansers'),
('treatments', 'Serums & Treatments', 'treatments'),
('moisturizers', 'Moisturizers & Creams', 'moisturizers'),
('sunscreens', 'Sun Care & SPF', 'sunscreens'),
('complexion', 'Complexion & Skin Tints', 'complexion');

-- Products
INSERT OR REPLACE INTO products (
    id, slug, name, category_id, price, rating, reviews_count, description,
    inci_ingredients, clinical_results, image_url, has_shade_swatches, routine_step,
    suitable_skin_types, target_concerns
) VALUES
(
    'prod-cleanse-01',
    'gentle-calming-gel-cleanser',
    'Gentle Calming Gel Cleanser',
    'cleansers',
    24.00,
    4.9,
    184,
    'A pH-balanced 5.5 sulfate-free gel cleanser infused with Centella Asiatica and Green Tea to clarify without stripping natural lipids.',
    'Water/Aqua/Eau, Glycerin, Coco-Glucoside, Centella Asiatica Extract, Camellia Sinensis (Green Tea) Leaf Extract, Allantoin, Panthenol, Citric Acid, Phenoxyethanol.',
    '99% agreed skin felt thoroughly clean without tightness or irritation in a 28-day consumer panel.',
    'https://images.unsplash.com/photo-1556228720-195a672e8a03?auto=format&fit=crop&w=600&q=80',
    0,
    'cleanse',
    '["oily", "combination", "sensitive", "normal"]',
    '["acne", "redness", "pores"]'
),
(
    'prod-cleanse-02',
    'barrier-nourish-cream-cleanser',
    'Barrier Nourishing Cream Cleanser',
    'cleansers',
    26.00,
    4.8,
    128,
    'Rich lipid-restoring cream cleanser packed with Oat Kernel Extract and Colloidal Oatmeal for dry, parched skin.',
    'Water/Aqua/Eau, Caprylic/Capric Triglyceride, Avena Sativa (Oat) Kernel Flour, Squalane, Ceramide NP, Cetearyl Alcohol, Glycerin, Sodium Hyaluronate.',
    '100% of participants with dry skin showed zero moisture loss after cleansing.',
    'https://images.unsplash.com/photo-1556228720-195a672e8a03?auto=format&fit=crop&w=600&q=80',
    0,
    'cleanse',
    '["dry", "sensitive", "normal"]',
    '["dryness", "redness"]'
),
(
    'prod-serum-01',
    'niacinamide-clarifying-serum',
    'Niacinamide 10% + Zinc 1% Clarifying Serum',
    'treatments',
    32.00,
    4.8,
    312,
    'High-potency balancing serum clinically formulated to regulate sebum production, minimize pore appearance, and fade post-blemish marks.',
    'Water/Aqua/Eau, Niacinamide (10%), Zinc PCA (1%), Dimethyl Isosorbide, Tamarindus Indica Seed Gum, Xanthan Gum, Isoceteth-20, Ethoxydiglycol, Phenoxyethanol.',
    'Clinical test proved 42% reduction in sebum output and 35% reduction in visible pore diameter within 14 days.',
    'https://images.unsplash.com/photo-1620916566398-39f1143ab7be?auto=format&fit=crop&w=600&q=80',
    0,
    'treat',
    '["oily", "combination", "sensitive"]',
    '["acne", "pores", "redness", "hyperpigmentation"]'
),
(
    'prod-serum-02',
    'multi-peptide-hyaluronic-serum',
    'Multi-Peptide + HA Youth Renewal Serum',
    'treatments',
    46.00,
    4.9,
    215,
    'Advanced peptide matrix combined with multi-molecular hyaluronic acid to stimulate collagen synthesis and diminish fine lines.',
    'Water/Aqua/Eau, Sodium Hyaluronate, Palmitoyl Tripeptide-1, Palmitoyl Tetrapeptide-7, Copper Tripeptide-1, Acetyl Hexapeptide-8, Glycerin, Butylene Glycol.',
    '94% demonstrated statistically significant improvement in skin firmness and wrinkle depth reduction.',
    'https://images.unsplash.com/photo-1608248597359-5f2524fb6192?auto=format&fit=crop&w=600&q=80',
    0,
    'treat',
    '["dry", "combination", "normal", "sensitive"]',
    '["aging", "dryness"]'
),
(
    'prod-moist-01',
    'barrier-support-ceramide-water-cream',
    'Barrier Support Ceramide Water Cream',
    'moisturizers',
    38.00,
    4.9,
    240,
    'Weightless, fast-absorbing gel-cream infused with 5 essential ceramides, squalane, and ectoin to lock in 72-hour continuous hydration.',
    'Water/Aqua/Eau, Squalane, Ceramide EOP, Ceramide EOS, Ceramide NP, Ceramide NS, Ceramide AP, Ectoin, Sodium Hyaluronate, Glycerin, Carbomer, Phenoxyethanol.',
    'Proven 180% immediate boost in skin moisture and 48% reduction in TEWL (Trans-Epidermal Water Loss).',
    'https://images.unsplash.com/photo-1535585209827-a15fcdbc4c2d?auto=format&fit=crop&w=600&q=80',
    0,
    'hydrate',
    '["oily", "dry", "combination", "sensitive", "normal"]',
    '["dryness", "redness", "aging"]'
),
(
    'prod-spf-01',
    'invisible-mineral-shield-spf-50',
    'Invisible Mineral Shield SPF 50',
    'sunscreens',
    28.00,
    4.8,
    192,
    '100% non-nano Zinc Oxide mineral sunscreen that glides on sheer with zero white cast, protecting against UVA/UVB and blue light radiation.',
    'Zinc Oxide (18.5%), Water/Aqua/Eau, Caprylic/Capric Triglyceride, Butyloctyl Salicylate, Silica, Niacinamide, Bisabolol, Tocopherol, Polyglyceryl-4 Diisostearate.',
    'Broad spectrum SPF 50 PA++++ tested in vivo. Water resistant for 80 minutes.',
    'https://images.unsplash.com/photo-1598440947619-2c35fc9aa908?auto=format&fit=crop&w=600&q=80',
    0,
    'protect',
    '["oily", "dry", "combination", "sensitive", "normal"]',
    '["aging", "hyperpigmentation", "redness"]'
),
(
    'prod-tint-01',
    'luminous-hydrating-skin-tint',
    'Luminous Hydrating Skin Tint SPF 30',
    'complexion',
    42.00,
    4.9,
    275,
    'Breathable light-to-medium coverage complexion tint with photo-accurate shade fidelity, providing an undetectable radiant finish.',
    'Water/Aqua/Eau, Squalane, Isohexadecane, Glycerin, Niacinamide, Sodium Hyaluronate, Zinc Oxide, Iron Oxides (CI 77491, CI 77492, CI 77499), Titanium Dioxide (CI 77891).',
    '98% agreed skin appeared naturally luminous without settling into fine lines.',
    'https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?auto=format&fit=crop&w=600&q=80',
    1,
    'protect',
    '["oily", "dry", "combination", "sensitive", "normal"]',
    '["hyperpigmentation", "pores", "redness"]'
);

-- Shade Swatch Matrix for Complexion Tint (Photorealistic Shade Accuracy)
INSERT OR REPLACE INTO shade_swatches (id, product_id, shade_id, shade_name, hex_color, undertone, sku, stock_quantity, image_url) VALUES
('sw-tint-100', 'prod-tint-01', 'shade-100', 'Fair Neutral 100', '#F7E2D2', 'neutral', 'SKU-TINT-100', 80, 'https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?w=200'),
('sw-tint-110', 'prod-tint-01', 'shade-110', 'Light Cool 110', '#EFCDBB', 'cool', 'SKU-TINT-110', 65, 'https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?w=200'),
('sw-tint-200', 'prod-tint-01', 'shade-200', 'Medium Warm 200', '#DFA884', 'warm', 'SKU-TINT-200', 95, 'https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?w=200'),
('sw-tint-300', 'prod-tint-01', 'shade-300', 'Tan Olive 300', '#B87F55', 'olive', 'SKU-TINT-300', 50, 'https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?w=200'),
('sw-tint-400', 'prod-tint-01', 'shade-400', 'Deep Warm 400', '#6E442B', 'warm', 'SKU-TINT-400', 40, 'https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?w=200');

-- Inventory Stock
INSERT OR REPLACE INTO inventory (sku, product_id, available_stock, reserved_stock) VALUES
('SKU-CLEANSE-01', 'prod-cleanse-01', 150, 0),
('SKU-CLEANSE-02', 'prod-cleanse-02', 120, 0),
('SKU-SERUM-01', 'prod-serum-01', 200, 0),
('SKU-SERUM-02', 'prod-serum-02', 90, 0),
('SKU-MOIST-01', 'prod-moist-01', 180, 0),
('SKU-SPF-01', 'prod-spf-01', 140, 0),
('SKU-TINT-100', 'prod-tint-01', 80, 0),
('SKU-TINT-110', 'prod-tint-01', 65, 0),
('SKU-TINT-200', 'prod-tint-01', 95, 0),
('SKU-TINT-300', 'prod-tint-01', 50, 0),
('SKU-TINT-400', 'prod-tint-01', 40, 0);
