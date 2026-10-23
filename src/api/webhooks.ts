// src/api/webhooks.ts
// Inbound 3PL Logistics Webhook Dispatcher [REQ-F-010]

import { Router, Request, Response, NextFunction } from 'express';
import { getDatabase } from '../db/database';
import { UnauthorizedError, BadRequestError } from '../core/errors';
import { verifyHmacSignature } from '../core/security';

export const router = Router();

/**
 * POST /api/v1/webhooks/3pl — Inbound 3PL logistics tracking update
 */
router.post('/3pl', (req: Request, res: Response, next: NextFunction) => {
  try {
    const signatureHeader = req.header('X-3PL-Signature') || req.header('x-3pl-signature');
    const rawPayload = JSON.stringify(req.body);

    // Verify HMAC signature
    if (!verifyHmacSignature(rawPayload, signatureHeader)) {
      throw new UnauthorizedError('Invalid or missing X-3PL-Signature header.');
    }

    const { event, order_id, tracking_number, status, carrier } = req.body;

    if (!order_id || !status) {
      throw new BadRequestError('Missing required webhook fields (order_id, status).');
    }

    const db = getDatabase();
    const result = db.prepare(`
      UPDATE orders
      SET status = ?, tracking_number = COALESCE(?, tracking_number), carrier = COALESCE(?, carrier)
      WHERE id = ?
    `).run(status.toUpperCase(), trackingNumberOrNull(tracking_number), carrier || null, order_id);

    db.prepare(`
      INSERT INTO audit_logs (event_type, entity_id, details)
      VALUES (?, ?, ?)
    `).run('3PL_WEBHOOK_PROCESSED', order_id, `Event: ${event || 'status_update'}, New Status: ${status}`);

    res.json({
      received: true,
      order_id,
      updated: result.changes > 0,
      timestamp: new Date().toISOString()
    });
  } catch (err) {
    next(err);
  }
});

function trackingNumberOrNull(val: unknown): string | null {
  return typeof val === 'string' && val.trim() ? val.trim() : null;
}
