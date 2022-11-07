from pathlib import Path

import uvicorn
from fastapi import FastAPI
from sqladmin import Admin, ModelView
from database.db import engine

from models import User, Video


DOCS_URL = "/ci_admin"
BASE_DIR = Path(__file__).parent

app = FastAPI(docs_url=DOCS_URL, redoc_url=DOCS_URL)


admin = Admin(app, engine)


class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.username]


class VideoView(ModelView, model=Video):
    column_list = [Video.id, Video.path]


admin.add_view(UserAdmin)
admin.add_view(VideoView)

if __name__ == '__main__':
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
