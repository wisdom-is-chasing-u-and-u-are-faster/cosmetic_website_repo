// src/core/idempotency.ts
// Idempotency Middleware for Mutating Endpoints [REQ-F-013]

import { Request, Response, NextFunction } from 'express';
import { getDatabase } from '../db/database';

export function idempotencyMiddleware(req: Request, res: Response, next: NextFunction): void {
  const idempotencyKey = req.header('Idempotency-Key') || req.header('idempotency-key');

  if (!idempotencyKey || req.method === 'GET' || req.method === 'HEAD' || req.method === 'OPTIONS') {
    return next();
  }

  const db = getDatabase();
  const existing = db.prepare('SELECT response_code, response_body FROM idempotency_keys WHERE key = ?').get(idempotencyKey) as { response_code: number; response_body: string } | undefined;

  if (existing) {
    try {
      const parsedBody = JSON.parse(existing.response_body);
      res.setHeader('X-Cache-Lookup', 'HIT-IDEMPOTENCY');
      res.status(existing.response_code).json(parsedBody);
      return;
    } catch {
      res.status(existing.response_code).send(existing.response_body);
      return;
    }
  }

  // Intercept response to store result
  const originalJson = res.json.bind(res);
  res.json = (body: unknown): Response => {
    try {
      const stringified = JSON.stringify(body);
      db.prepare('INSERT OR REPLACE INTO idempotency_keys (key, request_path, response_code, response_body) VALUES (?, ?, ?, ?)').run(
        idempotencyKey,
        req.originalUrl,
        res.statusCode,
        stringified
      );
    } catch (e) {
      console.error('Failed to store idempotency record:', e);
    }
    return originalJson(body);
  };

  next();
}
