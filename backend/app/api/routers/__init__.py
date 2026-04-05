from fastapi import APIRouter

from app.api.routers.accounts import router as accounts_router
from app.api.routers.connectors import router as connectors_router
from app.api.routers.health import router as health_router
from app.api.routers.institutions import router as institutions_router
from app.api.routers.manual import router as manual_router
from app.api.routers.overview import router as overview_router
from app.api.routers.recurring import router as recurring_router
from app.api.routers.transactions import router as transactions_router

router = APIRouter()

router.include_router(health_router)
router.include_router(overview_router)
router.include_router(institutions_router)
router.include_router(accounts_router)
router.include_router(transactions_router)
router.include_router(recurring_router)
router.include_router(manual_router)
router.include_router(connectors_router)
