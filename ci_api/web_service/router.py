from fastapi import APIRouter
from web_service.endpoints.login import router as login_router
from web_service.endpoints.profile import router as profile_router
from web_service.endpoints.charging import router as charging_router


router = APIRouter()
router.include_router(login_router)
router.include_router(profile_router)
router.include_router(charging_router)
