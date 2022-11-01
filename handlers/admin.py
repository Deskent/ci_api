from fastapi import APIRouter


admin_router = APIRouter()
TAGS = ['admin']


@admin_router.get('/', tags=TAGS)
async def root():
    return {"root": "OK"}
