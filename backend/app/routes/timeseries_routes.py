from datetime import date, timedelta
from typing import List, Dict, Any
from fastapi import APIRouter, Query, HTTPException, Depends

from app.schemas import TimeseriesResponse, ForecastEvolutionResponse, CutoffEvolutionItem
from app.config import VALID_CUTOFFS, DEFAULT_CUTOFF
from app.cache import CacheDatabase
from app.dependencies import get_cache_db, get_elexon_client
from app.client import ElexonClient
from app.routes.metrics_routes import ensure_data_loaded
from app.processing import (
    aggregate_hourly_actuals,
    select_day_ahead_forecasts,
    build_hourly_timeseries
)
from app.metrics import calculate_metrics

router = APIRouter(tags=["Timeseries"])


@router.get("/timeseries", response_model=TimeseriesResponse)
async def get_timeseries(
    date_str: str = Query(..., alias="date", description="Delivery date (YYYY-MM-DD)"),
    cutoff: str = Query(DEFAULT_CUTOFF, description=f"Day-ahead decision cutoff ({', '.join(VALID_CUTOFFS)})"),
    cache: CacheDatabase = Depends(get_cache_db),
    client: ElexonClient = Depends(get_elexon_client)
):
    """
    Return 24 hourly intervals for a specific delivery date and day-ahead cutoff,
    including actual generation, selected forecast, publication timestamp, and hourly error.
    """
    if cutoff not in VALID_CUTOFFS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid cutoff '{cutoff}'. Supported cutoffs are: {', '.join(VALID_CUTOFFS)}"
        )
    try:
        target_date = date.fromisoformat(date_str)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Expected YYYY-MM-DD.")

    await ensure_data_loaded(target_date, target_date, cache, client)

    prev_date = target_date - timedelta(days=1)
    fuelhh_records = cache.get_fuelhh(date_str, date_str, fuel_type="WIND")
    windfor_records = cache.get_windfor(f"{prev_date.isoformat()}T00:00:00Z", f"{date_str}T23:59:59Z")

    hourly_actuals = aggregate_hourly_actuals(fuelhh_records)
    selected_fc = select_day_ahead_forecasts(windfor_records, target_date, cutoff)
    intervals = build_hourly_timeseries(target_date, cutoff, hourly_actuals, selected_fc)

    # Compute single-day summary
    matched_pairs = [(i.forecastMW, i.actualMW) for i in intervals if i.isMatched]
    missing_actual = len([i for i in intervals if i.actualMW is None])
    missing_forecast = len([i for i in intervals if i.forecastMW is None])
    day_summary_dict = calculate_metrics(
        pairs=matched_pairs,
        total_hours=24,
        missing_actual_count=missing_actual,
        missing_forecast_count=missing_forecast,
        start_date=date_str,
        end_date=date_str,
        cutoff=cutoff
    )

    return TimeseriesResponse(
        date=date_str,
        cutoff=cutoff,
        intervals=intervals,
        daySummary=day_summary_dict
    )


@router.get("/forecast-evolution", response_model=ForecastEvolutionResponse)
async def get_forecast_evolution(
    date_str: str = Query(..., alias="date", description="Delivery date (YYYY-MM-DD)"),
    cache: CacheDatabase = Depends(get_cache_db),
    client: ElexonClient = Depends(get_elexon_client)
):
    """
    Compare how forecasts and accuracy metrics evolve across all available
    decision cutoffs (09:00, 11:00, 12:00, 14:00, 17:00 UTC) for a single delivery date.
    """
    try:
        target_date = date.fromisoformat(date_str)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Expected YYYY-MM-DD.")

    await ensure_data_loaded(target_date, target_date, cache, client)

    prev_date = target_date - timedelta(days=1)
    fuelhh_records = cache.get_fuelhh(date_str, date_str, fuel_type="WIND")
    windfor_records = cache.get_windfor(f"{prev_date.isoformat()}T00:00:00Z", f"{date_str}T23:59:59Z")

    hourly_actuals = aggregate_hourly_actuals(fuelhh_records)

    cutoff_results = []
    forecasts_by_cutoff = {}

    for c in VALID_CUTOFFS:
        selected_fc = select_day_ahead_forecasts(windfor_records, target_date, c)
        intervals = build_hourly_timeseries(target_date, c, hourly_actuals, selected_fc)
        matched_pairs = [(i.forecastMW, i.actualMW) for i in intervals if i.isMatched]
        missing_act = len([i for i in intervals if i.actualMW is None])
        missing_fc = len([i for i in intervals if i.forecastMW is None])

        metrics = calculate_metrics(
            pairs=matched_pairs,
            total_hours=24,
            missing_actual_count=missing_act,
            missing_forecast_count=missing_fc,
            start_date=date_str,
            end_date=date_str,
            cutoff=c
        )

        cutoff_results.append(
            CutoffEvolutionItem(
                cutoff=c,
                matchedHours=metrics["matchedHours"],
                maeMW=metrics["maeMW"],
                rmseMW=metrics["rmseMW"],
                biasMW=metrics["biasMW"],
                biasPct=metrics["biasPct"],
                wapePct=metrics["wapePct"]
            )
        )
        forecasts_by_cutoff[c] = {i.hour: i.forecastMW for i in intervals}

    # Build combined interval comparison table
    combined_intervals = []
    for h in range(24):
        hour_key = f"{date_str}T{h:02d}:00:00Z"
        act_mw, _ = hourly_actuals.get(hour_key, (None, 0))
        item = {
            "hour": h,
            "startTime": hour_key,
            "actualMW": act_mw
        }
        for c in VALID_CUTOFFS:
            c_key = f"fc_{c.replace(':', '')}"
            item[c_key] = forecasts_by_cutoff[c].get(h)
        combined_intervals.append(item)

    return ForecastEvolutionResponse(
        date=date_str,
        cutoffs=cutoff_results,
        intervals=combined_intervals
    )
