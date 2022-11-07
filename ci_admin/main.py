from pathlib import Path

import uvicorn
from fastapi import FastAPI

DOCS_URL = "/ci_admin"
app = FastAPI(docs_url=DOCS_URL, redoc_url=DOCS_URL)


BASE_DIR = Path(__file__).parent


if __name__ == '__main__':
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
