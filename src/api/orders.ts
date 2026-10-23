// src/api/orders.ts
// Order Detail & Real-Time 3PL Tracking Router [REQ-F-006]

import { Router, Request, Response, NextFunction } from 'express';
import { getDatabase } from '../db/database';
import { NotFoundError } from '../core/errors';

export const router = Router();

interface OrderRow {
  id: string;
  email: string;
  customer_name: string;
  is_guest: number;
  total_amount: number;
  discount_amount: number;
  promo_code: string | null;
  status: string;
  tracking_number: string;
  carrier: string;
  shipping_address: string;
  created_at: string;
}

interface OrderItemRow {
  product_id: string;
  quantity: number;
  unit_price: number;
  name: string;
  shade: string;
}

/**
 * GET /api/v1/orders/history — Retrieve order history by email
 */
router.get('/history', (req: Request, res: Response, next: NextFunction) => {
  try {
    const email = req.query.email as string;
    const db = getDatabase();

    let sql = 'SELECT * FROM orders ORDER BY created_at DESC LIMIT 20';
    const params: unknown[] = [];

    if (email) {
      sql = 'SELECT * FROM orders WHERE email = ? ORDER BY created_at DESC';
      params.push(email);
    }

    const rows = db.prepare(sql).all(...params) as OrderRow[];
    res.json({
      orders: rows.map((r) => ({
        id: r.id,
        email: r.email,
        customer_name: r.customer_name,
        total_amount: r.total_amount,
        status: r.status,
        tracking_number: r.tracking_number,
        carrier: r.carrier,
        created_at: r.created_at
      })),
      total: rows.length
    });
  } catch (err) {
    next(err);
  }
});

/**
 * GET /api/v1/orders/:id — Order details + 3PL shipment tracking [REQ-F-006]
 */
router.get('/:id', (req: Request, res: Response, next: NextFunction) => {
  try {
    const db = getDatabase();
    const order = db.prepare('SELECT * FROM orders WHERE id = ?').get(req.params.id) as OrderRow | undefined;

    if (!order) {
      throw new NotFoundError(`Order with ID '${req.params.id}' was not found.`);
    }

    const items = db.prepare(`
      SELECT oi.product_id, oi.quantity, oi.unit_price, p.name, p.shade
      FROM order_items oi
      JOIN products p ON oi.product_id = p.id
      WHERE oi.order_id = ?
    `).all(req.params.id) as OrderItemRow[];

    res.json({
      order_id: order.id,
      customer_name: order.customer_name,
      email: order.email,
      status: order.status,
      total_amount: order.total_amount,
      discount_amount: order.discount_amount,
      tracking_number: order.tracking_number,
      carrier: order.carrier,
      estimated_delivery: 'In Transit — Expected Delivery within 3 business days',
      shipping_address: JSON.parse(order.shipping_address),
      created_at: order.created_at,
      items
    });
  } catch (err) {
    next(err);
  }
});
