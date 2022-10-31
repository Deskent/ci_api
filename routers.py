from fastapi import APIRouter
from handlers import *


main_router = APIRouter(prefix="/api/v1")
main_router.include_router(users_router, prefix="/users")
main_router.include_router(alarms_router, prefix="/alarms")
main_router.include_router(videos_router, prefix="/videos")
main_router.include_router(notifications_router, prefix="/notifications")
main_router.include_router(admin_router)
