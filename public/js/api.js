/**
 * Client-Side Skincare API Layer & Interactive Event Handlers
 * Wires Storefront UI Views to High-Performance FastAPI Backend Endpoints.
 * ARCH-10099: Added dynamic stock visibility, real-time stock checks, and strict cart quantity controls.
 */

const API_BASE_URL = window.location.origin;

const SkincareAPI = {
    // Health probe
    async checkHealth() {
        try {
            const res = await fetch(`${API_BASE_URL}/health`);
            return await res.json();
        } catch (e) {
            console.error("Health check error:", e);
            return { status: "error", detail: e.message };
        }
    },

    // Skin profiles & quiz options
    async getSkinProfileOptions() {
        try {
            const res = await fetch(`${API_BASE_URL}/api/v1/skin-profiles/options`);
            if (!res.ok) throw new Error(`HTTP error ${res.status}`);
            return await res.json();
        } catch (e) {
            console.error("Error fetching skin profile options:", e);
            return null;
        }
    },

    // Get recommendations
    async getRecommendations(profile) {
        try {
            const res = await fetch(`${API_BASE_URL}/api/v1/recommendations`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(profile)
            });
            if (!res.ok) throw new Error(`HTTP error ${res.status}`);
            return await res.json();
        } catch (e) {
            console.error("Error fetching recommendations:", e);
            return null;
        }
    },

    // Catalog search & faceted filter
    async getProducts(params = {}) {
        try {
            const qs = new URLSearchParams(params).toString();
            const res = await fetch(`${API_BASE_URL}/api/v1/products?${qs}`);
            if (!res.ok) throw new Error(`HTTP error ${res.status}`);
            return await res.json();
        } catch (e) {
            console.error("Error fetching products:", e);
            return null;
        }
    },

    // Single product detail
    async getProductDetail(idOrSlug) {
        try {
            const res = await fetch(`${API_BASE_URL}/api/v1/products/${encodeURIComponent(idOrSlug)}`);
            if (!res.ok) throw new Error(`HTTP error ${res.status}`);
            return await res.json();
        } catch (e) {
            console.error("Error fetching product detail:", e);
            return null;
        }
    },

    // Real-time stock lookup for SKU or product (REQ-F-001, REQ-F-006)
    async getStock(skuOrProductId) {
        try {
            const res = await fetch(`${API_BASE_URL}/api/v1/inventory/${encodeURIComponent(skuOrProductId)}`);
            if (!res.ok) throw new Error(`HTTP error ${res.status}`);
            return await res.json();
        } catch (e) {
            console.error("Error fetching stock info:", e);
            return null;
        }
    },

    // Atomic Inventory Reservation (REQ-F-002, REQ-F-004, REQ-F-015)
    async reserveInventory(sku, quantity = 1, sessionId = "sess_default") {
        try {
            const res = await fetch(`${API_BASE_URL}/api/v1/inventory/reserve`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ sku, quantity, session_id: sessionId })
            });
            if (!res.ok) {
                const errorData = await res.json().catch(() => ({}));
                const msg = errorData.detail || `Reservation rejected (HTTP ${res.status})`;
                throw new Error(msg);
            }
            return await res.json();
        } catch (e) {
            console.error("Error creating reservation:", e);
            return { error: true, message: e.message };
        }
    },

    // Release stock reservation (REQ-F-006)
    async releaseInventory(reservationId) {
        try {
            const res = await fetch(`${API_BASE_URL}/api/v1/inventory/release`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ reservation_id: reservationId })
            });
            if (!res.ok) throw new Error(`HTTP error ${res.status}`);
            return await res.json();
        } catch (e) {
            console.error("Error releasing reservation:", e);
            return null;
        }
    },

    // Order Creation
    async createOrder(orderPayload) {
        try {
            const res = await fetch(`${API_BASE_URL}/api/v1/orders`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(orderPayload)
            });
            if (!res.ok) throw new Error(`HTTP error ${res.status}`);
            return await res.json();
        } catch (e) {
            console.error("Error creating order:", e);
            return null;
        }
    }
};

// Global Store State & DOM Init
document.addEventListener("DOMContentLoaded", () => {
    console.log("🌸 Skincare Storefront Initialized.");
    
    // Auto-initialize Product Finder if on page
    if (document.getElementById("finder-form") || document.getElementById("skin-type-options")) {
        initProductFinderPage();
    }

    // Auto-initialize Product Listing if on page
    if (document.getElementById("product-grid") || document.getElementById("recommendation-results")) {
        initProductListingPage();
    }

    // Auto-initialize Product Detail if on page
    if (document.getElementById("product-detail-view")) {
        initProductDetailPage();
    }
});

