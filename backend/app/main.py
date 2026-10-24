from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import ALLOWED_ORIGINS, CACHE_DB_PATH
from app.cache import CacheDatabase
from app.routes import health, metrics_routes, timeseries_routes

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("windwise")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize SQLite database cache on startup
    logger.info(f"Initializing WindWise UK Cache at {CACHE_DB_PATH}")
    cache = CacheDatabase(CACHE_DB_PATH)
    actuals_count, forecasts_count = cache.get_cached_counts()
    logger.info(f"Cache ready: {actuals_count} FUELHH records, {forecasts_count} WINDFOR records.")
    yield
    logger.info("WindWise UK Backend shutting down.")


app = FastAPI(
    title="WindWise UK API",
    description="UK Electricity Day-Ahead Wind Forecast & Accuracy Verification Engine (January 2026)",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware for local frontend development and configurable production domains
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
)

# Register API routers under /api
app.include_router(health.router, prefix="/api")
app.include_router(metrics_routes.router, prefix="/api")
app.include_router(timeseries_routes.router, prefix="/api")


@app.get("/")
async def root():
    return {
        "project": "WindWise UK",
        "description": "UK Day-Ahead Wind Forecast and Accuracy Dashboard API",
        "version": "1.0.0",
        "docsUrl": "/docs",
        "healthUrl": "/api/health"
    }
