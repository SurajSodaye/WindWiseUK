import pytest
from app.client import ElexonAPIError


def test_health_endpoint(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "timestamp" in data
    assert "cachedActualsCount" in data
    assert "cachedForecastsCount" in data


def test_summary_invalid_cutoff(client):
    response = client.get("/api/summary?cutoff=13:00")
    assert response.status_code == 400
    assert "Invalid cutoff '13:00'" in response.json()["detail"]


def test_summary_invalid_dates(client):
    # Invalid date format
    resp1 = client.get("/api/summary?startDate=invalid-date")
    assert resp1.status_code == 400
    assert "Invalid date format" in resp1.json()["detail"]

    # Start date after end date
    resp2 = client.get("/api/summary?startDate=2026-01-20&endDate=2026-01-10")
    assert resp2.status_code == 400
    assert "cannot be later than endDate" in resp2.json()["detail"]


def test_summary_and_metrics_with_cached_data(client, temp_cache, synthetic_fuelhh, synthetic_windfor):
    # Pre-populate cache
    temp_cache.store_fuelhh(synthetic_fuelhh)
    temp_cache.store_windfor(synthetic_windfor)

    # 1. Test /api/summary
    res_summary = client.get("/api/summary?startDate=2026-01-15&endDate=2026-01-15&cutoff=12:00")
    assert res_summary.status_code == 200
    s_data = res_summary.json()
    assert s_data["startDate"] == "2026-01-15"
    assert s_data["endDate"] == "2026-01-15"
    assert s_data["cutoff"] == "12:00"
    assert s_data["totalHours"] == 24
    assert s_data["matchedHours"] == 23  # Hour 2 has missing actual
    assert s_data["missingActualHours"] == 1
    assert s_data["maeMW"] is not None
    assert s_data["rmseMW"] is not None
    assert s_data["biasMW"] is not None
    assert s_data["wapePct"] is not None

    # 2. Test /api/metrics
    res_metrics = client.get("/api/metrics?startDate=2026-01-15&endDate=2026-01-15&cutoff=12:00")
    assert res_metrics.status_code == 200
    m_data = res_metrics.json()
    assert "summary" in m_data
    assert "dailyMetrics" in m_data
    assert len(m_data["dailyMetrics"]) == 1
    assert m_data["dailyMetrics"][0]["date"] == "2026-01-15"


def test_timeseries_endpoint(client, temp_cache, synthetic_fuelhh, synthetic_windfor):
    temp_cache.store_fuelhh(synthetic_fuelhh)
    temp_cache.store_windfor(synthetic_windfor)

    res = client.get("/api/timeseries?date=2026-01-15&cutoff=12:00")
    assert res.status_code == 200
    data = res.json()
    assert data["date"] == "2026-01-15"
    assert data["cutoff"] == "12:00"
    assert len(data["intervals"]) == 24
    assert "daySummary" in data

    # Check publication timestamps are included
    hour_0 = data["intervals"][0]
    assert hour_0["startTime"] == "2026-01-15T00:00:00Z"
    assert hour_0["forecastPublishTime"] == "2026-01-14T11:30:00Z"
    assert hour_0["actualMW"] == 1100.0
    assert hour_0["forecastMW"] == 1050.0
    assert hour_0["errorMW"] == -50.0


def test_forecast_evolution_endpoint(client, temp_cache, synthetic_fuelhh, synthetic_windfor):
    temp_cache.store_fuelhh(synthetic_fuelhh)
    temp_cache.store_windfor(synthetic_windfor)

    res = client.get("/api/forecast-evolution?date=2026-01-15")
    assert res.status_code == 200
    data = res.json()
    assert data["date"] == "2026-01-15"
    assert len(data["cutoffs"]) == 5  # 09:00, 11:00, 12:00, 14:00, 17:00
    assert len(data["intervals"]) == 24
    assert "fc_0900" in data["intervals"][0]
    assert "fc_1200" in data["intervals"][0]


def test_api_network_error_propagation(client, temp_cache):
    # Simulate failed API client when cache is completely empty
    from app.dependencies import get_elexon_client

    class FailingClient:
        async def fetch_fuelhh(self, *args, **kwargs):
            raise ElexonAPIError("Elexon server down", status_code=500)

        async def fetch_windfor(self, *args, **kwargs):
            raise ElexonAPIError("Elexon server down", status_code=500)

    from app.main import app
    app.dependency_overrides[get_elexon_client] = lambda: FailingClient()

    try:
        res = client.get("/api/summary?startDate=2026-01-15&endDate=2026-01-15&cutoff=12:00")
        assert res.status_code == 502
        assert "Failed to fetch" in res.json()["detail"]
    finally:
        app.dependency_overrides.pop(get_elexon_client, None)
