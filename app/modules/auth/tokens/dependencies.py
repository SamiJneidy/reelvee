from fastapi import Depends
from typing import Annotated
from .repository import TokenRepository
from .service import TokenService

def get_token_repository() -> TokenRepository:
    return TokenRepository()


def get_token_service(
    token_repo: Annotated[TokenRepository, Depends(get_token_repository)],
) -> TokenService:
    return TokenService(token_repo)
