import os
from functools import lru_cache
from app.core.config import settings, PROJECT_ROOT
from geoip2.database import Reader as GeoIPReader


def _resolve_db_path(db_path: str | None) -> str | None:
    if not db_path:
        return None
    if os.path.isabs(db_path):
        return db_path
    # Treat relative paths as relative to the project root, not the CWD.
    return os.path.join(PROJECT_ROOT, db_path)


@lru_cache
def _get_geoip_reader():
    db_path = _resolve_db_path(settings.geoip_db_path)
    if db_path and os.path.exists(db_path):
        try:
            print("Loading GeoIP reader from {db_path}")
            return GeoIPReader(db_path)
        except Exception:
            print("Error loading GeoIP reader from {db_path}")
            return None
    print("Error loading GeoIP reader from {db_path}")
    return None


def resolve_country_iso_from_ip(ip: str) -> str:
    """ISO 3166-1 alpha-2 country code, or "unknown" if lookup fails."""
    if not ip or ip == "unknown":
        return "unknown"
    reader = _get_geoip_reader()
    if reader is None:
        return "unknown"
    try:
        response = reader.country(ip)
        return response.country.iso_code or "unknown"
    except Exception:
        return "unknown"

print("Country code:")
print(resolve_country_iso_from_ip("5.0.52.244"))
print("Project root:")
print(PROJECT_ROOT)