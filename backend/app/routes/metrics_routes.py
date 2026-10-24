from datetime import datetime, date, timedelta
from typing import Optional, Tuple
from fastapi import APIRouter, Query, HTTPException, Depends

from app.schemas import MetricsSummary, MetricsResponse
from app.config import (
    VALID_CUTOFFS,
    DEFAULT_CUTOFF,
    DEFAULT_START_DATE,
    DEFAULT_END_DATE,
    CACHE_DB_PATH
)
from app.cache import CacheDatabase
from app.dependencies import get_cache_db, get_elexon_client
from app.client import ElexonClient, ElexonAPIError
from app.processing import process_date_range

router = APIRouter(tags=["Metrics"])


def validate_parameters(start_date: str, end_date: str, cutoff: str) -> Tuple[date, date, str]:
    if cutoff not in VALID_CUTOFFS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid cutoff '{cutoff}'. Supported cutoffs are: {', '.join(VALID_CUTOFFS)}"
        )
    try:
        s_date = date.fromisoformat(start_date)
        e_date = date.fromisoformat(end_date)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid date format. Dates must be in YYYY-MM-DD format."
        )
    if s_date > e_date:
        raise HTTPException(
            status_code=400,
            detail=f"startDate ({start_date}) cannot be later than endDate ({end_date})."
        )
    return s_date, e_date, cutoff


async def ensure_data_loaded(
    s_date: date,
    e_date: date,
    cache: CacheDatabase,
    client: ElexonClient
):
    """
    Ensure actuals and forecasts covering the date range are in the local cache.
    If missing, fetch from Elexon API and store.
    """
    start_str = s_date.isoformat()
    end_str = e_date.isoformat()

    # Check FUELHH actuals in cache
    cached_actuals = cache.get_fuelhh(start_str, end_str)
    # Expected: (end - start + 1) * 48 periods
    expected_actuals_count = (e_date - s_date).days + 1
    if len(cached_actuals) < expected_actuals_count * 40:  # Allow margin, but if mostly missing, fetch
        try:
            fetched_actuals = await client.fetch_fuelhh(start_str, end_str, fuel_type="WIND")
            cache.store_fuelhh(fetched_actuals)
        except ElexonAPIError as e:
            if not cached_actuals:
                raise HTTPException(status_code=502, detail=f"Failed to fetch actual generation: {str(e)}")

    # Check WINDFOR forecasts in cache
    # We need forecasts published from (start_date - 1 day) to end_date
    prev_date = s_date - timedelta(days=1)
    pub_from = f"{prev_date.isoformat()}T00:00:00Z"
    pub_to = f"{end_str}T23:59:59Z"
    cached_forecasts = cache.get_windfor(pub_from, pub_to)

    if not cached_forecasts:
        try:
            fetched_forecasts = await client.fetch_windfor(pub_from, pub_to)
            cache.store_windfor(fetched_forecasts)
        except ElexonAPIError as e:
            if not cached_forecasts:
                raise HTTPException(status_code=502, detail=f"Failed to fetch wind forecasts: {str(e)}")


@router.get("/summary", response_model=MetricsSummary)
async def get_summary(
    cutoff: str = Query(DEFAULT_CUTOFF, description=f"Day-ahead decision cutoff ({', '.join(VALID_CUTOFFS)})"),
    startDate: str = Query(DEFAULT_START_DATE, description="Start date (YYYY-MM-DD)"),
    endDate: str = Query(DEFAULT_END_DATE, description="End date (YYYY-MM-DD)"),
    cache: CacheDatabase = Depends(get_cache_db),
    client: ElexonClient = Depends(get_elexon_client)
):
    """
    Return high-level verification metrics (MAE, RMSE, Bias, Bias%, WAPE, Matched Hours)
    for the requested date range and day-ahead cutoff.
    """
    s_date, e_date, valid_cutoff = validate_parameters(startDate, endDate, cutoff)
    await ensure_data_loaded(s_date, e_date, cache, client)

    # Load from cache
    prev_date = s_date - timedelta(days=1)
    fuelhh_records = cache.get_fuelhh(startDate, endDate, fuel_type="WIND")
    windfor_records = cache.get_windfor(f"{prev_date.isoformat()}T00:00:00Z", f"{endDate}T23:59:59Z")

    summary, _, _ = process_date_range(startDate, endDate, valid_cutoff, fuelhh_records, windfor_records)
    return summary


@router.get("/metrics", response_model=MetricsResponse)
async def get_metrics(
    cutoff: str = Query(DEFAULT_CUTOFF, description=f"Day-ahead decision cutoff ({', '.join(VALID_CUTOFFS)})"),
    startDate: str = Query(DEFAULT_START_DATE, description="Start date (YYYY-MM-DD)"),
    endDate: str = Query(DEFAULT_END_DATE, description="End date (YYYY-MM-DD)"),
    cache: CacheDatabase = Depends(get_cache_db),
    client: ElexonClient = Depends(get_elexon_client)
):
    """
    Return both summary metrics and day-by-day metrics breakdown
    for the requested date range and day-ahead cutoff.
    """
    s_date, e_date, valid_cutoff = validate_parameters(startDate, endDate, cutoff)
    await ensure_data_loaded(s_date, e_date, cache, client)

    prev_date = s_date - timedelta(days=1)
    fuelhh_records = cache.get_fuelhh(startDate, endDate, fuel_type="WIND")
    windfor_records = cache.get_windfor(f"{prev_date.isoformat()}T00:00:00Z", f"{endDate}T23:59:59Z")

    summary, daily_metrics, _ = process_date_range(startDate, endDate, valid_cutoff, fuelhh_records, windfor_records)
    return MetricsResponse(summary=summary, dailyMetrics=daily_metrics)
