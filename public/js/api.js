/**
 * Client-Side Skincare API Layer & Interactive Event Handlers
 * Wires Storefront UI Views to High-Performance FastAPI Backend Endpoints.
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

    // Atomic Inventory Reservation
    async reserveInventory(sku, quantity = 1, sessionId = "sess_default") {
        try {
            const res = await fetch(`${API_BASE_URL}/api/v1/inventory/reserve`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ sku, quantity, session_id: sessionId })
            });
            if (!res.ok) throw new Error(`HTTP error ${res.status}`);
            return await res.json();
        } catch (e) {
            console.error("Error creating reservation:", e);
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
            <button type="button" class="concern-pill" data-concern="${c.id}" aria-pressed="false">
                ${c.label}
            </button>
        `).join("");

        concernsContainer.querySelectorAll(".concern-pill").forEach(btn => {
            btn.addEventListener("click", () => {
                const isPressed = btn.getAttribute("aria-pressed") === "true";
                btn.setAttribute("aria-pressed", !isPressed);
                btn.classList.toggle("active");
            });
        });
    }

    if (submitBtn) {
        submitBtn.addEventListener("click", async (e) => {
            e.preventDefault();
            const selectedCard = document.querySelector(".skin-card.selected");
            const skinType = selectedCard ? selectedCard.getAttribute("data-skin-type") : "combination";
            
            const activePills = document.querySelectorAll(".concern-pill.active");
            const concerns = Array.from(activePills).map(p => p.getAttribute("data-concern"));

            submitBtn.textContent = "Analyzing Skin Profile...";
            submitBtn.disabled = true;

            const recommendations = await SkincareAPI.getRecommendations({
                skin_type: skinType,
                concerns: concerns.length ? concerns : ["acne", "redness"],
                sensitivity: "medium"
            });

            if (recommendations) {
                sessionStorage.setItem("last_recommendations", JSON.stringify(recommendations));
                window.location.href = "/pages/product-listing.html?personalized=true";
            } else {
                submitBtn.textContent = "Find My Routine";
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

    const titleEl = document.getElementById("product-title");
    const priceEl = document.getElementById("product-price");
    const descEl = document.getElementById("product-desc");
    const inciEl = document.getElementById("inci-ingredients");
    const swatchesContainer = document.getElementById("shade-swatches");
    const reserveBtn = document.getElementById("reserve-btn");

    if (titleEl) titleEl.textContent = product.name;
    if (priceEl) priceEl.textContent = `$${product.price.toFixed(2)}`;
    if (descEl) descEl.textContent = product.description;
    if (inciEl) inciEl.textContent = product.inci_ingredients;

    if (swatchesContainer && product.shade_swatches && product.shade_swatches.length) {
        swatchesContainer.innerHTML = product.shade_swatches.map((s, idx) => `
            <button class="swatch-btn ${idx === 0 ? 'selected' : ''}" 
                    style="background-color: ${s.hex_color}" 
                    data-sku="${s.sku}" 
                    data-name="${s.shade_name}"
                    aria-label="${s.shade_name}" 
                    title="${s.shade_name}">
            </button>
        `).join("");

        swatchesContainer.querySelectorAll(".swatch-btn").forEach(btn => {
            btn.addEventListener("click", () => {
                swatchesContainer.querySelectorAll(".swatch-btn").forEach(b => b.classList.remove("selected"));
                btn.classList.add("selected");
                const label = document.getElementById("selected-shade-name");
                if (label) label.textContent = btn.getAttribute("data-name");
            });
        });
    }

    if (reserveBtn) {
        reserveBtn.addEventListener("click", async () => {
            const activeSwatch = document.querySelector(".swatch-btn.selected");
            const sku = activeSwatch ? activeSwatch.getAttribute("data-sku") : (product.shade_swatches[0]?.sku || "SKU-TINT-100");
            
            reserveBtn.textContent = "Reserving Stock (10m TTL)...";
            reserveBtn.disabled = true;

            const res = await SkincareAPI.reserveInventory(sku, 1, "session_" + Date.now());
            if (res && res.reservation_id) {
                alert(`✨ Reserved! Hold ID: ${res.reservation_id} (Expires in 10 minutes)`);
                reserveBtn.textContent = "Hold Confirmed ✓";
            } else {
                alert("Inventory reservation failed.");
                reserveBtn.textContent = "Add to Bag";
                reserveBtn.disabled = false;
            }
        });
    }
}
