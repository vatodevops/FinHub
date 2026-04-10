from fastapi import APIRouter, Depends

from app.api.deps.auth import require_auth
from app.api.routers.accounts import router as accounts_router
from app.api.routers.auth import router as auth_router
from app.api.routers.budgets import router as budgets_router
from app.api.routers.connectors import router as connectors_router
from app.api.routers.health import router as health_router
from app.api.routers.institutions import router as institutions_router
from app.api.routers.manual import router as manual_router
from app.api.routers.overview import router as overview_router
from app.api.routers.recurring import router as recurring_router
from app.api.routers.reports import router as reports_router
from app.api.routers.transactions import router as transactions_router

router = APIRouter()
protected_router = APIRouter(dependencies=[Depends(require_auth)])

router.include_router(health_router)
router.include_router(auth_router)
protected_router.include_router(overview_router)
protected_router.include_router(institutions_router)
protected_router.include_router(accounts_router)
protected_router.include_router(transactions_router)
protected_router.include_router(recurring_router)
protected_router.include_router(manual_router)
protected_router.include_router(connectors_router)
protected_router.include_router(budgets_router)
protected_router.include_router(reports_router)
router.include_router(protected_router)
