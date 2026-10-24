from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Tuple, Optional
from collections import defaultdict

from app.schemas import HourlyInterval, DailyMetrics, MetricsSummary
from app.metrics import calculate_metrics


def parse_date_range(start_date_str: str, end_date_str: str) -> List[date]:
    """Return a list of dates from start_date to end_date inclusive."""
    start = date.fromisoformat(start_date_str)
    end = date.fromisoformat(end_date_str)
    if start > end:
        raise ValueError(f"startDate ({start_date_str}) cannot be after endDate ({end_date_str})")
    
    dates = []
    curr = start
    while curr <= end:
        dates.append(curr)
        curr += timedelta(days=1)
    return dates


def aggregate_hourly_actuals(fuelhh_records: List[Dict[str, Any]]) -> Dict[str, Tuple[Optional[float], int]]:
    """
    Aggregate half-hourly FUELHH records into hourly actual generation.
    Returns dict mapping hour start ISO timestamp (YYYY-MM-DDTHH:00:00Z) to (average_mw, periods_count).
    Only computes average MW if BOTH half-hour periods (at :00 and :30) are present.
    """
    # Group by (settlementDate, hour)
    buckets = defaultdict(dict)
    for r in fuelhh_records:
        st = r["startTime"]  # e.g. 2026-01-01T00:30:00Z
        try:
            minute = st[14:16]
            hour_key = st[:13] + ":00:00Z"
            buckets[hour_key][minute] = float(r["generation"])
        except (IndexError, ValueError):
            continue

    hourly_actuals = {}
    for hour_key, minutes_dict in buckets.items():
        count = len(minutes_dict)
        if count == 2 and "00" in minutes_dict and "30" in minutes_dict:
            avg_mw = round((minutes_dict["00"] + minutes_dict["30"]) / 2.0, 2)
            hourly_actuals[hour_key] = (avg_mw, 2)
        else:
            # Missing one or more periods in the hour
            hourly_actuals[hour_key] = (None, count)

    return hourly_actuals


def select_day_ahead_forecasts(
    windfor_records: List[Dict[str, Any]],
    target_date: date,
    cutoff_time: str = "12:00"
) -> Dict[str, Tuple[float, str]]:
    """
    Select the latest eligible WINDFOR forecast for each hour of target_date.
    
    Cutoff Rule:
      - Delivery day D = target_date
      - Cutoff timestamp = (D - 1 day) at cutoff_time UTC (e.g. 2026-01-14T12:00:00Z)
      - Forecasts published after cutoff_timestamp are strictly excluded.
      - If multiple eligible forecasts exist for target hour t, select the one with latest publishTime.
    
    Returns dict mapping hour start timestamp (YYYY-MM-DDTHH:00:00Z) to (generation, publishTime).
    """
    prev_date = target_date - timedelta(days=1)
    cutoff_timestamp = f"{prev_date.isoformat()}T{cutoff_time}:00Z"
    target_date_str = target_date.isoformat()

    # Filter eligible forecasts
    eligible = [
        f for f in windfor_records
        if f["publishTime"] <= cutoff_timestamp and f["startTime"].startswith(target_date_str)
    ]

    # Sort ascending by publishTime so that later publications overwrite earlier ones
    eligible.sort(key=lambda x: x["publishTime"])

    selected = {}
    for f in eligible:
        st = f["startTime"]  # e.g. 2026-01-15T10:00:00Z
        selected[st] = (float(f["generation"]), f["publishTime"])

    return selected


