"""
Personalized Skincare Commerce Engine — FastAPI Main Application
Integrates high-performance REST APIs, RFC-7807 Problem Details,
automated DB bootstrap, and modular static storefront mounting.
"""

from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.db import init_database
from app.routers import skin_profiles, recommendations, products, inventory, orders


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initializes the database schema and seed data on application start."""
    init_database()
    yield


app = FastAPI(
    title="Personalized Skincare Product Finder & Commerce Engine",
    description="High-performance decoupled commerce engine delivering sub-250ms personalized skincare routines.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware (Explicit origins for enterprise SAST compliance)
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8000",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


# RFC-7807 Problem Details Global Exception Handler
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "type": "https://errors.skincare-commerce.internal/errors/internal-server-error",
            "title": "Internal Server Error",
            "status": 500,
            "detail": str(exc),
            "instance": request.url.path
        },
        media_type="application/problem+json"
    )


# Health Probe (Container readiness / liveness check)
@app.get("/health", tags=["system"])
def health_check():
    return {
        "status": "ok",
        "service": "skincare-product-finder",
        "version": "1.0.0"
    }


# Include Routers
app.include_router(skin_profiles.router)
app.include_router(recommendations.router)
app.include_router(products.router)
app.include_router(inventory.router)
app.include_router(orders.router)

# Mount Static Frontend Views
repo_root = Path(__file__).resolve().parent.parent
public_dir = repo_root / "public"

if public_dir.exists():
    pages_dir = public_dir / "pages"
    if pages_dir.exists():
        app.mount("/pages", StaticFiles(directory=str(pages_dir)), name="pages")
    app.mount("/", StaticFiles(directory=str(public_dir), html=True), name="public")
