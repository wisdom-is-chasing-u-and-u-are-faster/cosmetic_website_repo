// tests/e2e.test.ts
// End-to-End Customer Purchase Journey [ARCH-5134-AC1, ARCH-5134-AC3, ARCH-5134-AC5, ARCH-5134-AC6]

import request from 'supertest';
import { createApp } from '../src/app';
import { resetDatabaseForTesting } from '../src/db/database';
import { generateHmacSignature } from '../src/core/security';

describe('E2E Customer Journey (Discovery -> Reserve -> Promo -> Checkout -> Tracking -> Return)', () => {
  let app: ReturnType<typeof createApp>;

  beforeEach(() => {
    resetDatabaseForTesting();
    app = createApp();
  });

  test('Complete E2E Commerce Flow', async () => {
    // 1. Discovery / Faceted search
    const plpRes = await request(app).get('/api/v1/products?category=foundation&finish=Dewy');
    expect(plpRes.status).toBe(200);
    const product = plpRes.body.products[0];
    expect(product).toBeDefined();

    // 2. Reserve stock (2 units = $96.00)
    const reserveRes = await request(app).post('/api/v1/checkout/reserve').send({
      session_id: 'e2e-session-888',
      items: [{ product_id: product.id, quantity: 2 }]
    });
    expect(reserveRes.status).toBe(200);
    const reservationId = reserveRes.body.reservation_id;

    // 3. Apply Promo Code (BEAUTY20 requires min $50)
    const promoRes = await request(app).post('/api/v1/promotions/apply').send({
      code: 'BEAUTY20',
      cart_total: product.price * 2,
      items: [{ product_id: product.id, quantity: 2 }]
    });
    expect(promoRes.status).toBe(200);
    expect(promoRes.body.valid).toBe(true);
    expect(promoRes.body.discount_amount).toBe(19.2);

    // 4. Checkout
    const checkoutRes = await request(app).post('/api/v1/checkout/process').send({
      reservation_id: reservationId,
      email: 'e2e.shopper@aura.com',
      shipping_address: {
        full_name: 'E2E Shopper',
        address_line1: '999 Beauty Blvd',
        city: 'Seattle',
        state: 'WA',
        postal_code: '98101',
        country: 'US'
      },
      payment_method: 'stripe_token_card',
      items: [{ product_id: product.id, quantity: 2, price: product.price }],
      promo_code: 'BEAUTY20'
    });
    expect(checkoutRes.status).toBe(201);
    const orderId = checkoutRes.body.order_id;

    // 5. 3PL Shipment Webhook
    const webhookPayload = {
      event: 'carrier.package_delivered',
      order_id: orderId,
      tracking_number: 'DELIV-3PL-77',
      carrier: 'FedEx Expedited',
      status: 'DELIVERED'
    };
    const rawPayload = JSON.stringify(webhookPayload);
    const signature = generateHmacSignature(rawPayload, process.env.WEBHOOK_3PL_HMAC_SECRET || 'secret-webhook-key-3pl');

    const webhookRes = await request(app)
      .post('/api/v1/webhooks/3pl')
      .set('X-3PL-Signature', `sha256=${signature}`)
      .send(webhookPayload);
    expect(webhookRes.status).toBe(200);

    // 6. Verify order status
    const orderRes = await request(app).get(`/api/v1/orders/${orderId}`);
    expect(orderRes.status).toBe(200);
    expect(orderRes.body.status).toBe('DELIVERED');

    // 7. Request Return
    const returnRes = await request(app).post('/api/v1/returns').send({
      order_id: orderId,
      product_id: product.id,
      type: 'RETURN',
      reason: 'Color slightly different from expectation'
    });
    expect(returnRes.status).toBe(201);
    expect(returnRes.body.status).toBe('APPROVED');
  });
});
