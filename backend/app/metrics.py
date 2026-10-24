import math
from typing import List, Optional, Tuple, Dict, Any


def calculate_metrics(
    pairs: List[Tuple[float, float]],
    total_hours: int,
    missing_actual_count: int,
    missing_forecast_count: int,
    start_date: str = "",
    end_date: str = "",
    cutoff: str = ""
) -> Dict[str, Any]:
    """
    Calculate verification metrics on matched (forecast, actual) pairs.
    
    Formula definitions:
      - MAE = (1/N) * sum(|F_i - A_i|)
      - RMSE = sqrt((1/N) * sum((F_i - A_i)^2))
      - Forecast Bias = (1/N) * sum(F_i - A_i)
      - Bias % = (Bias / Mean(A)) * 100
      - WAPE = sum(|F_i - A_i|) / sum(A_i) * 100
    
    Handles zero denominators and missing observations safely.
    """
    n = len(pairs)
    matched_count = n

    if n == 0:
        return {
            "startDate": start_date,
            "endDate": end_date,
            "cutoff": cutoff,
            "totalHours": total_hours,
            "matchedHours": 0,
            "missingActualHours": missing_actual_count,
            "missingForecastHours": missing_forecast_count,
            "meanActualMW": None,
            "meanForecastMW": None,
            "totalActualGWh": None,
            "totalForecastGWh": None,
            "maeMW": None,
            "rmseMW": None,
            "biasMW": None,
            "biasPct": None,
            "wapePct": None,
        }

    sum_abs_err = 0.0
    sum_sq_err = 0.0
    sum_err = 0.0
    sum_actual = 0.0
    sum_forecast = 0.0

    for forecast, actual in pairs:
        err = forecast - actual
        sum_err += err
        sum_abs_err += abs(err)
        sum_sq_err += err ** 2
        sum_actual += actual
        sum_forecast += forecast

    mae = round(sum_abs_err / n, 2)
    rmse = round(math.sqrt(sum_sq_err / n), 2)
    bias = round(sum_err / n, 2)
    mean_actual = round(sum_actual / n, 2)
    mean_forecast = round(sum_forecast / n, 2)

    # Bias % relative to mean actual generation
    if mean_actual > 0:
        bias_pct = round((bias / mean_actual) * 100.0, 2)
    elif mean_actual == 0:
        bias_pct = 0.0 if bias == 0 else None
    else:
        bias_pct = None

    # WAPE in percent
    if sum_actual > 0:
        wape_pct = round((sum_abs_err / sum_actual) * 100.0, 2)
    elif sum_actual == 0:
        wape_pct = 0.0 if sum_abs_err == 0 else None
    else:
        wape_pct = None

    # Total energy: each interval is 1 hour, so MW * 1h = MWh, / 1000 = GWh
    total_actual_gwh = round(sum_actual / 1000.0, 2)
    total_forecast_gwh = round(sum_forecast / 1000.0, 2)

    return {
        "startDate": start_date,
        "endDate": end_date,
        "cutoff": cutoff,
        "totalHours": total_hours,
        "matchedHours": matched_count,
        "missingActualHours": missing_actual_count,
        "missingForecastHours": missing_forecast_count,
        "meanActualMW": mean_actual,
        "meanForecastMW": mean_forecast,
        "totalActualGWh": total_actual_gwh,
        "totalForecastGWh": total_forecast_gwh,
        "maeMW": mae,
        "rmseMW": rmse,
        "biasMW": bias,
        "biasPct": bias_pct,
        "wapePct": wape_pct,
    }
