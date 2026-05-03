import os
from functools import lru_cache
from app.core.config import settings
from geoip2.database import Reader as GeoIPReader


@lru_cache
def _get_geoip_reader():
    db_path = settings.geoip_db_path
    if db_path and os.path.exists(db_path):
        try:
            return GeoIPReader(db_path)
        except Exception:
            return None
    return None


def resolve_country_iso_from_ip(ip: str) -> str:
    """ISO 3166-1 alpha-2 country code, or \"unknown\" if lookup fails."""
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
