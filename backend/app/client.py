import logging
from typing import List, Dict, Any, Optional
import httpx
from app.config import ELEXON_BASE_URL, ELEXON_TIMEOUT_SECONDS

logger = logging.getLogger(__name__)


class ElexonAPIError(Exception):
    """Raised when Elexon API requests fail."""
    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.status_code = status_code


class ElexonClient:
    """Client for fetching datasets from Elexon Insights Solution (BMRS API v1)."""

    def __init__(self, base_url: str = ELEXON_BASE_URL, timeout: float = ELEXON_TIMEOUT_SECONDS):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.headers = {
            "User-Agent": "WindWiseUK-Dashboard/1.0",
            "Accept": "application/json",
        }

    async def fetch_fuelhh(
        self,
        settlement_date_from: str,
        settlement_date_to: str,
        fuel_type: str = "WIND"
    ) -> List[Dict[str, Any]]:
        """
        Fetch half-hourly generation outturn (FUELHH stream) filtered by fuelType.
        settlement_date_from/to format: YYYY-MM-DD
        """
        url = f"{self.base_url}/datasets/FUELHH/stream"
        params = {
            "settlementDateFrom": settlement_date_from,
            "settlementDateTo": settlement_date_to,
            "fuelType": fuel_type,
        }
        
        logger.info(f"Fetching FUELHH from {settlement_date_from} to {settlement_date_to} (fuelType={fuel_type})")
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(url, params=params, headers=self.headers)
                if response.status_code != 200:
                    raise ElexonAPIError(
                        f"Elexon API error {response.status_code}: {response.text[:200]}",
                        status_code=response.status_code
                    )
                data = response.json()
                if not isinstance(data, list):
                    raise ElexonAPIError(f"Unexpected response format: expected list, got {type(data)}")
                return data
            except httpx.RequestError as exc:
                raise ElexonAPIError(f"Network error querying Elexon FUELHH: {str(exc)}")

    async def fetch_windfor(
        self,
        publish_datetime_from: str,
        publish_datetime_to: str
    ) -> List[Dict[str, Any]]:
        """
        Fetch wind generation forecasts (WINDFOR stream).
        publish_datetime_from/to format: ISO 8601 UTC (e.g. 2025-12-31T00:00:00Z)
        """
        url = f"{self.base_url}/datasets/WINDFOR/stream"
        params = {
            "publishDateTimeFrom": publish_datetime_from,
            "publishDateTimeTo": publish_datetime_to,
        }
        
        logger.info(f"Fetching WINDFOR from {publish_datetime_from} to {publish_datetime_to}")
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(url, params=params, headers=self.headers)
                if response.status_code != 200:
                    raise ElexonAPIError(
                        f"Elexon API error {response.status_code}: {response.text[:200]}",
                        status_code=response.status_code
                    )
                data = response.json()
                if not isinstance(data, list):
                    raise ElexonAPIError(f"Unexpected response format: expected list, got {type(data)}")
                return data
            except httpx.RequestError as exc:
                raise ElexonAPIError(f"Network error querying Elexon WINDFOR: {str(exc)}")
