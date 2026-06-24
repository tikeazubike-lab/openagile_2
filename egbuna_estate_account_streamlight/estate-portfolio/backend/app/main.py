"""
EPM — FastAPI application factory.

Route order matters:
  1. API routers (/api/v1/*)   — registered first
  2. Static assets (/assets/*) — Vite-generated JS/CSS bundles
  3. SPA catch-all              — any other path returns index.html

FastAPI's StaticFiles(html=True) only serves index.html for the exact root "/",
not for sub-paths like "/login" or "/dashboard". A proper SPA needs a catch-all
route that returns index.html for any non-API, non-asset path so the client-side
router (TanStack Router) can handle the route.
"""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.routers import auth, dashboard, holdings, obsidian, claims, registrars
from app.routers.admin_users import router as admin_users_router
from app.routers.companies import router as companies_router
from app.routers.prices import router as prices_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup actions (e.g. warm connection pool) go here if needed.
    yield
    # Shutdown actions go here if needed.


app = FastAPI(
    title="Estate Portfolio Manager API",
    version="2.0.0",
    docs_url="/api/docs" if settings.is_dev else None,   # Disable Swagger in production
    redoc_url="/api/redoc" if settings.is_dev else None,
    lifespan=lifespan,
)

# ── CORS ───────────────────────────────────────────────────────────────────────
# allow_credentials=True is REQUIRED for httpOnly cookies to be sent cross-origin.
# In production, ALLOWED_ORIGINS is the exact Traefik-routed domain.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── API Routers ────────────────────────────────────────────────────────────────
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(dashboard.router, prefix="/api/v1", tags=["dashboard"])
app.include_router(holdings.router, prefix="/api/v1", tags=["holdings"])
app.include_router(companies_router)
app.include_router(prices_router)
app.include_router(obsidian.router)
app.include_router(claims.router)
app.include_router(registrars.router, prefix="/api/v1")
app.include_router(admin_users_router)

# ── Caching Middleware ────────────────────────────────────────────────────────
@app.middleware("http")
async def add_cache_headers(request: Request, call_next):
    response = await call_next(request)
    path = request.url.path
    if path.startswith("/assets/"):
        # Vite hashed assets can be cached securely for a year
        response.headers["Cache-Control"] = "public, max-age=31536000, immutable"
    return response

# ── React SPA Serving ──────────────────────────────────────────────────────────
# Strategy:
#   1. Mount /assets as StaticFiles → serves Vite-hashed JS/CSS bundles
#   2. Catch-all route → returns index.html for any non-API path
#      This allows TanStack Router to handle client-side routing.
_static_dir = os.path.join(os.path.dirname(__file__), "static")
_index_html = os.path.join(_static_dir, "index.html")

if os.path.isdir(_static_dir):
    # Serve Vite build assets (JS, CSS, images) at /assets/*
    _assets_dir = os.path.join(_static_dir, "assets")
    if os.path.isdir(_assets_dir):
        app.mount("/assets", StaticFiles(directory=_assets_dir), name="assets")

    # SPA catch-all: any path not matched by API routers or /assets returns index.html
    @app.get("/{full_path:path}", response_class=HTMLResponse, include_in_schema=False)
    async def spa_fallback(request: Request, full_path: str):
        response = FileResponse(_index_html)
        # Prevent caching of index.html so clients always get the latest Vite asset hashes
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response
