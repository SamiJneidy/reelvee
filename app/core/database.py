from typing import AsyncGenerator

from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import settings

from app.modules.users.models import User
from app.modules.auth.otp.models import OTP
from app.modules.auth.tokens.models import RefreshTokenRecord
from app.modules.items.models import Item
from app.modules.categories.models import Category
from app.modules.customers.models import Customer

# Single client for the app. Created at import; connect in init_db().
client = AsyncIOMotorClient(
    settings.mongodb_uri,
    tz_aware=True,
)
database = client[settings.mongodb_name]

async def init_db() -> None:
    """Init Beanie with the app client. Call once at startup (lifespan)."""
    await init_beanie(database=database, document_models=[User, OTP, Item, Category, RefreshTokenRecord, Customer])


async def get_session() -> AsyncGenerator[AsyncIOMotorClient, None]:
    """MongoDB session with an active transaction. Commits on success, aborts on exception."""
    async with await client.start_session() as session:
        async with session.start_transaction():
            yield session
