from dataclasses import dataclass
from app.modules.users.schemas.internal import UserInDB

@dataclass
class CurrentUser:
    user: UserInDB