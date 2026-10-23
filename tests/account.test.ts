// tests/account.test.ts
// Account Management & GDPR/CCPA PII Erasure Tests [ARCH-5134-AC8]

import request from 'supertest';
import { createApp } from '../src/app';
import { resetDatabaseForTesting, getDatabase } from '../src/db/database';

describe('Account & PII Erasure API', () => {
  let app: ReturnType<typeof createApp>;

  beforeEach(() => {
    resetDatabaseForTesting();
    app = createApp();
  });

  test('[ARCH-5134-AC8] PII Erasure endpoint anonymizes user orders and logs audit event', async () => {
    const userEmail = 'privacy.user@domain.com';

    // 1. Create an order with PII
    await request(app).post('/api/v1/checkout/process').send({
      email: userEmail,
      shipping_address: {
        full_name: 'Privacy User',
        address_line1: '100 Secret Ave',
        city: 'Austin',
        state: 'TX',
        postal_code: '78701',
        country: 'US'
      },
      payment_method: 'card',
      items: [{ product_id: 'PROD-CON-001', quantity: 1, price: 28.0 }]
    });

    // 2. Request PII Erasure
    const resErasure = await request(app).post('/api/v1/account/pii-erasure').send({
      email: userEmail
    });

    expect(resErasure.status).toBe(200);
    expect(resErasure.body.status).toBe('ERASED');
    expect(resErasure.body.records_updated).toBeGreaterThanOrEqual(1);

    // 3. Verify in database that email and address are anonymized
    const db = getDatabase();
    const order = db.prepare("SELECT * FROM orders WHERE id LIKE 'ORD-%'").get() as { email: string; customer_name: string; shipping_address: string };

    expect(order.email).not.toBe(userEmail);
    expect(order.email).toContain('@redacted.local');
    expect(order.shipping_address).toContain('redacted');
  });
});
