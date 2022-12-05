from fastapi import APIRouter
from web_service.endpoints.login import router as login_router
from web_service.endpoints.profile import router as profile_router
from web_service.endpoints.charging import router as charging_router
from web_service.endpoints.subscribe import router as subscribe_router
from web_service.endpoints.index import router as index_router
from web_service.endpoints.notifications import router as notifications_router
from web_service.endpoints.come_tomorrow import router as tomorrow_router
from web_service.endpoints.verify_email import router as verify_email_router
from web_service.endpoints.register import router as register_router
from web_service.endpoints.payment_result import router as payment_result_router
from web_service.endpoints.password_recover import router as password_recover_router


router = APIRouter()
router.include_router(login_router)
router.include_router(profile_router)
router.include_router(charging_router)
router.include_router(subscribe_router)
router.include_router(index_router)
router.include_router(notifications_router)
router.include_router(tomorrow_router)
router.include_router(verify_email_router)
router.include_router(register_router)
router.include_router(payment_result_router)
router.include_router(password_recover_router)
