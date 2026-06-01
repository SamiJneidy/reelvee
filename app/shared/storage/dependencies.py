from functools import lru_cache
from app.shared.storage.service import StorageService

_storage_service: StorageService | None = None
_s3_client = None

def init_s3_client(s3_client) -> None:
    """Call once from the application lifespan with the live S3 client."""
    global _s3_client
    _s3_client = s3_client

@lru_cache
def get_storage_service() -> StorageService:
    return StorageService(_s3_client)
