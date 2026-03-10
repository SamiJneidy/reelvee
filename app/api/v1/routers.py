from fastapi import APIRouter
from app.modules.auth.auth.router import router as auth_router
from app.modules.users.router import router as users_router
from app.modules.items.routers import (
    public_router as items_public_router,
    private_router as items_private_router,
)

router = APIRouter(
    prefix="/v1",
)

router.include_router(auth_router)
router.include_router(users_router)
router.include_router(items_public_router)
router.include_router(items_private_router)
