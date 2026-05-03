from fastapi import APIRouter
from app.modules.auth.router import router as auth_router
from app.modules.users.router import router as users_router
from app.modules.store.router import router as store_router
from app.modules.items.routers import (
    public_router as items_public_router,
    private_router as items_private_router,
)
from app.modules.storage.router import router as storage_router
from app.modules.categories.router import router as categories_router
from app.modules.customers.router import router as customers_router
from app.modules.orders.routers import (
    public_router as orders_public_router,
    private_router as orders_private_router,
)
from app.modules.analytics.routers import (
    public_router as analytics_public_router,
    private_router as analytics_private_router,
)
from app.modules.invoices.router import router as invoices_router
from app.modules.expenses.router import router as expenses_router

router = APIRouter(
    prefix="/v1",
)

router.include_router(auth_router)
router.include_router(users_router)
router.include_router(store_router)

router.include_router(analytics_public_router)
router.include_router(analytics_private_router) ## analytics router comes before items router to avoid conflict

router.include_router(items_public_router)
router.include_router(items_private_router)

router.include_router(storage_router)
router.include_router(categories_router)
router.include_router(customers_router)
router.include_router(orders_private_router)
router.include_router(orders_public_router)
router.include_router(invoices_router, deprecated=True)
router.include_router(expenses_router)