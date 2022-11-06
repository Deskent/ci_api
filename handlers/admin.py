from fastapi import APIRouter


router = APIRouter(tags=['Admin'])


@router.get('/')
async def root():
    return {"root": "OK"}
