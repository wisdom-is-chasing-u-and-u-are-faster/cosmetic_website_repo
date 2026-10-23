-- Baseline Seed Data for Cosmetics Platform

INSERT OR REPLACE INTO products (id, name, brand, category, price, rating, description, finish, is_hero) VALUES
('prod-lum-silk', 'Luminous Silk Flawless Foundation', 'Aura Beauty', 'Foundation', 48.00, 4.9, 'Weightless liquid foundation with 24-hour hydration and micro-fil technology for a natural radiant glow.', 'Radiant', 1),
('prod-vel-matte', 'Velvet Matte Liquid Lip Color', 'Aura Beauty', 'Lips', 28.00, 4.8, 'Ultra-pigmented, transfer-proof matte lip cream infused with hyaluronic acid spheres.', 'Matte', 1),
('prod-hydra-glow', 'Hydra-Glow Multi-Use Concealer', 'Aura Beauty', 'Concealer', 32.00, 4.7, 'Medium-to-full buildable coverage concealer with botanical peptides and vitamin C.', 'Dewy', 1),
('prod-cloud-blush', 'Soft Cloud Seamless Liquid Blush', 'Aura Beauty', 'Blush', 26.00, 4.9, 'Light-as-air gel-cream blush that melts into cheeks for a diffuse, healthy flush.', 'Satin', 0),
('prod-solar-bronze', 'Solar Radiance Baked Bronzer', 'Aura Beauty', 'Bronzer', 36.00, 4.8, 'Silky baked bronzer infused with golden micro-pearls for sun-kissed warmth.', 'Radiant', 0);

INSERT OR REPLACE INTO product_shades (id, product_id, sku, shade_name, hex_code, skin_tone, undertone, stock_quantity) VALUES
('sh-ls-10', 'prod-lum-silk', 'LS-10-COOL', '1.0 Fair Alabaster', '#FCE9DB', 'Fair', 'Cool', 150),
('sh-ls-20', 'prod-lum-silk', 'LS-20-WARM', '2.0 Light Porcelain', '#FADDC8', 'Light', 'Warm', 120),
('sh-ls-30', 'prod-lum-silk', 'LS-30-NEUT', '3.0 Light-Medium Bisque', '#EEC19D', 'Medium', 'Neutral', 200),
('sh-ls-40', 'prod-lum-silk', 'LS-40-WARM', '4.0 Medium Honey', '#D49B6A', 'Tan', 'Warm', 180),
('sh-ls-50', 'prod-lum-silk', 'LS-50-DEEP', '5.0 Deep Espresso', '#693E2B', 'Deep', 'Cool', 140),

('sh-vm-01', 'prod-vel-matte', 'VM-01-ROSE', 'Rose Cashmere', '#C76A75', 'Fair', 'Neutral', 100),
('sh-vm-02', 'prod-vel-matte', 'VM-02-RUBY', 'Royal Crimson', '#9B1B30', 'Medium', 'Cool', 110),
('sh-vm-03', 'prod-vel-matte', 'VM-03-NUDE', 'Warm Caramel Nude', '#B07559', 'Tan', 'Warm', 95),

('sh-hg-01', 'prod-hydra-glow', 'HG-01-FAIR', 'Fair 01 Neutral', '#FAE3D2', 'Fair', 'Neutral', 140),
('sh-hg-02', 'prod-hydra-glow', 'HG-02-MED', 'Medium 03 Warm', '#DEAA83', 'Medium', 'Warm', 130),
('sh-hg-03', 'prod-hydra-glow', 'HG-03-DEEP', 'Deep 05 Rich', '#73442C', 'Deep', 'Neutral', 110);

INSERT OR REPLACE INTO product_attributes (id, product_id, formulations, allergens, ingredients, mocra_disclosures, eu_compliance) VALUES
('attr-lum-silk', 'prod-lum-silk', '["vegan", "cruelty-free", "hypoallergenic", "non-comedogenic"]', '["fragrance-free", "paraben-free", "gluten-free"]', 'Aqua (Water), Dimethicone, Isododecane, Glycerin, PEG-10 Dimethicone, Niacinamide, Sodium Hyaluronate, Tocopherol, Phenoxyethanol, Ethylhexylglycerin.', '{"fda_facility_registration": "FEI-301829104", "responsible_person": "Aura Cosmetics USA LLC, New York NY", "adverse_event_contact": "safety@aurabeauty.com"}', '{"responsible_person_eu": "Aura Cosmetics Europe Ltd, Dublin IE", "cosing_registered": true, "cpr_reference": "CPNP-8492019"}'),

