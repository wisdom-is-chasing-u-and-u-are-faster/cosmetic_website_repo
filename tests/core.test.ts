// tests/core.test.ts
// Unit Tests for Core RFC-7807 Errors, Idempotency, and Security [ARCH-5134-AC9, ARCH-5134-AC10]

import express from 'express';
import request from 'supertest';
import { AppError, BadRequestError, NotFoundError, errorHandler } from '../src/core/errors';
import { idempotencyMiddleware } from '../src/core/idempotency';
import { generateHmacSignature, verifyHmacSignature, anonymizePiiString } from '../src/core/security';
import { resetDatabaseForTesting } from '../src/db/database';

describe('Core Infrastructure & RFC-7807 Compliance', () => {
  beforeEach(() => {
    resetDatabaseForTesting();
  });

  test('[ARCH-5134-AC10] RFC-7807 Error formatting for BadRequest and NotFound', async () => {
    const app = express();
    app.use(express.json());

    app.get('/test-bad-request', () => {
      throw new BadRequestError('Invalid input field', [{ name: 'email', reason: 'Must be a valid email' }]);
    });

    app.get('/test-not-found', () => {
      throw new NotFoundError('Item not found');
    });

    app.use(errorHandler);

    const resBad = await request(app).get('/test-bad-request');
    expect(resBad.status).toBe(400);
    expect(resBad.header['content-type']).toContain('application/problem+json');
    expect(resBad.body.title).toBe('Bad Request');
    expect(resBad.body.detail).toBe('Invalid input field');
    expect(resBad.body.invalid_params).toHaveLength(1);

    const resNotFound = await request(app).get('/test-not-found');
    expect(resNotFound.status).toBe(404);
    expect(resNotFound.body.title).toBe('Resource Not Found');
  });

  test('[ARCH-5134-AC9] Idempotency key middleware prevents duplicate executions', async () => {
    const app = express();
    app.use(express.json());
    app.use(idempotencyMiddleware);

    let counter = 0;
    app.post('/test-mutate', (req, res) => {
      counter += 1;
      res.status(201).json({ count: counter, message: 'Created' });
    });

    const key = 'test-idemp-key-123';

    // First Call
    const res1 = await request(app).post('/test-mutate').set('Idempotency-Key', key).send({ item: 'lipstick' });
    expect(res1.status).toBe(201);
    expect(res1.body.count).toBe(1);

    // Duplicate Call with same key
    const res2 = await request(app).post('/test-mutate').set('Idempotency-Key', key).send({ item: 'lipstick' });
    expect(res2.status).toBe(201);
    expect(res2.body.count).toBe(1); // Cached response returned
    expect(counter).toBe(1); // Counter did not increment
  });

  test('HMAC verification and PII anonymization helpers work correctly', () => {
    const payload = JSON.stringify({ event: 'test', order_id: 'ORD-1' });
    const dummyKey = 'mock-test-key-3pl';
    const sig = generateHmacSignature(payload, dummyKey);

    expect(verifyHmacSignature(payload, sig, dummyKey)).toBe(true);
    expect(verifyHmacSignature(payload, 'wrong-sig', dummyKey)).toBe(false);

    const anonEmail = anonymizePiiString('customer@example.com');
    expect(anonEmail).toContain('@redacted.local');
    expect(anonEmail).not.toContain('customer');
  });
});
