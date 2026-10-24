import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.main import app
from app.cache import CacheDatabase
from app.dependencies import get_cache_db, get_elexon_client
from app.client import ElexonClient


@pytest.fixture
def temp_cache(tmp_path):
    """Provide a clean isolated SQLite database for each test."""
    db_file = tmp_path / "test_windwise.db"
    cache = CacheDatabase(str(db_file))
    return cache


@pytest.fixture
def mock_client():
    """Mock Elexon Client for offline deterministic testing."""
    class DummyElexonClient:
        async def fetch_fuelhh(self, *args, **kwargs):
            return []

        async def fetch_windfor(self, *args, **kwargs):
            return []

    return DummyElexonClient()


@pytest.fixture
def client(temp_cache, mock_client):
    """FastAPI TestClient with overridden test dependencies."""
    app.dependency_overrides[get_cache_db] = lambda: temp_cache
    app.dependency_overrides[get_elexon_client] = lambda: mock_client
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def synthetic_fuelhh():
    """Synthetic FUELHH records covering 2026-01-15 (periods 1 to 48)."""
    records = []
    # Hour 0: Period 1 (00:00) = 1000 MW, Period 2 (00:30) = 1200 MW -> Expected avg = 1100 MW
    records.append({
        "dataset": "FUELHH",
        "settlementDate": "2026-01-15",
        "settlementPeriod": 1,
        "startTime": "2026-01-15T00:00:00Z",
        "publishTime": "2026-01-15T00:30:00Z",
        "fuelType": "WIND",
        "generation": 1000.0
    })
    records.append({
        "dataset": "FUELHH",
        "settlementDate": "2026-01-15",
        "settlementPeriod": 2,
        "startTime": "2026-01-15T00:30:00Z",
        "publishTime": "2026-01-15T01:00:00Z",
        "fuelType": "WIND",
        "generation": 1200.0
    })
    # Hour 1: Complete (1400 and 1600 MW -> Expected avg = 1500 MW)
    records.append({
        "dataset": "FUELHH",
        "settlementDate": "2026-01-15",
        "settlementPeriod": 3,
        "startTime": "2026-01-15T01:00:00Z",
        "publishTime": "2026-01-15T01:30:00Z",
        "fuelType": "WIND",
        "generation": 1400.0
    })
    records.append({
        "dataset": "FUELHH",
        "settlementDate": "2026-01-15",
        "settlementPeriod": 4,
        "startTime": "2026-01-15T01:30:00Z",
        "publishTime": "2026-01-15T02:00:00Z",
        "fuelType": "WIND",
        "generation": 1600.0
    })
    # Hour 2: Incomplete (Only period 5 at 02:00 is present, period 6 is missing)
    records.append({
        "dataset": "FUELHH",
        "settlementDate": "2026-01-15",
        "settlementPeriod": 5,
        "startTime": "2026-01-15T02:00:00Z",
        "publishTime": "2026-01-15T02:30:00Z",
        "fuelType": "WIND",
        "generation": 1800.0
    })
    # Hours 3 to 23: Complete periods
    for h in range(3, 24):
        p1 = 2 * h + 1
        p2 = 2 * h + 2
        base_gen = 2000.0 + h * 100.0
        records.append({
            "dataset": "FUELHH",
            "settlementDate": "2026-01-15",
            "settlementPeriod": p1,
            "startTime": f"2026-01-15T{h:02d}:00:00Z",
            "publishTime": f"2026-01-15T{h:02d}:30:00Z",
            "fuelType": "WIND",
            "generation": base_gen
        })
        records.append({
            "dataset": "FUELHH",
            "settlementDate": "2026-01-15",
            "settlementPeriod": p2,
            "startTime": f"2026-01-15T{h:02d}:30:00Z",
            "publishTime": f"2026-01-15T{h+1:02d}:00:00Z" if h < 23 else "2026-01-16T00:00:00Z",
            "fuelType": "WIND",
            "generation": base_gen + 100.0
        })
    return records


@pytest.fixture
def synthetic_windfor():
    """Synthetic WINDFOR forecasts published before and after cutoff."""
    records = []
    # For target day 2026-01-15, D-1 is 2026-01-14
    # Cutoff 12:00 UTC -> cutoff timestamp is 2026-01-14T12:00:00Z
    
    # Run 1: Published at 07:30 UTC on 2026-01-14 (Eligible, but earlier)
    for h in range(24):
        records.append({
            "dataset": "WINDFOR",
            "startTime": f"2026-01-15T{h:02d}:00:00Z",
            "publishTime": "2026-01-14T07:30:00Z",
            "generation": 900.0 + h * 50.0  # Old forecast
        })

    # Run 2: Published at 11:30 UTC on 2026-01-14 (Eligible, latest before 12:00 cutoff)
    for h in range(24):
        records.append({
            "dataset": "WINDFOR",
            "startTime": f"2026-01-15T{h:02d}:00:00Z",
            "publishTime": "2026-01-14T11:30:00Z",
            "generation": 1050.0 + h * 100.0  # Latest eligible forecast
        })

    # Run 3: Published at 15:30 UTC on 2026-01-14 (AFTER 12:00 cutoff -> MUST BE EXCLUDED for 12:00 cutoff)
    for h in range(24):
        records.append({
            "dataset": "WINDFOR",
            "startTime": f"2026-01-15T{h:02d}:00:00Z",
            "publishTime": "2026-01-14T15:30:00Z",
            "generation": 9999.0  # Trap value
        })

    return records
