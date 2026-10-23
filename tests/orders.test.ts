// tests/orders.test.ts
// Order Status & 3PL Logistics Tracking Tests [ARCH-5134-AC6]

import request from 'supertest';
import { createApp } from '../src/app';
import { resetDatabaseForTesting } from '../src/db/database';

describe('Orders and 3PL Tracking API', () => {
  let app: ReturnType<typeof createApp>;

  beforeEach(() => {
    resetDatabaseForTesting();
    app = createApp();
  });

  test('[ARCH-5134-AC6] Order details and real-time tracking retrieval', async () => {
    // 1. Create order
    const resCheckout = await request(app).post('/api/v1/checkout/process').send({
      email: 'jane.doe@example.com',
      shipping_address: {
        full_name: 'Jane Doe',
        address_line1: '456 Glam St',
        city: 'Los Angeles',
        state: 'CA',
        postal_code: '90001',
        country: 'US'
      },
      payment_method: 'stripe_google_pay',
      items: [{ product_id: 'PROD-LIP-001', quantity: 1, price: 32.0 }]
    });

    const orderId = resCheckout.body.order_id;

    // 2. Fetch order
    const resOrder = await request(app).get(`/api/v1/orders/${orderId}`);
    expect(resOrder.status).toBe(200);
    expect(resOrder.body.order_id).toBe(orderId);
    expect(resOrder.body.tracking_number).toBeDefined();
    expect(resOrder.body.carrier).toBeDefined();
    expect(resOrder.body.items).toHaveLength(1);
  });

  test('Order history lookup by email', async () => {
    const resHistory = await request(app).get('/api/v1/orders/history?email=jane.doe@example.com');
    expect(resHistory.status).toBe(200);
    expect(Array.isArray(resHistory.body.orders)).toBe(true);
  });
});
