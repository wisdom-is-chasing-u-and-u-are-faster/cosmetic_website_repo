// tests/products.test.ts
// Product Catalog, Faceted Search & MoCRA/EU Compliance Tests [ARCH-5134-AC2, ARCH-5134-AC7]

import request from 'supertest';
import { createApp } from '../src/app';
import { resetDatabaseForTesting } from '../src/db/database';

describe('Product Catalog & Faceted Search Endpoints', () => {
  let app: ReturnType<typeof createApp>;

  beforeEach(() => {
    resetDatabaseForTesting();
    app = createApp();
  });

  test('[ARCH-5134-AC2] Faceted search filters products by finish and undertone', async () => {
    const res = await request(app).get('/api/v1/products?finish=Dewy');
    expect(res.status).toBe(200);
    expect(res.body.products.length).toBeGreaterThan(0);
    expect(res.body.products[0].finish).toBe('Dewy');
  });

  test('[ARCH-5134-AC2] Search filters by keyword and category', async () => {
    const res = await request(app).get('/api/v1/products?category=lipstick');
    expect(res.status).toBe(200);
    expect(res.body.products.length).toBe(1);
    expect(res.body.products[0].category).toBe('lipstick');
  });

  test('[ARCH-5134-AC7] Product detail endpoint returns FDA MoCRA and EU compliance disclosures', async () => {
    const res = await request(app).get('/api/v1/products/PROD-FND-001');
    expect(res.status).toBe(200);
    expect(res.body.id).toBe('PROD-FND-001');
    expect(res.body.fda_mocra_listed).toBe(true);
    expect(res.body.eu_1223_2009_compliant).toBe(true);
    expect(res.body.ingredients).toBeDefined();
    expect(res.body.ingredients).toContain('Titanium Dioxide');
  });

  test('Non-existent product returns 404 Problem Details', async () => {
    const res = await request(app).get('/api/v1/products/PROD-DOES-NOT-EXIST');
    expect(res.status).toBe(404);
    expect(res.body.title).toBe('Resource Not Found');
  });
});
