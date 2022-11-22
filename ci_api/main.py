import os
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from admin.views import get_admin
from config import settings
from create_data import recreate_db_data
from routers import main_router
from services.utils import create_default_admin


DOCS_URL = "/ci"
BASE_DIR = Path(__file__).parent


def get_application():
    app = FastAPI(docs_url=DOCS_URL, redoc_url=DOCS_URL)
    app.include_router(main_router)

    @app.on_event("startup")
    async def on_startup():
        await create_default_admin()
        await recreate_db_data()
        if not settings.MEDIA_DIR.exists():
            Path.mkdir(settings.MEDIA_DIR, exist_ok=True)

    get_admin(app)
    app.add_middleware(SessionMiddleware, secret_key=settings.SECRET)

    return app


app: FastAPI = get_application()


if __name__ == '__main__':
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
