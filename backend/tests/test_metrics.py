import math
import pytest
from app.metrics import calculate_metrics


def test_calculate_metrics_exact_hand_calculated():
    # 4 observations with symmetric errors
    # Pairs: (forecast, actual)
    pairs = [
        (110.0, 100.0),  # err = +10, abs = 10, sq = 100
        (90.0, 100.0),   # err = -10, abs = 10, sq = 100
        (120.0, 100.0),  # err = +20, abs = 20, sq = 400
        (80.0, 100.0),   # err = -20, abs = 20, sq = 400
    ]
    res = calculate_metrics(
        pairs=pairs,
        total_hours=4,
        missing_actual_count=0,
        missing_forecast_count=0,
        start_date="2026-01-01",
        end_date="2026-01-01",
        cutoff="12:00"
    )

    assert res["matchedHours"] == 4
    assert res["missingActualHours"] == 0
    assert res["missingForecastHours"] == 0
    assert res["meanActualMW"] == 100.0
    assert res["meanForecastMW"] == 100.0
    assert res["totalActualGWh"] == 0.4   # 400 MW * 1h / 1000 = 0.4 GWh
    assert res["totalForecastGWh"] == 0.4
    assert res["maeMW"] == 15.0           # 60 / 4
    assert res["rmseMW"] == round(math.sqrt(250.0), 2)  # sqrt(1000/4) = 15.81
    assert res["biasMW"] == 0.0
    assert res["biasPct"] == 0.0
    assert res["wapePct"] == 15.0         # (60 / 400) * 100


def test_forecast_bias_direction():
    # Over-forecasting
    over_pairs = [(150.0, 100.0), (120.0, 100.0)]
    over_res = calculate_metrics(over_pairs, 2, 0, 0)
    assert over_res["biasMW"] == 35.0
    assert over_res["biasPct"] == 35.0

    # Under-forecasting
    under_pairs = [(80.0, 100.0), (70.0, 100.0)]
    under_res = calculate_metrics(under_pairs, 2, 0, 0)
    assert under_res["biasMW"] == -25.0
    assert under_res["biasPct"] == -25.0


def test_zero_denominator_handling():
    # Case 1: Both forecast and actual are zero (perfect calm prediction)
    zero_pairs = [(0.0, 0.0), (0.0, 0.0)]
    res = calculate_metrics(zero_pairs, 2, 0, 0)
    assert res["maeMW"] == 0.0
    assert res["rmseMW"] == 0.0
    assert res["biasMW"] == 0.0
    assert res["biasPct"] == 0.0
    assert res["wapePct"] == 0.0

    # Case 2: Actual is zero, but forecast is non-zero (division by zero guard)
    nonzero_fc_zero_act = [(100.0, 0.0)]
    res2 = calculate_metrics(nonzero_fc_zero_act, 1, 0, 0)
    assert res2["maeMW"] == 100.0
    assert res2["rmseMW"] == 100.0
    assert res2["biasMW"] == 100.0
    assert res2["biasPct"] is None  # Safe handling of zero actual mean
    assert res2["wapePct"] is None  # Safe handling of zero actual sum


def test_empty_dataset_handling():
    res = calculate_metrics(
        pairs=[],
        total_hours=24,
        missing_actual_count=24,
        missing_forecast_count=24
    )
    assert res["matchedHours"] == 0
    assert res["missingActualHours"] == 24
    assert res["missingForecastHours"] == 24
    assert res["maeMW"] is None
    assert res["rmseMW"] is None
    assert res["biasMW"] is None
    assert res["wapePct"] is None
