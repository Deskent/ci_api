import datetime

import uvicorn
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from admin.utils import create_default_admin
from admin.views import get_admin
from config import settings, MAX_LEVEL, logger
from create_data import create_fake_data, recreate_db
from exc.exceptions import UserNotLoggedError, ComeTomorrowException
from models.models import User
from routers import main_router
from services.notification_scheduler import create_notifications_for_not_viewed_users
from services.web_context_class import WebContext
from web_service.router import router as web_router
from web_service.utils.get_contexts import (
    get_base_context, get_browser_session_token, get_session_user, get_logged_user_context
)


def get_application():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        create_notifications_for_not_viewed_users, 'cron',
        hour=settings.NOTIFICATION_HOUR,
        minute=00,
        replace_existing=True,
        timezone=datetime.timezone(datetime.timedelta(hours=3))
    )

    app = FastAPI(docs_url=settings.DOCS_URL, redoc_url=settings.DOCS_URL, debug=settings.DEBUG)

    app.mount("/static", StaticFiles(directory=str(settings.STATIC_DIR)), name="static")
    app.mount("/media", StaticFiles(directory=str(settings.MEDIA_DIR)), name="media")
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
        logger.debug("Raised user_not_logged_exception_handler")

        request.session.clear()
        web_context = WebContext(context=get_base_context({"request": request}))
        web_context.template = "entry_via_phone.html"

        return web_context.web_render()

    @app.exception_handler(ComeTomorrowException)
    async def user_not_active_exception_handler(
            request: Request, exc: ComeTomorrowException,
    ):
        logger.debug("Raised user_not_active_exception_handler")

        token: str = await get_browser_session_token(request)
        user: User = await get_session_user(token)
        base_context: dict = get_base_context({"request": request})
        context: dict = await get_logged_user_context(user, base_context)
        context.update(max_level=MAX_LEVEL)
        web_context = WebContext(context=get_base_context({"request": request}))
        web_context.template = "profile.html"

        return web_context.web_render()

    # @app.exception_handler(status.HTTP_500_INTERNAL_SERVER_ERROR)
    # async def status_500_exception_handler(
    #         request: Request, exc: Exception
    # ):
    #     context: dict = get_base_context({"request": request})
    #     logger.error(f"Status 500 error: \n{request.url}\n{exc}\n")
    #     logger.exception(exc)
    #
    #     return templates.TemplateResponse(
    #         "error_page.html", context=get_page_titles(context, "error_page.html")
    #     )

    app: FastAPI = get_admin(app)
    app.add_middleware(SessionMiddleware, secret_key=settings.SECRET)

    return app


app: FastAPI = get_application()

if __name__ == '__main__':
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
