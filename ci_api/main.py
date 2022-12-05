import datetime

import uvicorn
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from admin.utils import create_default_admin
from admin.views import get_admin
from config import settings, templates
from create_data import create_fake_data, recreate_db
from exc.exceptions import UserNotLoggedError
from routers import main_router
from services.notification_scheduler import create_notifications_for_not_viewed_users
from web_service.router import router as web_router
from web_service.utils.title_context_func import update_title
from web_service.utils.titles_context import get_base_context

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

    app: FastAPI = get_admin(app)
    app.add_middleware(SessionMiddleware, secret_key=settings.SECRET)

    return app


app: FastAPI = get_application()

if __name__ == '__main__':
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
