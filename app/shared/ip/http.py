from starlette.requests import Request


def get_client_ip_from_request(request: Request) -> str:
    """Best-effort client IP (respects X-Forwarded-For when behind a proxy)."""
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    if request.client:
        return request.client.host
    return "unknown"
