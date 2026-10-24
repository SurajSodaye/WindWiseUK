from datetime import date
from app.processing import (
    select_day_ahead_forecasts,
    aggregate_hourly_actuals,
    build_hourly_timeseries,
    process_date_range
)


def test_cutoff_boundary_inclusion_and_exclusion():
    target_date = date(2026, 1, 15)
    # Cutoff 12:00 -> cutoff timestamp is 2026-01-14T12:00:00Z
    records = [
        # 1 second before cutoff: ELIGIBLE
        {
            "dataset": "WINDFOR",
            "startTime": "2026-01-15T10:00:00Z",
            "publishTime": "2026-01-14T11:59:59Z",
            "generation": 500.0
        },
        # Exactly on cutoff: ELIGIBLE and latest so far
        {
            "dataset": "WINDFOR",
            "startTime": "2026-01-15T10:00:00Z",
            "publishTime": "2026-01-14T12:00:00Z",
            "generation": 600.0
        },
        # 1 second after cutoff: STRICTLY EXCLUDED
        {
            "dataset": "WINDFOR",
            "startTime": "2026-01-15T10:00:00Z",
            "publishTime": "2026-01-14T12:00:01Z",
            "generation": 700.0
        },
        # 3.5 hours after cutoff: STRICTLY EXCLUDED
        {
            "dataset": "WINDFOR",
            "startTime": "2026-01-15T10:00:00Z",
            "publishTime": "2026-01-14T15:30:00Z",
            "generation": 9999.0
        }
    ]

    selected = select_day_ahead_forecasts(records, target_date, cutoff_time="12:00")
    
    # Must pick the exact 12:00:00Z record (600.0 MW), NOT 700.0 or 9999.0
    assert "2026-01-15T10:00:00Z" in selected
    gen, pub_time = selected["2026-01-15T10:00:00Z"]
    assert gen == 600.0
    assert pub_time == "2026-01-14T12:00:00Z"


def test_latest_eligible_forecast_selection(synthetic_windfor):
    target_date = date(2026, 1, 15)
    # Under 12:00 cutoff, synthetic_windfor has runs at 07:30, 11:30, and 15:30
    selected = select_day_ahead_forecasts(synthetic_windfor, target_date, cutoff_time="12:00")

    # Hour 0: Run at 07:30 has gen=900, run at 11:30 has gen=1050, run at 15:30 has gen=9999
    # The selected should be 1050 with publishTime 11:30:00Z
    assert "2026-01-15T00:00:00Z" in selected
    gen, pub = selected["2026-01-15T00:00:00Z"]
    assert gen == 1050.0
    assert pub == "2026-01-14T11:30:00Z"


def test_hourly_actual_aggregation_complete_and_incomplete(synthetic_fuelhh):
    actuals = aggregate_hourly_actuals(synthetic_fuelhh)

    # Hour 0: Period 1 (1000) and Period 2 (1200) -> Both present -> Avg = 1100.0
    hour_0 = "2026-01-15T00:00:00Z"
    assert hour_0 in actuals
    avg_mw, count = actuals[hour_0]
    assert avg_mw == 1100.0
    assert count == 2

    # Hour 1: Period 3 (1400) and Period 4 (1600) -> Both present -> Avg = 1500.0
    hour_1 = "2026-01-15T01:00:00Z"
    avg_mw1, count1 = actuals[hour_1]
    assert avg_mw1 == 1500.0
    assert count1 == 2

    # Hour 2: Incomplete (Only period 5 present, period 6 missing) -> MUST BE None, count = 1
    hour_2 = "2026-01-15T02:00:00Z"
    avg_mw2, count2 = actuals[hour_2]
    assert avg_mw2 is None
    assert count2 == 1


def test_missing_intervals_preserved_in_timeseries(synthetic_fuelhh, synthetic_windfor):
    target_date = date(2026, 1, 15)
    actuals = aggregate_hourly_actuals(synthetic_fuelhh)
    selected_fc = select_day_ahead_forecasts(synthetic_windfor, target_date, "12:00")
    intervals = build_hourly_timeseries(target_date, "12:00", actuals, selected_fc)

    assert len(intervals) == 24

    # Hour 0: Matched (Actual = 1100.0, Forecast = 1050.0)
    # Error = Forecast - Actual = 1050 - 1100 = -50.0
    assert intervals[0].isMatched is True
    assert intervals[0].actualMW == 1100.0
    assert intervals[0].forecastMW == 1050.0
    assert intervals[0].errorMW == -50.0
    assert intervals[0].absoluteErrorMW == 50.0

    # Hour 2: Actual is missing because period 6 was missing -> Must NOT be zero!
    assert intervals[2].isMatched is False
    assert intervals[2].actualMW is None
    assert intervals[2].errorMW is None
    assert intervals[2].absoluteErrorMW is None
    assert intervals[2].forecastMW is not None  # Forecast exists, but unmatched


def test_process_date_range_data_quality_counts(synthetic_fuelhh, synthetic_windfor):
    summary, daily, intervals = process_date_range(
        start_date_str="2026-01-15",
        end_date_str="2026-01-15",
        cutoff_time="12:00",
        fuelhh_records=synthetic_fuelhh,
        windfor_records=synthetic_windfor
    )

    assert summary.totalHours == 24
    # Hour 2 is missing actual, so 23 matched hours, 1 missing actual hour, 0 missing forecast
    assert summary.matchedHours == 23
    assert summary.missingActualHours == 1
    assert summary.missingForecastHours == 0
    assert summary.maeMW is not None
    assert summary.biasMW is not None
    assert summary.wapePct is not None
