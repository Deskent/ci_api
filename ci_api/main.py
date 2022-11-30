from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from admin.utils import create_default_admin
from admin.views import get_admin
from config import settings
from create_data import create_fake_data, recreate_db
from routers import main_router
from web_service.router import router as web_router


DOCS_URL = "/ci"


def get_application():
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
        if not settings.MEDIA_DIR.exists():
            Path.mkdir(settings.MEDIA_DIR, exist_ok=True)

    app: FastAPI = get_admin(app)
    app.add_middleware(SessionMiddleware, secret_key=settings.SECRET)

    return app


app: FastAPI = get_application()

if __name__ == '__main__':
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
