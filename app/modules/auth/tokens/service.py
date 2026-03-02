import jwt
from datetime import datetime, timedelta, timezone
from app.core.config import settings
from .schemas import AccessToken, EmailChangeToken, PasswordResetToken, RefreshToken, SignUpCompleteToken
from .repository import TokenRepository
from .exceptions import InvalidTokenException


class TokenService:
    
    def __init__(self, token_repo: TokenRepository):
        self.token_repo = token_repo

    def _create_token(self, payload: dict) -> str:
        return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)

    def decode_token(self, token: str) -> dict:  
        """Decode a token and return the payload. It will raise an exception if the token is invalid."""
        try:
            payload_dict: dict = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
            sub = payload_dict.get("sub")
            if not sub:
                raise InvalidTokenException()
            return payload_dict
        except jwt.InvalidTokenError:
            raise InvalidTokenException()
        except Exception as e:
            raise InvalidTokenException("An error has occurred while decoding the token") from e

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


    def create_password_reset_token(self, token: PasswordResetToken) -> str:
        token.iat = datetime.now(tz=timezone.utc)
        token.exp = datetime.now(tz=timezone.utc) + timedelta(minutes=settings.password_reset_token_expiration_minutes)
        payload = token.model_dump()
        return self._create_token(payload)


    def create_sign_up_complete_token(self, token: SignUpCompleteToken) -> str:
        token.iat = datetime.now(tz=timezone.utc)
        token.exp = datetime.now(tz=timezone.utc) + timedelta(days=settings.sign_up_complete_expiration_days)
        payload = token.model_dump()
        return self._create_token(payload)
    
    def create_email_change_token(self, token: EmailChangeToken) -> str:
        token.iat = datetime.now(tz=timezone.utc)
        token.exp = datetime.now(tz=timezone.utc) + timedelta(minutes=settings.email_change_token_expiration_minutes)
        payload = token.model_dump()
        return self._create_token(payload)
