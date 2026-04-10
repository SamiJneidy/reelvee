from fastapi import Request

from app.shared.ip.geo import resolve_country_iso_from_ip
from app.shared.ip.http import get_client_ip_from_request
from app.shared.ip.schemas import IPMetadata
from app.shared.ip.user_agent import is_likely_bot, parse_os_from_user_agent


async def get_ip_metadata(request: Request) -> IPMetadata:
    """Resolve IP, country (GeoIP), OS (User-Agent), and bot flag for the current request."""
    client_ip = get_client_ip_from_request(request)
    ua = request.headers.get("User-Agent")
    return IPMetadata(
        client_ip=client_ip,
        country_code=resolve_country_iso_from_ip(client_ip),
        os_type=parse_os_from_user_agent(ua),
        is_bot=is_likely_bot(ua),
        user_agent=ua,
    )
