from fastapi import APIRouter
from api.users import router as user_router
from api.alarms import router as alarms_router
from api.notifications import router as notifications_router
from api.videos import router as videos_router
from api.complexes import router as complex_router
from api.authorization import router as auth_router
from api.payments import router as payments_router
from api.web_api import router as web_api_router
from api.rates import router as rates_router
from api.avatars import router as avatars_router
from api.moods import router as moods_router


main_router = APIRouter(prefix="/api/v1")
main_router.include_router(auth_router)
main_router.include_router(user_router)
main_router.include_router(alarms_router)
main_router.include_router(complex_router)
main_router.include_router(notifications_router)
main_router.include_router(videos_router)
main_router.include_router(payments_router)
main_router.include_router(rates_router)
main_router.include_router(avatars_router)
main_router.include_router(moods_router)
main_router.include_router(web_api_router)
