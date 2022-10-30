import os

import uvicorn
from fastapi import FastAPI

from routers import main_router
from create_data import recreate

app = FastAPI()
app.include_router(main_router)


def migrate():
    os.system('. ./migrations.sh')


@app.on_event("startup")
async def on_startup():
    await recreate()
    if not os.path.exists('media'):
        os.mkdir('media')


if __name__ == '__main__':
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