// Interactive Handlers
async function initProductFinderPage() {
    const skinTypeContainer = document.getElementById("skin-type-options");
    const concernsContainer = document.getElementById("concerns-options");
    const submitBtn = document.getElementById("finder-submit-btn");

    const options = await SkincareAPI.getSkinProfileOptions();
    if (!options) return;

    if (skinTypeContainer && options.skin_types) {
        skinTypeContainer.innerHTML = options.skin_types.map(st => `
            <div class="skin-card" data-skin-type="${st.id}" tabindex="0" role="radio" aria-checked="false" aria-label="${st.label}">
                <h4>${st.label}</h4>
                <p>${st.description}</p>
            </div>
        `).join("");

        skinTypeContainer.querySelectorAll(".skin-card").forEach(card => {
            card.addEventListener("click", () => {
                skinTypeContainer.querySelectorAll(".skin-card").forEach(c => {
                    c.classList.remove("selected");
                    c.setAttribute("aria-checked", "false");
                });
                card.classList.add("selected");
                card.setAttribute("aria-checked", "true");
            });
        });
    }

    if (concernsContainer && options.concerns) {
        concernsContainer.innerHTML = options.concerns.map(c => `
            <button type="button" class="concern-pill" data-concern="${c.id}">
                ${c.icon} ${c.label}
            </button>
        `).join("");

        concernsContainer.querySelectorAll(".concern-pill").forEach(pill => {
            pill.addEventListener("click", () => {
                pill.classList.toggle("active");
            });
        });
    }

    if (submitBtn) {
        submitBtn.addEventListener("click", async () => {
            const selectedSkinType = skinTypeContainer?.querySelector(".skin-card.selected")?.getAttribute("data-skin-type");
            const selectedConcerns = Array.from(concernsContainer?.querySelectorAll(".concern-pill.active") || []).map(p => p.getAttribute("data-concern"));
            const sensitivity = document.querySelector('input[name="sensitivity"]:checked')?.value || "medium";

            if (!selectedSkinType) {
                alert("Please select your primary skin type.");
                return;
            }

            submitBtn.textContent = "Analyzing Skin Profile...";
            submitBtn.disabled = true;

            const recommendations = await SkincareAPI.getRecommendations({
                skin_type: selectedSkinType,
                concerns: selectedConcerns,
                sensitivity: sensitivity
            });

            if (recommendations && recommendations.routine_steps) {
                sessionStorage.setItem("last_recommendations", JSON.stringify(recommendations));
                window.location.href = "/pages/product-listing.html?personalized=true";
            } else {
                alert("Could not generate recommendations at this time.");
                submitBtn.textContent = "Generate Personalized Routine";
                submitBtn.disabled = false;
            }
        });
    }
}

async function initProductListingPage() {
    const grid = document.getElementById("product-grid");
    const countEl = document.getElementById("product-count");
    if (!grid) return;

    // Check if recommendations exist in session
    const recsJson = sessionStorage.getItem("last_recommendations");
    const urlParams = new URLSearchParams(window.location.search);

    if (urlParams.get("personalized") === "true" && recsJson) {
        const recs = JSON.parse(recsJson);
        if (countEl) countEl.textContent = `${recs.routine_steps.length} Personalized Matches Found`;

        grid.innerHTML = recs.routine_steps.map(step => `
            <div class="product-card recommendation-card">
                <span class="step-badge">${step.step_name}</span>
                <img src="${step.image_url}" alt="${step.product_name}" class="product-img" />
                <div class="card-body">
                    <span class="match-score">🎯 ${step.match_score}% Match</span>
                    <h3>${step.product_name}</h3>
                    <p class="match-reason">${step.match_reasons[0] || ""}</p>
                    <div class="price-row">
                        <span class="price">$${step.price.toFixed(2)}</span>
                        <a href="/pages/product-detail.html?product=${step.product_slug}" class="btn-sm">View Details</a>
                    </div>
                </div>
            </div>
        `).join("");
    } else {
        const catalog = await SkincareAPI.getProducts();
        if (catalog && catalog.products) {
            if (countEl) countEl.textContent = `${catalog.pagination.total} Products Available`;
            grid.innerHTML = catalog.products.map(p => `
                <div class="product-card">
                    <img src="${p.image_url}" alt="${p.name}" class="product-img" />
                    <div class="card-body">
                        <h3>${p.name}</h3>
                        <p class="rating">⭐ ${p.rating.toFixed(1)} (${p.review_count} reviews)</p>
                        <div class="price-row">
                            <span class="price">$${p.price.toFixed(2)}</span>
                            <a href="/pages/product-detail.html?product=${p.slug}" class="btn-sm">Explore</a>
                        </div>
                    </div>
                </div>
            `).join("");
        }
    }
}

