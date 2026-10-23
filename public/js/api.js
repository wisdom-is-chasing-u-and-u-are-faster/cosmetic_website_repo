// public/js/api.js - Client API Client for REST Endpoints
const API = {
  baseUrl: "/api/v1",

  async request(endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint}`;
    const headers = {
      "Content-Type": "application/json",
      ...(options.headers || {})
    };

    try {
      const response = await fetch(url, { ...options, headers });
      const data = await response.json();

      if (!response.ok) {
        const errorMsg = data.detail || data.title || "An error occurred";
        throw new Error(errorMsg);
      }
      return data;
    } catch (err) {
      console.error(`API Error [${endpoint}]:`, err);
      throw err;
    }
  },

  // Products
  async getProducts(params = {}) {
    const query = new URLSearchParams(params).toString();
    return this.request(`/products${query ? `?${query}` : ""}`);
  },

  async getProductDetail(id) {
    return this.request(`/products/${id}`);
  },

  // Merchandising & Promos
  async getHeroPromotions() {
    return this.request("/promotions/hero");
  },

  async applyPromo(code, cartTotal, items = []) {
    return this.request("/promotions/apply", {
      method: "POST",
      body: JSON.stringify({ code, cart_total: cartTotal, items })
    });
  },

  // Inventory & Checkout
  async reserveInventory(items, idempotencyKey = null) {
    const headers = idempotencyKey ? { "Idempotency-Key": idempotencyKey } : {};
    return this.request("/checkout/reserve", {
      method: "POST",
      headers,
      body: JSON.stringify({ items, reservation_ttl_seconds: 900 })
    });
  },

  async processCheckout(payload, idempotencyKey = null) {
    const headers = idempotencyKey ? { "Idempotency-Key": idempotencyKey } : {};
    return this.request("/checkout/process", {
      method: "POST",
      headers,
      body: JSON.stringify(payload)
    });
  },

  // Orders & Tracking
  async getOrder(orderId) {
    return this.request(`/orders/${orderId}`);
  },

  async listOrders(email = null) {
    const query = email ? `?customer_email=${encodeURIComponent(email)}` : "";
    return this.request(`/orders${query}`);
  },

  // Returns & Exchanges
  async submitReturn(payload) {
    return this.request("/returns", {
      method: "POST",
      body: JSON.stringify(payload)
    });
  },

  // Account & GDPR PII
  async getAccount(customerId) {
    return this.request(`/account/${customerId}`);
  },

  async updateAccount(customerId, data) {
    return this.request(`/account/${customerId}`, {
      method: "PUT",
      body: JSON.stringify(data)
    });
  },

  async erasePII(customerId) {
    return this.request(`/customers/${customerId}/pii`, {
      method: "DELETE"
    });
  }
};

window.API = API;
