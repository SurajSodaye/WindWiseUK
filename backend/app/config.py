import os
from pathlib import Path
from typing import List

# Base directory for backend
BASE_DIR = Path(__file__).resolve().parent.parent

# Elexon Insights Solution (BMRS) API Configuration
ELEXON_BASE_URL: str = os.getenv("ELEXON_BASE_URL", "https://data.elexon.co.uk/bmrs/api/v1")
ELEXON_TIMEOUT_SECONDS: float = float(os.getenv("ELEXON_TIMEOUT_SECONDS", "30.0"))

# Cache Database Path (SQLite)
DEFAULT_DB_PATH = BASE_DIR / "windwise_cache.db"
CACHE_DB_PATH: str = os.getenv("CACHE_DB_PATH", str(DEFAULT_DB_PATH))

# Default Day-Ahead Settings
VALID_CUTOFFS: List[str] = ["09:00", "11:00", "12:00", "14:00", "17:00"]
DEFAULT_CUTOFF: str = "12:00"

DEFAULT_START_DATE: str = "2026-01-01"
DEFAULT_END_DATE: str = "2026-01-31"

# CORS Configuration
_env_origins = os.getenv("ALLOWED_ORIGINS", "")
ALLOWED_ORIGINS: List[str] = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
if _env_origins:
    ALLOWED_ORIGINS.extend([origin.strip() for origin in _env_origins.split(",") if origin.strip()])
