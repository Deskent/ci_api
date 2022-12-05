from fastapi import APIRouter
from web_service.endpoints.login import router as login_router
from web_service.endpoints.profile import router as profile_router
from web_service.endpoints.charging import router as charging_router
from web_service.endpoints.subscribe_and_payment import router as payments_router


router = APIRouter()
router.include_router(login_router)
router.include_router(profile_router)
router.include_router(charging_router)
router.include_router(payments_router)
