from fastapi import APIRouter
from handlers.users import router as user_router
from handlers.alarms import router as alarms_router
from handlers.notifications import router as notifications_router
from handlers.videos import router as videos_router
from handlers.admin import router as admin_router


main_router = APIRouter(prefix="/api/v1")
main_router.include_router(user_router)
main_router.include_router(alarms_router)
main_router.include_router(videos_router)
main_router.include_router(notifications_router)
main_router.include_router(admin_router)
