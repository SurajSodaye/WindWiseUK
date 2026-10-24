import sqlite3
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Tuple
from app.config import CACHE_DB_PATH

logger = logging.getLogger(__name__)


class CacheDatabase:
    """SQLite cache for storing and quickly retrieving Elexon actuals and forecasts."""

    def __init__(self, db_path: str = CACHE_DB_PATH):
        self.db_path = db_path
        self._ensure_dir()
        self.init_db()

    def _ensure_dir(self):
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        """Initialize SQLite tables and indexes."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # Table for FUELHH actuals
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS fuelhh (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    dataset TEXT NOT NULL,
                    settlementDate TEXT NOT NULL,
                    settlementPeriod INTEGER NOT NULL,
                    startTime TEXT NOT NULL,
                    publishTime TEXT NOT NULL,
                    fuelType TEXT NOT NULL,
                    generation REAL NOT NULL,
                    UNIQUE(startTime, fuelType)
                )
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_fuelhh_date ON fuelhh(settlementDate, fuelType)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_fuelhh_start ON fuelhh(startTime)")

            # Table for WINDFOR forecasts
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS windfor (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    dataset TEXT NOT NULL,
                    startTime TEXT NOT NULL,
                    publishTime TEXT NOT NULL,
                    generation REAL NOT NULL,
                    UNIQUE(startTime, publishTime)
                )
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_windfor_start ON windfor(startTime)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_windfor_publish ON windfor(publishTime)")
            conn.commit()

    def store_fuelhh(self, records: List[Dict[str, Any]]) -> int:
        """Insert or replace FUELHH records."""
        if not records:
            return 0
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.executemany("""
                INSERT INTO fuelhh (dataset, settlementDate, settlementPeriod, startTime, publishTime, fuelType, generation)
                VALUES (:dataset, :settlementDate, :settlementPeriod, :startTime, :publishTime, :fuelType, :generation)
                ON CONFLICT(startTime, fuelType) DO UPDATE SET
                    generation = excluded.generation,
                    publishTime = excluded.publishTime,
                    settlementPeriod = excluded.settlementPeriod
            """, records)
            conn.commit()
            return cursor.rowcount

    def store_windfor(self, records: List[Dict[str, Any]]) -> int:
        """Insert or replace WINDFOR records."""
        if not records:
            return 0
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.executemany("""
                INSERT INTO windfor (dataset, startTime, publishTime, generation)
                VALUES (:dataset, :startTime, :publishTime, :generation)
                ON CONFLICT(startTime, publishTime) DO UPDATE SET
                    generation = excluded.generation
            """, records)
            conn.commit()
            return cursor.rowcount

    def get_fuelhh(self, start_date: str, end_date: str, fuel_type: str = "WIND") -> List[Dict[str, Any]]:
        """Retrieve FUELHH records within the settlement date range."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT dataset, settlementDate, settlementPeriod, startTime, publishTime, fuelType, generation
                FROM fuelhh
                WHERE settlementDate >= ? AND settlementDate <= ? AND fuelType = ?
                ORDER BY startTime ASC
            """, (start_date, end_date, fuel_type))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def get_windfor(self, publish_from: str, publish_to: str) -> List[Dict[str, Any]]:
        """Retrieve WINDFOR forecasts published in the given range."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT dataset, startTime, publishTime, generation
                FROM windfor
                WHERE publishTime >= ? AND publishTime <= ?
                ORDER BY publishTime ASC, startTime ASC
            """, (publish_from, publish_to))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def get_cached_counts(self) -> Tuple[int, int]:
        """Return counts of cached FUELHH and WINDFOR records."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM fuelhh")
            f_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM windfor")
            w_count = cursor.fetchone()[0]
            return f_count, w_count

    def clear(self):
        """Clear all cached records (useful for testing)."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM fuelhh")
            cursor.execute("DELETE FROM windfor")
            conn.commit()
