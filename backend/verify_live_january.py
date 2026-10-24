import asyncio
import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.config import CACHE_DB_PATH
from app.cache import CacheDatabase
from app.client import ElexonClient
from app.processing import process_date_range


async def main():
    print("=== LIVE ELEXON DATA VERIFICATION (JANUARY 2026) ===")
    cache = CacheDatabase(CACHE_DB_PATH)
    client = ElexonClient()

    # 1. Fetch FUELHH for Jan 2026 if not already cached
    cached_actuals = cache.get_fuelhh("2026-01-01", "2026-01-31", fuel_type="WIND")
    if len(cached_actuals) < 1488:
        print(f"Fetching FUELHH actuals from Elexon API (currently cached: {len(cached_actuals)})...")
        live_actuals = await client.fetch_fuelhh("2026-01-01", "2026-01-31", fuel_type="WIND")
        cache.store_fuelhh(live_actuals)
        cached_actuals = cache.get_fuelhh("2026-01-01", "2026-01-31", fuel_type="WIND")
        print(f"Successfully cached {len(cached_actuals)} FUELHH actual records.")
    else:
        print(f"Using {len(cached_actuals)} cached FUELHH records.")

    # 2. Fetch WINDFOR for Jan 2026 (including 2025-12-31 publications)
    pub_from = "2025-12-31T00:00:00Z"
    pub_to = "2026-01-31T23:59:59Z"
    cached_forecasts = cache.get_windfor(pub_from, pub_to)
    if len(cached_forecasts) < 10000:
        print(f"Fetching WINDFOR forecasts from Elexon API (currently cached: {len(cached_forecasts)})...")
        live_forecasts = await client.fetch_windfor(pub_from, pub_to)
        cache.store_windfor(live_forecasts)
        cached_forecasts = cache.get_windfor(pub_from, pub_to)
        print(f"Successfully cached {len(cached_forecasts)} WINDFOR forecast records.")
    else:
        print(f"Using {len(cached_forecasts)} cached WINDFOR records.")

    # 3. Process full January 2026 using backend processing engine at 12:00 UTC cutoff
    print("\nRunning backend processing engine for January 2026 at cutoff 12:00 UTC...")
    summary, daily_metrics, all_intervals = process_date_range(
        start_date_str="2026-01-01",
        end_date_str="2026-01-31",
        cutoff_time="12:00",
        fuelhh_records=cached_actuals,
        windfor_records=cached_forecasts
    )

    print("\n=== VERIFIED RESULT METRICS (12:00 UTC Cutoff) ===")
    print(f"Total Hours: {summary.totalHours}")
    print(f"Matched Hours: {summary.matchedHours}")
    print(f"Missing Actual Hours: {summary.missingActualHours}")
    print(f"Missing Forecast Hours: {summary.missingForecastHours}")
    print(f"Mean Actual Generation: {summary.meanActualMW} MW")
    print(f"Mean Forecast Generation: {summary.meanForecastMW} MW")
    print(f"Total Actual Energy: {summary.totalActualGWh} GWh")
    print(f"Total Forecast Energy: {summary.totalForecastGWh} GWh")
    print(f"MAE: {summary.maeMW} MW")
    print(f"RMSE: {summary.rmseMW} MW")
    print(f"Forecast Bias: {summary.biasMW} MW ({summary.biasPct:+.2f}%)")
    print(f"WAPE: {summary.wapePct}%")

    print("\n=== AUDIT REPORT COMPARISON ===")
    print("Audit Reported Baseline (12:00 UTC):")
    print("  - MAE: 2,017.92 MW")
    print("  - RMSE: 2,477.04 MW")
    print("  - Forecast Bias: +1,806.23 MW (+15.60%)")
    print("  - WAPE: 17.42%")
    print(f"Live Backend Output:")
    print(f"  - MAE: {summary.maeMW} MW")
    print(f"  - RMSE: {summary.rmseMW} MW")
    print(f"  - Forecast Bias: {summary.biasMW} MW ({summary.biasPct:+.2f}%)")
    print(f"  - WAPE: {summary.wapePct}%")

    assert summary.matchedHours == 744, f"Expected 744 matched hours, got {summary.matchedHours}"
    assert summary.maeMW == 2017.92, f"Expected MAE 2017.92, got {summary.maeMW}"
    assert summary.rmseMW == 2477.04, f"Expected RMSE 2477.04, got {summary.rmseMW}"
    assert summary.biasMW == 1806.23, f"Expected Bias 1806.23, got {summary.biasMW}"
    assert summary.wapePct == 17.42, f"Expected WAPE 17.42%, got {summary.wapePct}"
    print("\n>>> ALL VERIFIED LIVE METRICS MATCH THE AUDIT BASELINE WITH 100% MATHEMATICAL PRECISION! <<<")


if __name__ == "__main__":
    asyncio.run(main())
