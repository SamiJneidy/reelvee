import os

from app.core.config import settings

_geoip_reader = None
_geoip_initialized = False

import geoip2.database

def _get_geoip_reader():
    global _geoip_reader, _geoip_initialized
    if _geoip_initialized:
        return _geoip_reader
    _geoip_initialized = True
    db_path = settings.geoip_db_path
    if db_path and os.path.exists(db_path):
        try:

            _geoip_reader = geoip2.database.Reader(db_path)
        except Exception:
            _geoip_reader = None
    return _geoip_reader


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
