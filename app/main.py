# app/main.py
"""FastAPI Application Entry Point with Static View Mounts and RFC-7807 Exception Handlers."""

import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.db.database import init_database
from app.core.errors import AppException, app_exception_handler
from app.api.products import router as products_router
from app.api.promotions import router as promotions_router
from app.api.checkout import router as checkout_router
from app.api.orders import router as orders_router
from app.api.account import router as account_router
from app.api.returns import router as returns_router
from app.api.webhooks import router as webhooks_router

app = FastAPI(
    title="Enterprise Online Cosmetic Store API",
    description="Headless Composable Commerce Platform API with faceted search, MoCRA compliance, and Stripe checkout.",
    version="1.0.0"
)

# Exception handlers
app.add_exception_handler(AppException, app_exception_handler)

# CORS middleware with explicit secure origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://127.0.0.1:8000", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Database startup hook
@app.on_event("startup")
def on_startup():
    """Ensure database schema and baseline catalog seeds are loaded."""
    init_database()

# Register API Routers
app.include_router(products_router)
app.include_router(promotions_router)
app.include_router(checkout_router)
app.include_router(orders_router)
app.include_router(account_router)
app.include_router(returns_router)
app.include_router(webhooks_router)

# Health & Readiness Probe
@app.get("/health", tags=["System"])
def health_check():
    """Service health and liveness probe."""
    return {"status": "ok", "service": "cosmetics-store-api", "version": "1.0.0"}

# Static and Page Mounts
base_dir = Path(__file__).resolve().parent.parent
public_dir = base_dir / "public"

if public_dir.exists():
    pages_dir = public_dir / "pages"
    if pages_dir.exists():
        app.mount("/pages", StaticFiles(directory=str(pages_dir)), name="pages")

    # Static assets (css, js)
    css_dir = public_dir / "css"
    if css_dir.exists():
        app.mount("/css", StaticFiles(directory=str(css_dir)), name="css")

    js_dir = public_dir / "js"
    if js_dir.exists():
        app.mount("/js", StaticFiles(directory=str(js_dir)), name="js")

    @app.get("/", include_in_schema=False)
    async def serve_root():
        index_file = public_dir / "index.html"
        if index_file.exists():
            return FileResponse(str(index_file))
        return {"message": "Cosmetics Store API Online"}

    app.mount("/", StaticFiles(directory=str(public_dir), html=True), name="public")
