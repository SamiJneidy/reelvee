import user_agents

from app.core.enums import OSType


def is_likely_bot(user_agent: str | None) -> bool:
    if not user_agent:
        return False
    return user_agents.parse(user_agent).is_bot


def parse_os_from_user_agent(user_agent: str | None) -> OSType:
    if not user_agent:
        return OSType.unknown
    ua = user_agents.parse(user_agent)
    if ua.is_bot:
        return OSType.unknown
    family = ua.os.family.lower()
    if "ios" in family or "iphone" in family or "ipad" in family:
        return OSType.ios
    if "android" in family:
        return OSType.android
    if "windows" in family:
        return OSType.windows
    if "mac os" in family:
        return OSType.macos
    if "linux" in family:
        return OSType.linux
    return OSType.unknown
