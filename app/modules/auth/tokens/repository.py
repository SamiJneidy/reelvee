from typing import Optional
from .models import RefreshTokenRecord
from .schemas import RefreshTokenCreate, RefreshTokenInDB


class TokenRepository:
    def __init__(self):
        pass

    async def create_refresh_token(self, data: RefreshTokenCreate, session=None) -> None:
        record = RefreshTokenRecord(
            token_id=data.token_id,
            family_id=data.family_id,
            user_id=data.user_id,
            expires_at=data.expires_at,
        )
        await record.insert(session=session)

    async def get_refresh_token_by_jti(self, jti: str, session=None) -> Optional[RefreshTokenInDB]:
        record = await RefreshTokenRecord.find_one(RefreshTokenRecord.token_id == jti, session=session)
        if not record:
            return None
        return RefreshTokenInDB(
            token_id=record.token_id,
            family_id=record.family_id,
            user_id=record.user_id,
            is_revoked=record.is_revoked,
            expires_at=record.expires_at,
        )

    async def revoke_refresh_token(self, jti: str, session=None) -> None:
        await RefreshTokenRecord.find_one(
            RefreshTokenRecord.token_id == jti,
            session=session,
        ).update({"$set": {"is_revoked": True}})

    async def revoke_refresh_token_family(self, family_id: str, session=None) -> None:
        await RefreshTokenRecord.find(
            RefreshTokenRecord.family_id == family_id,
            session=session,
        ).update_many({"$set": {"is_revoked": True}})

    async def revoke_all_refresh_tokens_for_user(self, user_id: str, session=None) -> None:
        await RefreshTokenRecord.find(
            RefreshTokenRecord.user_id == user_id,
            session=session,
        ).update_many({"$set": {"is_revoked": True}})
