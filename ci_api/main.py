import os
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from sqladmin import Admin
from starlette.middleware.sessions import SessionMiddleware

from admin.auth import authentication_backend
from admin.views import AlarmView, NotificationView, UserView, VideoView, ComplexView, UploadVideo
from config import settings
from create_data import recreate
from database.db import engine
from routers import main_router


DOCS_URL = "/ci"
ADMIN_URL = "/ci_admin"
BASE_DIR = Path(__file__).parent


def migrate():
    os.system('. ./migrations.sh')


def get_admin(app: FastAPI) -> Admin:
    admin = Admin(
        app,
        engine,
        base_url=ADMIN_URL,
        authentication_backend=authentication_backend,
        templates_dir=settings.TEMPLATES_DIR
    )

    admin.add_view(UserView)
    admin.add_view(VideoView)
    admin.add_view(AlarmView)
    admin.add_view(NotificationView)
    admin.add_view(ComplexView)
    admin.add_view(UploadVideo)

    return admin


def get_application():
    app = FastAPI(docs_url=DOCS_URL, redoc_url=DOCS_URL)
    app.include_router(main_router)

    @app.on_event("startup")
    async def on_startup():
        await recreate()
        if not settings.MEDIA_DIR.exists():
            Path.mkdir(settings.MEDIA_DIR, exist_ok=True)

    get_admin(app)
    app.add_middleware(SessionMiddleware, secret_key=settings.SECRET)

    return app


app = get_application()


if __name__ == '__main__':
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
