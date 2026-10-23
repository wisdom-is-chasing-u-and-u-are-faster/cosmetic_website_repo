// src/api/returns.ts
// Customer Returns & Automated Shade Exchange Router [REQ-F-007, REQ-F-008]

import { Router, Request, Response, NextFunction } from 'express';
import crypto from 'crypto';
import { getDatabase } from '../db/database';
import { BadRequestError, NotFoundError } from '../core/errors';

export const router = Router();

/**
 * POST /api/v1/returns — Submit customer return or shade exchange
 */
router.post('/', (req: Request, res: Response, next: NextFunction) => {
  try {
    const { order_id, product_id, target_shade_id, type, reason } = req.body;

    if (!order_id || !product_id || !reason) {
      throw new BadRequestError('order_id, product_id, and reason are required.');
    }

    const returnType = type === 'SHADE_EXCHANGE' ? 'SHADE_EXCHANGE' : 'RETURN';
    const db = getDatabase();

    // Verify order exists
    const order = db.prepare('SELECT * FROM orders WHERE id = ?').get(order_id);
    if (!order) {
      throw new NotFoundError(`Order '${order_id}' not found.`);
    }

    const returnId = `RET-${crypto.randomBytes(4).toString('hex').toUpperCase()}`;
    const prepaidLabel = `https://shipping.cosmetics.example/labels/${returnId}.pdf`;
    let exchangeOrderId: string | null = null;

    if (returnType === 'SHADE_EXCHANGE') {
      exchangeOrderId = `EXC-${crypto.randomBytes(3).toString('hex').toUpperCase()}`;
    }

    db.prepare(`
      INSERT INTO returns (return_id, order_id, product_id, target_shade_id, type, status, reason, prepaid_label_url, exchange_order_id)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    `).run(
      returnId,
      order_id,
      product_id,
      target_shade_id || null,
      returnType,
      'APPROVED',
      reason,
      prepaidLabel,
      exchangeOrderId
    );

    res.status(201).json({
      return_id: returnId,
      order_id,
      type: returnType,
      status: 'APPROVED',
      message: returnType === 'SHADE_EXCHANGE' ? 'Shade exchange approved. Replacement unit ordered.' : 'Return request approved.',
      prepaid_label_url: prepaidLabel,
      exchange_order_id: exchangeOrderId
    });
  } catch (err) {
    next(err);
  }
});
