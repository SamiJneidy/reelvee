from typing import Annotated

from fastapi import Depends

from app.modules.users.dependencies import UserService, get_user_service
from app.modules.auth.tokens.dependencies import TokenService, get_token_service
from app.modules.auth.google.service import GoogleAuthService

def get_google_auth_service(
    user_service: Annotated[UserService, Depends(get_user_service)],
    token_service: Annotated[TokenService, Depends(get_token_service)],
) -> GoogleAuthService:
    return GoogleAuthService(user_service=user_service, token_service=token_service)
