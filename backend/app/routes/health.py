from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from app.schemas import HealthResponse
from app.cache import CacheDatabase
from app.dependencies import get_cache_db

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
async def health_check(cache: CacheDatabase = Depends(get_cache_db)):
    """Health check endpoint to verify backend operational state and database cache statistics."""
    actuals_count, forecasts_count = cache.get_cached_counts()
    return HealthResponse(
        status="ok",
        timestamp=datetime.now(timezone.utc).isoformat(),
        cachedActualsCount=actuals_count,
        cachedForecastsCount=forecasts_count,
        cacheDatabase=cache.db_path
    )
