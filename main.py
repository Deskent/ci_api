import uvicorn
from fastapi import FastAPI

from routers import main_router
from core.db import drop_db, create_db


app = FastAPI()
app.include_router(main_router)


@app.on_event("startup")
async def on_startup():
    # await drop_db()
    await create_db()


if __name__ == '__main__':
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