('attr-vel-matte', 'prod-vel-matte', '["vegan", "cruelty-free", "non-comedogenic"]', '["paraben-free", "gluten-free"]', 'Isododecane, Trimethylsiloxysilicate, Cyclopentasiloxane, Dimethicone, Synthetic Beeswax, Disteardimonium Hectorite, Ricinus Communis (Castor) Seed Oil, Red 7 Lake (CI 15850), Iron Oxides (CI 77491, CI 77499).', '{"fda_facility_registration": "FEI-301829104", "responsible_person": "Aura Cosmetics USA LLC, New York NY", "adverse_event_contact": "safety@aurabeauty.com"}', '{"responsible_person_eu": "Aura Cosmetics Europe Ltd, Dublin IE", "cosing_registered": true, "cpr_reference": "CPNP-8492020"}'),

('attr-hydra-glow', 'prod-hydra-glow', '["vegan", "cruelty-free", "hypoallergenic", "non-comedogenic"]', '["fragrance-free", "paraben-free", "nut-free"]', 'Water/Aqua, Caprylic/Capric Triglyceride, Mica, Polyglyceryl-3 Polyricinoleate, Squalane, Palmitoyl Tripeptide-5, Ascorbyl Glucoside, Sodium Chloride, Caprylyl Glycol.', '{"fda_facility_registration": "FEI-301829104", "responsible_person": "Aura Cosmetics USA LLC, New York NY", "adverse_event_contact": "safety@aurabeauty.com"}', '{"responsible_person_eu": "Aura Cosmetics Europe Ltd, Dublin IE", "cosing_registered": true, "cpr_reference": "CPNP-8492021"}');

INSERT OR REPLACE INTO promotions (id, code, description, discount_type, discount_value, min_spend, is_active) VALUES
('promo-glow10', 'GLOW10', '10% off entire order for new radiance seekers', 'percentage', 10.0, 30.0, 1),
('promo-beauty20', 'BEAUTY20', '20% off orders over $75', 'percentage', 20.0, 75.0, 1),
('promo-welcome5', 'WELCOME5', '$5 off any purchase', 'fixed', 5.0, 20.0, 1);

INSERT OR REPLACE INTO customers (id, email, full_name, phone, skin_tone_profile, undertone_profile) VALUES
('cust-guest-demo', 'guest@example.com', 'Emma Watson', '+1 (555) 019-2834', 'Medium', 'Warm');

INSERT OR REPLACE INTO orders (id, order_number, customer_id, customer_email, is_guest, total_amount, discount_amount, promo_code, payment_method, payment_status, tracking_carrier, tracking_number, status, shipping_address) VALUES
('ord-1001', 'ORD-98214-AUR', 'cust-guest-demo', 'guest@example.com', 0, 76.00, 0.0, NULL, 'Apple Pay', 'succeeded', 'FedEx Express', 'FDX-7482918234-US', 'delivered', '{"name": "Emma Watson", "street": "742 Evergreen Terrace", "city": "Springfield", "state": "OR", "zip": "97477", "country": "USA"}');

INSERT OR REPLACE INTO order_items (id, order_id, sku, product_name, shade_name, quantity, unit_price, subtotal) VALUES
('oi-1001-1', 'ord-1001', 'LS-30-NEUT', 'Luminous Silk Flawless Foundation', '3.0 Light-Medium Bisque', 1, 48.00, 48.00),
('oi-1001-2', 'ord-1001', 'VM-01-ROSE', 'Velvet Matte Liquid Lip Color', 'Rose Cashmere', 1, 28.00, 28.00);

INSERT OR REPLACE INTO tracking_events (id, order_id, tracking_number, status, location, description, timestamp) VALUES
('te-1', 'ord-1001', 'FDX-7482918234-US', 'Order Placed', 'Aura Fulfillment Center, Louisville KY', 'Shipment order data received', '2026-10-21 08:30:00'),
('te-2', 'ord-1001', 'FDX-7482918234-US', 'In Transit', 'FedEx Sorting Hub, Indianapolis IN', 'Package scanned and in transit', '2026-10-21 14:15:00'),
('te-3', 'ord-1001', 'FDX-7482918234-US', 'Out for Delivery', 'Local Distribution Hub, Eugene OR', 'On vehicle for delivery', '2026-10-22 09:00:00'),
('te-4', 'ord-1001', 'FDX-7482918234-US', 'Delivered', 'Front Porch, Springfield OR', 'Delivered to resident', '2026-10-22 13:45:00');