async function initProductDetailPage() {
    const params = new URLSearchParams(window.location.search);
    const slug = params.get("product") || "prod-tint-01";
    const product = await SkincareAPI.getProductDetail(slug);
    if (!product) return;

    const pageContainer = document.getElementById("product-detail-view");
    const titleEl = document.getElementById("product-title");
    const priceEl = document.getElementById("product-price");
    const descEl = document.getElementById("product-desc");
    const inciEl = document.getElementById("inci-ingredients");
    const swatchesContainer = document.getElementById("shade-swatches");
    const reserveBtn = document.getElementById("reserve-btn");

    const stockBadge = document.getElementById("stock-status-badge");
    const quantityInput = document.getElementById("quantity-input");
    const minusBtn = document.getElementById("quantity-minus");
    const plusBtn = document.getElementById("quantity-plus");
    const stockLimitHint = document.getElementById("stock-limit-hint");

    if (titleEl) titleEl.textContent = product.name;
    if (priceEl) priceEl.textContent = `$${product.price.toFixed(2)}`;
    if (descEl) descEl.textContent = product.description;
    if (inciEl) inciEl.textContent = product.inci_ingredients;

    // Helper: update UI according to available stock (REQ-F-008, REQ-F-009)
    function updateStockUI(availableStock) {
        if (pageContainer) pageContainer.setAttribute("data-stock-level", availableStock);

        const currentVal = parseInt(quantityInput?.value || "1", 10);
        const lowStockThreshold = 10;

        if (quantityInput) {
            quantityInput.max = availableStock;
            if (availableStock === 0) {
                quantityInput.value = 0;
                quantityInput.disabled = true;
            } else {
                quantityInput.disabled = false;
                if (currentVal > availableStock) {
                    quantityInput.value = availableStock;
                } else if (currentVal < 1) {
                    quantityInput.value = 1;
                }
            }
        }

        if (availableStock === 0) {
            if (stockBadge) {
                stockBadge.textContent = "Out of Stock";
                stockBadge.className = "stock-status stock-status-out";
            }
            if (reserveBtn) {
                reserveBtn.disabled = true;
                reserveBtn.textContent = "Out of Stock";
            }
            if (minusBtn) minusBtn.disabled = true;
            if (plusBtn) plusBtn.disabled = true;
            if (stockLimitHint) stockLimitHint.textContent = "(Product is currently unavailable)";
        } else if (availableStock <= lowStockThreshold) {
            if (stockBadge) {
                stockBadge.textContent = `Only ${availableStock} Left`;
                stockBadge.className = "stock-status stock-status-low";
            }
            if (reserveBtn) {
                reserveBtn.disabled = false;
                reserveBtn.textContent = "Add to Bag & Reserve Inventory (10m Hold)";
            }
            if (minusBtn) minusBtn.disabled = false;
            if (plusBtn) plusBtn.disabled = false;
            if (stockLimitHint) stockLimitHint.textContent = `(Max limit: ${availableStock})`;
        } else {
            if (stockBadge) {
                stockBadge.textContent = "In Stock";
                stockBadge.className = "stock-status stock-status-instock";
            }
            if (reserveBtn) {
                reserveBtn.disabled = false;
                reserveBtn.textContent = "Add to Bag & Reserve Inventory (10m Hold)";
            }
            if (minusBtn) minusBtn.disabled = false;
            if (plusBtn) plusBtn.disabled = false;
            if (stockLimitHint) stockLimitHint.textContent = "";
        }
    }

    // Set initial stock from product payload
    let currentStock = product.available_stock !== undefined ? product.available_stock : (product.inventory?.available || 0);
    updateStockUI(currentStock);

    // Quantity selector buttons
    if (minusBtn && quantityInput) {
        minusBtn.addEventListener("click", () => {
            const stock = parseInt(pageContainer?.getAttribute("data-stock-level") || `${currentStock}`, 10);
            let val = parseInt(quantityInput.value || "1", 10);
            if (val > 1) {
                quantityInput.value = val - 1;
            }
        });
    }

    if (plusBtn && quantityInput) {
        plusBtn.addEventListener("click", () => {
            const stock = parseInt(pageContainer?.getAttribute("data-stock-level") || `${currentStock}`, 10);
            let val = parseInt(quantityInput.value || "1", 10);
            if (val < stock) {
                quantityInput.value = val + 1;
            }
        });
    }

    if (quantityInput) {
        quantityInput.addEventListener("change", () => {
            const stock = parseInt(pageContainer?.getAttribute("data-stock-level") || `${currentStock}`, 10);
            let val = parseInt(quantityInput.value, 10);
            if (isNaN(val) || val < 1) {
                quantityInput.value = stock > 0 ? 1 : 0;
            } else if (val > stock) {
                // Clamp to available stock (REQ-F-009)
                quantityInput.value = stock;
            }
        });
    }

    // Swatches interactivity
    if (swatchesContainer && product.shade_swatches && product.shade_swatches.length) {
        swatchesContainer.innerHTML = product.shade_swatches.map((s, idx) => `
            <button class="swatch-btn ${idx === 0 ? 'selected' : ''}" 
                    style="background-color: ${s.hex_color}" 
                    data-sku="${s.sku}" 
                    data-name="${s.shade_name}"
                    data-stock="${s.stock_quantity}"
                    aria-label="${s.shade_name}" 
                    title="${s.shade_name} (${s.stock_quantity} available)">
            </button>
        `).join("");

        // If first swatch selected, sync stock
        const firstSwatch = product.shade_swatches[0];
        if (firstSwatch) {
            updateStockUI(firstSwatch.stock_quantity);
        }

        swatchesContainer.querySelectorAll(".swatch-btn").forEach(btn => {
            btn.addEventListener("click", async () => {
                swatchesContainer.querySelectorAll(".swatch-btn").forEach(b => b.classList.remove("selected"));
                btn.classList.add("selected");
                const label = document.getElementById("selected-shade-name");
                if (label) label.textContent = btn.getAttribute("data-name");

                const sku = btn.getAttribute("data-sku");
                // Fetch real-time stock for this specific swatch SKU (REQ-F-001)
                const stockData = await SkincareAPI.getStock(sku);
                const swatchStock = stockData ? stockData.available_stock : parseInt(btn.getAttribute("data-stock") || "0", 10);
                updateStockUI(swatchStock);
            });
        });
    }

    // Add to cart & reserve handler
    if (reserveBtn) {
        reserveBtn.addEventListener("click", async () => {
            const activeSwatch = document.querySelector(".swatch-btn.selected");
            const sku = activeSwatch ? activeSwatch.getAttribute("data-sku") : (product.shade_swatches[0]?.sku || "SKU-TINT-100");
            const selectedQty = parseInt(quantityInput?.value || "1", 10);
            const maxStock = parseInt(pageContainer?.getAttribute("data-stock-level") || "0", 10);

            // Validation before sending reservation (REQ-F-002, REQ-F-010)
            if (selectedQty > maxStock) {
                alert(`Requested quantity (${selectedQty}) exceeds available stock (${maxStock}). Please adjust quantity.`);
                return;
            }

            reserveBtn.textContent = "Reserving Stock (10m TTL)...";
            reserveBtn.disabled = true;

            const res = await SkincareAPI.reserveInventory(sku, selectedQty, "session_" + Date.now());
            if (res && res.reservation_id) {
                alert(`✨ Reserved! Hold ID: ${res.reservation_id} for quantity ${res.quantity} (Expires in 10 minutes)`);
                reserveBtn.textContent = "Hold Confirmed ✓";
                // Re-query stock after reservation
                const updatedStock = await SkincareAPI.getStock(sku);
                if (updatedStock) {
                    updateStockUI(updatedStock.available_stock);
                }
            } else {
                const errMsg = res?.message || "Inventory reservation failed.";
                alert(`Failed to reserve stock: ${errMsg}`);
                reserveBtn.textContent = "Add to Bag & Reserve Inventory (10m Hold)";
                reserveBtn.disabled = false;
            }
        });
    }
}
