from fastapi import Request

from app.shared.client_metadata.geo import resolve_country_iso_from_ip
from app.shared.client_metadata.http import get_client_ip_from_request
from app.shared.client_metadata.schemas import ClientRequestMetadata
from app.shared.client_metadata.user_agent import is_likely_bot, parse_os_from_user_agent


async def get_client_request_metadata(request: Request) -> ClientRequestMetadata:
    """Resolve IP, country (GeoIP), OS (User-Agent), and bot flag for the current request."""
    client_ip = get_client_ip_from_request(request)
    ua = request.headers.get("User-Agent")
    return ClientRequestMetadata(
        client_ip=client_ip,
        country_code=resolve_country_iso_from_ip(client_ip),
        os_type=parse_os_from_user_agent(ua),
        is_bot=is_likely_bot(ua),
        user_agent=ua,
    )
