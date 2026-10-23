// src/api/account.ts
// Account Management and GDPR/CCPA PII Erasure Router [REQ-F-012]

import { Router, Request, Response, NextFunction } from 'express';
import { getDatabase } from '../db/database';
import { BadRequestError } from '../core/errors';
import { anonymizePiiString } from '../core/security';

export const router = Router();

/**
 * POST /api/v1/account/pii-erasure — GDPR/CCPA PII Erasure [REQ-F-012]
 */
router.post('/pii-erasure', (req: Request, res: Response, next: NextFunction) => {
  try {
    const { email } = req.body;

    if (!email) {
      throw new BadRequestError('Email address is required for PII erasure processing.');
    }

    const db = getDatabase();
    const anonymizedEmail = anonymizePiiString(email);
    const anonymizedName = anonymizePiiString('Customer');

    const result = db.prepare(`
      UPDATE orders
      SET email = ?, customer_name = ?, shipping_address = '{"redacted": true}'
      WHERE email = ?
    `).run(anonymizedEmail, anonymizedName, email);

    // Record audit event
    db.prepare(`
      INSERT INTO audit_logs (event_type, entity_id, details)
      VALUES (?, ?, ?)
    `).run('GDPR_PII_ERASURE', anonymizedEmail, `Erased PII records for ${result.changes} associated order(s).`);

    res.json({
      status: 'ERASED',
      message: `PII successfully anonymized for ${result.changes} records in compliance with GDPR/CCPA.`,
      anonymized_identifier: anonymizedEmail,
      records_updated: result.changes,
      timestamp: new Date().toISOString()
    });
  } catch (err) {
    next(err);
  }
});
