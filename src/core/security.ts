// src/core/security.ts
// Security Utilities: HMAC-SHA256 Webhook Verification & PII Anonymization

import crypto from 'crypto';

const HMAC_SECRET = process.env.WEBHOOK_3PL_HMAC_SECRET || 'secret-webhook-key-3pl';

/**
 * Generate HMAC-SHA256 signature for payload
 */
export function generateHmacSignature(payload: string | Buffer, secret: string = HMAC_SECRET): string {
  return crypto.createHmac('sha256', secret).update(payload).digest('hex');
}

/**
 * Verify inbound webhook signature using timing-safe comparison [REQ-F-010]
 */
export function verifyHmacSignature(
  rawBody: string | Buffer,
  signatureHeader?: string,
  secret: string = HMAC_SECRET
): boolean {
  if (!signatureHeader) {
    return false;
  }
  const cleanSig = signatureHeader.replace(/^sha256=/, '').trim();
  const expectedSig = generateHmacSignature(rawBody, secret);

  try {
    const cleanBuffer = Buffer.from(cleanSig, 'hex');
    const expectedBuffer = Buffer.from(expectedSig, 'hex');
    if (cleanBuffer.length !== expectedBuffer.length) {
      return false;
    }
    return crypto.timingSafeEqual(cleanBuffer, expectedBuffer);
  } catch {
    return false;
  }
}

/**
 * Deterministically anonymize PII values (emails/names) for GDPR/CCPA erasure [REQ-F-012]
 */
export function anonymizePiiString(value: string): string {
  if (!value) {
    return '[ANONYMIZED]';
  }
  const salt = 'pii-erasure-salt';
  const hash = crypto.createHash('sha256').update(`${value}:${salt}`).digest('hex').substring(0, 12);
  return value.includes('@') ? `anon_${hash}@redacted.local` : `ANON_${hash}`;
}
