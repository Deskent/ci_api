from fastapi import APIRouter


root_router = APIRouter()


@root_router.get('/', tags=['root'])
async def root():
    return {"root": "OK"}
