import datetime

import uvicorn
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from admin.utils import create_default_admin
from admin.views import get_admin
from config import settings, templates, MAX_LEVEL
from create_data import create_fake_data, recreate_db
from exc.exceptions import UserNotLoggedError, ComeTomorrowException
from models.models import User
from routers import main_router
from services.notification_scheduler import create_notifications_for_not_viewed_users
from web_service.router import router as web_router
from web_service.utils.get_contexts import get_base_context, \
    get_session_token, get_session_user, get_logged_user_context
from web_service.utils.title_context_func import update_title

DOCS_URL = "/ci"


def get_application():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        create_notifications_for_not_viewed_users, 'cron',
        hour=settings.NOTIFICATION_HOUR,
        minute=00,
        replace_existing=True,
        timezone=datetime.timezone(datetime.timedelta(hours=3))
    )

    app = FastAPI(docs_url=DOCS_URL, redoc_url=DOCS_URL, debug=settings.DEBUG)

    # origins = [
    #     "http://localhost.tiangolo.com",
    #     "https://localhost.tiangolo.com",
    #     "http://localhost",
    #     "http://localhost:8080",
    #     "http://localhost:8000",
    #     "http://127.0.0.1:8000",
    # ]
    #
    # app.add_middleware(
    #     CORSMiddleware,
    #     allow_origins=origins,
    #     allow_credentials=True,
    #     allow_methods=["*"],
    #     allow_headers=["*"],
    # )

    app.mount("/static", StaticFiles(directory=str(settings.STATIC_DIR)), name="static")
    app.mount("/templates", StaticFiles(directory=str(settings.TEMPLATES_DIR)), name="templates")
    app.include_router(main_router)
    app.include_router(web_router)

    @app.on_event("startup")
    async def on_startup():
        await recreate_db()
        await create_default_admin()
        await create_fake_data()
        scheduler.start()

    @app.on_event('shutdown')
    async def on_shutdown():
        scheduler.shutdown()

    @app.exception_handler(UserNotLoggedError)
    async def user_not_logged_exception_handler(
            request: Request, exc: UserNotLoggedError
    ):
        context: dict = get_base_context({"request": request})
        return templates.TemplateResponse(
            "entry.html", context=update_title(context, "entry.html")
        )

    @app.exception_handler(ComeTomorrowException)
    async def user_not_active_exception_handler(
            request: Request, exc: ComeTomorrowException,
    ):
        token: str = await get_session_token(request)
        user: User = await get_session_user(token)
        base_context: dict = get_base_context({"request": request})
        context: dict = await get_logged_user_context(user, base_context)
        context.update(max_level=MAX_LEVEL)
        return templates.TemplateResponse(
            "profile.html", context=update_title(context, "profile.html")
        )

    app: FastAPI = get_admin(app)
    app.add_middleware(SessionMiddleware, secret_key=settings.SECRET)

    return app


app: FastAPI = get_application()

if __name__ == '__main__':
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
