# app/core/security.py
"""Security utilities including HMAC webhook verification and PII anonymization."""

import os
import hmac
import hashlib

HMAC_SECRET = os.getenv("WEBHOOK_3PL_HMAC_SECRET", "secret-webhook-key-3pl")


def generate_hmac_signature(payload_bytes: bytes,
                            secret: str = HMAC_SECRET) -> str:
    """Generate SHA256 HMAC hex digest for payload bytes."""
    return hmac.new(secret.encode("utf-8"), payload_bytes,
                    hashlib.sha256).hexdigest()


def verify_hmac_signature(
        payload_bytes: bytes, signature_header: str, secret: str = HMAC_SECRET) -> bool:
    """Verify inbound webhook HMAC signature securely with constant time compare."""
    if not signature_header:
        return False
    expected = generate_hmac_signature(payload_bytes, secret)
    # Support 'sha256=<hex>' or raw hex
    clean_sig = signature_header.replace("sha256=", "").strip()
    return hmac.compare_digest(expected, clean_sig)


def anonymize_pii_string(value: str) -> str:
    """Anonymize PII field (e.g. email or name) with deterministic hash mask."""
    if not value:
        return "[ANONYMIZED]"
    salt = "pii-erasure-salt"
    digest = hashlib.sha256(f"{value}:{salt}".encode("utf-8")).hexdigest()[:12]
    return f"anon_{digest}@redacted.local" if "@" in value else f"ANON_{digest}"