def build_hourly_timeseries(
    target_date: date,
    cutoff_time: str,
    hourly_actuals: Dict[str, Tuple[Optional[float], int]],
    selected_forecasts: Dict[str, Tuple[float, str]]
) -> List[HourlyInterval]:
    """Build the 24 hourly intervals for a single delivery day."""
    intervals = []
    target_date_str = target_date.isoformat()

    for h in range(24):
        hour_start = f"{target_date_str}T{h:02d}:00:00Z"
        
        # Actuals
        actual_data = hourly_actuals.get(hour_start, (None, 0))
        actual_mw, actual_count = actual_data

        # Forecasts
        fc_data = selected_forecasts.get(hour_start)
        forecast_mw = fc_data[0] if fc_data else None
        forecast_pub_time = fc_data[1] if fc_data else None

        # Matching & Error
        if actual_mw is not None and forecast_mw is not None:
            is_matched = True
            error_mw = round(forecast_mw - actual_mw, 2)
            abs_error_mw = round(abs(error_mw), 2)
        else:
            is_matched = False
            error_mw = None
            abs_error_mw = None

        intervals.append(
            HourlyInterval(
                startTime=hour_start,
                settlementDate=target_date_str,
                hour=h,
                actualMW=actual_mw,
                actualPeriodsCount=actual_count,
                forecastMW=forecast_mw,
                forecastPublishTime=forecast_pub_time,
                errorMW=error_mw,
                absoluteErrorMW=abs_error_mw,
                isMatched=is_matched
            )
        )

    return intervals


def process_date_range(
    start_date_str: str,
    end_date_str: str,
    cutoff_time: str,
    fuelhh_records: List[Dict[str, Any]],
    windfor_records: List[Dict[str, Any]]
) -> Tuple[MetricsSummary, List[DailyMetrics], List[HourlyInterval]]:
    """
    Process full date range:
    1. Parse dates
    2. Aggregate actuals
    3. Select forecasts per day at the configured cutoff
    4. Compile all hourly intervals
    5. Compute summary metrics and daily breakdown
    """
    target_dates = parse_date_range(start_date_str, end_date_str)
    hourly_actuals = aggregate_hourly_actuals(fuelhh_records)

    all_intervals: List[HourlyInterval] = []
    daily_metrics_list: List[DailyMetrics] = []
    matched_pairs: List[Tuple[float, float]] = []

    missing_actual_hours = 0
    missing_forecast_hours = 0

    for d in target_dates:
        d_str = d.isoformat()
        fc_for_day = select_day_ahead_forecasts(windfor_records, d, cutoff_time)
        day_intervals = build_hourly_timeseries(d, cutoff_time, hourly_actuals, fc_for_day)
        all_intervals.extend(day_intervals)

        day_pairs = []
        for interval in day_intervals:
            if interval.actualMW is None:
                missing_actual_hours += 1
            if interval.forecastMW is None:
                missing_forecast_hours += 1
            if interval.isMatched:
                day_pairs.append((interval.forecastMW, interval.actualMW))
                matched_pairs.append((interval.forecastMW, interval.actualMW))

        # Daily metrics
        d_res = calculate_metrics(
            pairs=day_pairs,
            total_hours=24,
            missing_actual_count=24 - len([i for i in day_intervals if i.actualMW is not None]),
            missing_forecast_count=24 - len([i for i in day_intervals if i.forecastMW is not None]),
            start_date=d_str,
            end_date=d_str,
            cutoff=cutoff_time
        )
        daily_metrics_list.append(
            DailyMetrics(
                date=d_str,
                totalHours=24,
                matchedHours=d_res["matchedHours"],
                meanActualMW=d_res["meanActualMW"],
                meanForecastMW=d_res["meanForecastMW"],
                maeMW=d_res["maeMW"],
                rmseMW=d_res["rmseMW"],
                biasMW=d_res["biasMW"],
                biasPct=d_res["biasPct"],
                wapePct=d_res["wapePct"]
            )
        )

    total_hours = len(target_dates) * 24
    summary_data = calculate_metrics(
        pairs=matched_pairs,
        total_hours=total_hours,
        missing_actual_count=missing_actual_hours,
        missing_forecast_count=missing_forecast_hours,
        start_date=start_date_str,
        end_date=end_date_str,
        cutoff=cutoff_time
    )

    summary = MetricsSummary(**summary_data)
    return summary, daily_metrics_list, all_intervals
