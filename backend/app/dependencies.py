from app.config import CACHE_DB_PATH
from app.cache import CacheDatabase
from app.client import ElexonClient


def get_cache_db() -> CacheDatabase:
    """Dependency provider for the SQLite cache database."""
    return CacheDatabase(CACHE_DB_PATH)


def get_elexon_client() -> ElexonClient:
    """Dependency provider for the Elexon API client."""
    return ElexonClient()
