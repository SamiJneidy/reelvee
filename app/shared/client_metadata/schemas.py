from dataclasses import dataclass

from app.core.enums import OSType


@dataclass(frozen=True, slots=True)
class ClientRequestMetadata:
    """Parsed client info from HTTP request (IP, GeoIP, User-Agent).

    Built by `get_client_request_metadata` dependency; safe to pass into
    BackgroundTasks (unlike the raw Request object).
    """

    client_ip: str
    country_code: str
    os_type: OSType
    is_bot: bool
    user_agent: str | None = None
