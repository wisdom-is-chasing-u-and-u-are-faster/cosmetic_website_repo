// src/api/promotions.ts
// Promo Engine & Shade Bundle Discount Router [REQ-F-005, REQ-F-015]

import { Router, Request, Response, NextFunction } from 'express';
import { getDatabase } from '../db/database';
import { BadRequestError } from '../core/errors';

export const router = Router();

interface PromotionRow {
  code: string;
  description: string;
  discount_type: 'PERCENTAGE' | 'FIXED_AMOUNT' | 'SHADE_BUNDLE';
  discount_value: number;
  minimum_cart_value: number;
  is_active: number;
}

/**
 * POST /api/v1/promotions/apply — Apply promo code or shade bundle
 */
router.post('/apply', (req: Request, res: Response, next: NextFunction) => {
  try {
    const { code, cart_total, items } = req.body;

    if (!code) {
      throw new BadRequestError('Promo code is required.');
    }

    const currentTotal = Number(cart_total) || 0;
    const db = getDatabase();
    const promo = db.prepare('SELECT * FROM promotions WHERE code = ? AND is_active = 1').get(code.toUpperCase()) as PromotionRow | undefined;

    if (!promo) {
      throw new BadRequestError(`Invalid or expired promo code: '${code}'`);
    }

    if (currentTotal < promo.minimum_cart_value) {
      throw new BadRequestError(
        `Promo code '${code}' requires a minimum cart total of $${promo.minimum_cart_value.toFixed(2)}.`
      );
    }

    let discount = 0;
    if (promo.discount_type === 'PERCENTAGE') {
      discount = (currentTotal * promo.discount_value) / 100.0;
    } else if (promo.discount_type === 'FIXED_AMOUNT') {
      discount = Math.min(promo.discount_value, currentTotal);
    } else if (promo.discount_type === 'SHADE_BUNDLE') {
      // Check if at least 2 items in cart
      const totalItemCount = Array.isArray(items) ? items.reduce((acc: number, item: { quantity?: number }) => acc + (item.quantity || 1), 0) : 0;
      if (totalItemCount >= 2) {
        discount = (currentTotal * promo.discount_value) / 100.0;
      } else {
        throw new BadRequestError('Shade Bundle promotion requires at least 2 matching items in cart.');
      }
    }

    discount = Math.round(discount * 100) / 100;
    const finalTotal = Math.max(0, Math.round((currentTotal - discount) * 100) / 100);

    res.json({
      valid: true,
      code: promo.code,
      description: promo.description,
      discount_amount: discount,
      final_total: finalTotal
    });
  } catch (err) {
    next(err);
  }
});
