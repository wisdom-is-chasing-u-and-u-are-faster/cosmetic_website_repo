// tests/promotions.test.ts
// Promo Engine & Bundle Discount Tests [ARCH-5134-AC11]

import request from 'supertest';
import { createApp } from '../src/app';
import { resetDatabaseForTesting } from '../src/db/database';

describe('Promotions Engine API', () => {
  let app: ReturnType<typeof createApp>;

  beforeEach(() => {
    resetDatabaseForTesting();
    app = createApp();
  });

  test('[ARCH-5134-AC11] Percentage discount coupon (BEAUTY20) calculates discount correctly', async () => {
    const res = await request(app).post('/api/v1/promotions/apply').send({
      code: 'BEAUTY20',
      cart_total: 100.0,
      items: [{ product_id: 'PROD-FND-001', quantity: 2 }]
    });

    expect(res.status).toBe(200);
    expect(res.body.valid).toBe(true);
    expect(res.body.discount_amount).toBe(20.0);
    expect(res.body.final_total).toBe(80.0);
  });

  test('[ARCH-5134-AC11] Shade bundle promo (SHADEBUNDLE) applies discount when >= 2 items in cart', async () => {
    const res = await request(app).post('/api/v1/promotions/apply').send({
      code: 'SHADEBUNDLE',
      cart_total: 80.0,
      items: [
        { product_id: 'PROD-FND-001', quantity: 1 },
        { product_id: 'PROD-CON-001', quantity: 1 }
      ]
    });

    expect(res.status).toBe(200);
    expect(res.body.valid).toBe(true);
    expect(res.body.discount_amount).toBe(12.0); // 15% of 80 = 12
    expect(res.body.final_total).toBe(68.0);
  });

  test('Invalid promo code returns 400 Bad Request Problem Details', async () => {
    const res = await request(app).post('/api/v1/promotions/apply').send({
      code: 'INVALIDCODE',
      cart_total: 100.0
    });

    expect(res.status).toBe(400);
    expect(res.body.title).toBe('Bad Request');
  });
});
