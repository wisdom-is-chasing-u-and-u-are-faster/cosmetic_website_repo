// tests/webhooks.test.ts
// Inbound 3PL Logistics Webhook Tests [ARCH-5134-AC6]

import request from 'supertest';
import { createApp } from '../src/app';
import { resetDatabaseForTesting, getDatabase } from '../src/db/database';
import { generateHmacSignature } from '../src/core/security';

describe('3PL Logistics Webhook API', () => {
  let app: ReturnType<typeof createApp>;
  let orderId: string;

  beforeEach(async () => {
    resetDatabaseForTesting();
    app = createApp();

    const res = await request(app).post('/api/v1/checkout/process').send({
      email: 'tracking.user@example.com',
      shipping_address: {
        full_name: 'Tracking User',
        address_line1: '123 Logistics St',
        city: 'Chicago',
        state: 'IL',
        postal_code: '60601',
        country: 'US'
      },
      payment_method: 'card',
      items: [{ product_id: 'PROD-FND-001', quantity: 1, price: 48.0 }]
    });
    orderId = res.body.order_id;
  });

  test('[ARCH-5134-AC6] Valid signed webhook updates order status to SHIPPED', async () => {
    const payload = {
      event: 'shipment.dispatched',
      order_id: orderId,
      tracking_number: 'FEDEX-99887766',
      carrier: 'FedEx Priority',
      status: 'SHIPPED'
    };

    const rawPayload = JSON.stringify(payload);
    const signature = generateHmacSignature(rawPayload, process.env.WEBHOOK_3PL_HMAC_SECRET || 'secret-webhook-key-3pl');

    const res = await request(app)
      .post('/api/v1/webhooks/3pl')
      .set('X-3PL-Signature', `sha256=${signature}`)
      .set('Content-Type', 'application/json')
      .send(payload);

    expect(res.status).toBe(200);
    expect(res.body.received).toBe(true);

    // Verify order was updated in DB
    const db = getDatabase();
    const order = db.prepare('SELECT * FROM orders WHERE id = ?').get(orderId) as { status: string; tracking_number: string };
    expect(order.status).toBe('SHIPPED');
    expect(order.tracking_number).toBe('FEDEX-99887766');
  });

  test('Webhook rejected with 401 when signature is invalid or missing', async () => {
    const payload = {
      event: 'shipment.dispatched',
      order_id: orderId,
      status: 'SHIPPED'
    };

    const res = await request(app)
      .post('/api/v1/webhooks/3pl')
      .set('X-3PL-Signature', 'sha256=invalid-signature-hex')
      .send(payload);

    expect(res.status).toBe(401);
    expect(res.body.title).toBe('Unauthorized');
  });
});
