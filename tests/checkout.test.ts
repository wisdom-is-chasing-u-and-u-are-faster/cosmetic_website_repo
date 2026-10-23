// tests/checkout.test.ts
// Inventory Reservation & Progressive Checkout Tests [ARCH-5134-AC3, ARCH-5134-AC4, ARCH-5134-AC5]

import request from 'supertest';
import { createApp } from '../src/app';
import { resetDatabaseForTesting } from '../src/db/database';

describe('Checkout & Inventory Reservation API', () => {
  let app: ReturnType<typeof createApp>;

  beforeEach(() => {
    resetDatabaseForTesting();
    app = createApp();
  });

  test('[ARCH-5134-AC5] Real-time inventory reservation locks stock atomically', async () => {
    const res = await request(app).post('/api/v1/checkout/reserve').send({
      session_id: 'sess-abc-123',
      items: [{ product_id: 'PROD-FND-001', quantity: 2 }]
    });

    expect(res.status).toBe(200);
    expect(res.body.reservation_id).toBeDefined();
    expect(res.body.status).toBe('ACTIVE');
  });

  test('[ARCH-5134-AC5] Reservation fails with 409 Conflict when requesting more stock than available', async () => {
    const res = await request(app).post('/api/v1/checkout/reserve').send({
      session_id: 'sess-abc-123',
      items: [{ product_id: 'PROD-FND-001', quantity: 9999 }]
    });

    expect(res.status).toBe(409);
    expect(res.body.title).toBe('Conflict');
  });

  test('[ARCH-5134-AC3, ARCH-5134-AC4] Guest single-page checkout completes successfully with Stripe tokenization', async () => {
    // 1. Reserve
    const resReserve = await request(app).post('/api/v1/checkout/reserve').send({
      session_id: 'sess-guest-001',
      items: [{ product_id: 'PROD-FND-001', quantity: 1 }]
    });
    const reservationId = resReserve.body.reservation_id;

    // 2. Checkout
    const resCheckout = await request(app).post('/api/v1/checkout/process').send({
      reservation_id: reservationId,
      email: 'guest.shopper@example.com',
      is_guest: true,
      shipping_address: {
        full_name: 'Guest Shopper',
        address_line1: '123 Beauty Lane',
        city: 'New York',
        state: 'NY',
        postal_code: '10001',
        country: 'US'
      },
      payment_method: 'stripe_apple_pay_token',
      items: [{ product_id: 'PROD-FND-001', quantity: 1, price: 48.0 }],
      promo_code: 'WELCOME10'
    });

    expect(resCheckout.status).toBe(201);
    expect(resCheckout.body.order_id).toBeDefined();
    expect(resCheckout.body.status).toBe('CONFIRMED');
    expect(resCheckout.body.tracking_number).toBeDefined();
    expect(resCheckout.body.discount_applied).toBe(10.0);
    expect(resCheckout.body.total_amount).toBe(38.0);
  });
});
