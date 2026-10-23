// tests/returns.test.ts
// Customer Returns & Automated Shade Exchange Tests [ARCH-5134-AC8]

import request from 'supertest';
import { createApp } from '../src/app';
import { resetDatabaseForTesting } from '../src/db/database';

describe('Returns and Shade Exchange API', () => {
  let app: ReturnType<typeof createApp>;
  let orderId: string;

  beforeEach(async () => {
    resetDatabaseForTesting();
    app = createApp();

    const res = await request(app).post('/api/v1/checkout/process').send({
      email: 'customer@aura.com',
      shipping_address: {
        full_name: 'Aura Fan',
        address_line1: '789 Glow Rd',
        city: 'Miami',
        state: 'FL',
        postal_code: '33101',
        country: 'US'
      },
      payment_method: 'card',
      items: [{ product_id: 'PROD-FND-001', quantity: 1, price: 48.0 }]
    });
    orderId = res.body.order_id;
  });

  test('Automated Shade Exchange flow creates exchange order and prepaid label', async () => {
    const res = await request(app).post('/api/v1/returns').send({
      order_id: orderId,
      product_id: 'PROD-FND-001',
      target_shade_id: 'PROD-FND-002',
      type: 'SHADE_EXCHANGE',
      reason: 'Shade too warm, exchanging for Cool Porcelain.'
    });

    expect(res.status).toBe(201);
    expect(res.body.return_id).toBeDefined();
    expect(res.body.status).toBe('APPROVED');
    expect(res.body.exchange_order_id).toBeDefined();
    expect(res.body.prepaid_label_url).toBeDefined();
  });

  test('Standard return request creates return record and prepaid label', async () => {
    const res = await request(app).post('/api/v1/returns').send({
      order_id: orderId,
      product_id: 'PROD-FND-001',
      type: 'RETURN',
      reason: 'Item no longer needed.'
    });

    expect(res.status).toBe(201);
    expect(res.body.status).toBe('APPROVED');
    expect(res.body.prepaid_label_url).toBeDefined();
  });
});
