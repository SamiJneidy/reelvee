import jwt
from datetime import datetime, timedelta, timezone
from fastapi import Request, Response
from app.core.config import settings
from .schemas import AccessToken, RefreshToken, SignUpCompleteToken
from .repository import TokenRepository
from .exceptions import InvalidTokenException


class TokenService:
    
    def __init__(self, token_repo: TokenRepository):
        self.token_repo = token_repo

    def _create_token(self, payload: dict) -> str:
        return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)

    def decode_token(self, token: str) -> dict:  
        try:
            payload_dict: dict = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
            user_id = payload_dict.get("sub")
            if not user_id:
                raise InvalidTokenException()
            return payload_dict
        except jwt.InvalidTokenError:
            raise InvalidTokenException()

    def create_access_token(self, token: AccessToken) -> str:
        token.iat = datetime.now(tz=timezone.utc)
        token.exp = datetime.now(tz=timezone.utc) + timedelta(minutes=settings.access_token_expiration_minutes)
        payload = token.model_dump()
        return self._create_token(payload)


    def create_refresh_token(self, token: RefreshToken) -> str:
        token.iat = datetime.now(tz=timezone.utc)
        token.exp = datetime.now(tz=timezone.utc) + timedelta(days=settings.refresh_token_expiration_days)
        payload = token.model_dump()
        return self._create_token(payload)


    def create_sign_up_complete_token(self, token: SignUpCompleteToken) -> str:
        token.iat = datetime.now(tz=timezone.utc)
        token.exp = datetime.now(tz=timezone.utc) + timedelta(days=settings.sign_up_complete_expiration_days)
        payload = token.model_dump()
        return self._create_token(payload)
    

    def set_token_cookies(self, response: Response, access_token: str, refresh_token: str) -> None:
        self.set_access_token_cookie(response, access_token)
        self.set_refresh_token_cookie(response, refresh_token)


    def set_access_token_cookie(self, request: Request, response: Response, token: str) -> None:
        origin = request.headers.get("origin") or ""
        is_local = origin.startswith("http://localhost") or origin.startswith("http://127.0.0.1")
        secure_flag = settings.environment == "PRODUCTION" and not is_local
        response.set_cookie(
            key="access_token",
            value=token,
            httponly=True,
            secure=secure_flag,
            samesite="lax",
            max_age=settings.access_token_expiration_minutes * 60,
            path="/"
        )


    def set_refresh_token_cookie(self, request: Request, response: Response, token: str) -> None:
        origin = request.headers.get("origin") or ""
        is_local = origin.startswith("http://localhost") or origin.startswith("http://127.0.0.1")
        secure_flag = settings.environment == "PRODUCTION" and not is_local
        response.set_cookie(
            key="refresh_token",
            value=token,
            httponly=True,
            secure=secure_flag,
            samesite="lax",
            max_age=settings.refresh_token_expiration_days * 24 * 60 * 60,
            path="/",
        )

    
    def set_sign_up_complete_token_cookie(self, request: Request, response: Response, token: str) -> None:
        origin = request.headers.get("origin") or ""
        is_local = origin.startswith("http://localhost") or origin.startswith("http://127.0.0.1")
        secure_flag = settings.environment == "PRODUCTION" and not is_local
        response.set_cookie(
            key="sign_up_complete_token",
            value=token,
            httponly=True,
            secure=secure_flag,
            samesite="lax",
            max_age=settings.sign_up_complete_expiration_days * 24 * 60 * 60,
            path="/",
        )
