from app.core.config import settings

def get_full_store_url(store_url: str) -> str:
    return f"{settings.frontend_url}/@{store_url}"