from dataclasses import dataclass
from app.modules.users.schemas import UserResponse
from app.modules.store.schemas import StoreResponse

@dataclass
class SessionContext:
    user: UserResponse
    store: StoreResponse