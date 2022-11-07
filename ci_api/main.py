import os
from pathlib import Path

import uvicorn
from fastapi import FastAPI

from routers import main_router
from create_data import recreate

app = FastAPI(docs_url="/ci", redoc_url=None)
app.include_router(main_router)


BASE_DIR = Path(__file__).parent


def migrate():
    os.system('. ./migrations.sh')


@app.on_event("startup")
async def on_startup():
    await recreate()
    media_path = BASE_DIR / 'media'
    if not media_path.exists():
        Path.mkdir(media_path, exist_ok=True)


if __name__ == '__main__':
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
