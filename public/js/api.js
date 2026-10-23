/**
 * Client-Side API Helper for Enterprise Online Cosmetic Store Platform
 * Connects UI pages dynamically to REST endpoints in api_contract.json
 */

const API_BASE = '/api/v1';

const StoreAPI = {
  // Products & Faceted Search [REQ-F-001, REQ-F-011]
  async getProducts(filters = {}) {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([key, val]) => {
      if (val !== undefined && val !== null && val !== '') {
        params.append(key, val);
      }
    });
    const res = await fetch(`${API_BASE}/products?${params.toString()}`);
    if (!res.ok) throw await res.json();
    return await res.json();
  },

  async getProductById(id) {
    const res = await fetch(`${API_BASE}/products/${id}`);
    if (!res.ok) throw await res.json();
    return await res.json();
  },

  // Promo Engine [REQ-F-015]
  async applyPromoCode(code, cartTotal, items = []) {
    const res = await fetch(`${API_BASE}/promotions/apply`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ code, cart_total: cartTotal, items })
    });
    if (!res.ok) throw await res.json();
    return await res.json();
  },

  // Inventory Reservation Lock [REQ-F-009, REQ-F-013]
  async reserveInventory(sessionId, items, idempotencyKey = null) {
    const headers = { 'Content-Type': 'application/json' };
    if (idempotencyKey) headers['Idempotency-Key'] = idempotencyKey;

    const res = await fetch(`${API_BASE}/checkout/reserve`, {
      method: 'POST',
      headers,
      body: JSON.stringify({ session_id: sessionId, items })
    });
    if (!res.ok) throw await res.json();
    return await res.json();
  },

  // Single-Page Progressive Checkout [REQ-F-002, REQ-F-003, REQ-F-004]
  async processCheckout(checkoutPayload, idempotencyKey = null) {
    const headers = { 'Content-Type': 'application/json' };
    if (idempotencyKey) headers['Idempotency-Key'] = idempotencyKey;

    const res = await fetch(`${API_BASE}/checkout/process`, {
      method: 'POST',
      headers,
      body: JSON.stringify(checkoutPayload)
    });
    if (!res.ok) throw await res.json();
    return await res.json();
  },

  // Orders & 3PL Logistics Tracking [REQ-F-006]
  async getOrder(orderId) {
    const res = await fetch(`${API_BASE}/orders/${orderId}`);
    if (!res.ok) throw await res.json();
    return await res.json();
  },

  async getOrderHistory(email) {
    const params = email ? `?email=${encodeURIComponent(email)}` : '';
    const res = await fetch(`${API_BASE}/orders/history${params}`);
    if (!res.ok) throw await res.json();
    return await res.json();
  },

  // Returns & Shade Exchange [REQ-F-007, REQ-F-008]
  async submitReturn(returnPayload) {
    const res = await fetch(`${API_BASE}/returns`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(returnPayload)
    });
    if (!res.ok) throw await res.json();
    return await res.json();
  },

  // GDPR/CCPA PII Erasure [REQ-F-012]
  async requestPiiErasure(email) {
    const res = await fetch(`${API_BASE}/account/pii-erasure`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email })
    });
    if (!res.ok) throw await res.json();
    return await res.json();
  }
};

window.StoreAPI = StoreAPI;
