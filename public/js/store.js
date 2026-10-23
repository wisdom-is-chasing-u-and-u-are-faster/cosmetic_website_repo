// public/js/store.js - Client Cart & Local State Store
const Store = {
  getCart() {
    const raw = localStorage.getItem("aura_cart");
    return raw ? JSON.parse(raw) : [];
  },

  saveCart(cart) {
    localStorage.setItem("aura_cart", JSON.stringify(cart));
    this.updateCartBadge();
  },

  addToCart(item) {
    const cart = this.getCart();
    const existing = cart.find(i => i.sku === item.sku);
    if (existing) {
      existing.quantity += item.quantity || 1;
    } else {
      cart.push({
        sku: item.sku,
        product_id: item.product_id,
        product_name: item.product_name,
        shade_name: item.shade_name,
        unit_price: item.unit_price,
        quantity: item.quantity || 1
      });
    }
    this.saveCart(cart);
  },

  removeFromCart(sku) {
    const cart = this.getCart().filter(i => i.sku !== sku);
    this.saveCart(cart);
  },

  updateQuantity(sku, qty) {
    const cart = this.getCart();
    const item = cart.find(i => i.sku === sku);
    if (item) {
      item.quantity = Math.max(1, qty);
      this.saveCart(cart);
    }
  },

  clearCart() {
    localStorage.removeItem("aura_cart");
    this.updateCartBadge();
  },

  getCartTotal() {
    return this.getCart().reduce((sum, i) => sum + (i.unit_price * i.quantity), 0);
  },

  updateCartBadge() {
    const badge = document.getElementById("cart-count-badge");
    if (badge) {
      const totalItems = this.getCart().reduce((sum, i) => sum + i.quantity, 0);
      badge.textContent = totalItems;
    }
  }
};

window.Store = Store;
document.addEventListener("DOMContentLoaded", () => {
  Store.updateCartBadge();
});
