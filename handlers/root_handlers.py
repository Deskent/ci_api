from fastapi import APIRouter, Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from core.db import get_session
from app.models import User, UserCreate


root_router = APIRouter()


@root_router.get('/', tags=['root'])
async def root():
    return {"root": "OK"}


@root_router.get("/songs", response_model=list[User])
async def get_songs(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(User))
    users = result.scalars().all()

    return [User(name=user.username, artist=user.email, id=user.id) for user in users]


@root_router.post("/songs", response_model=User)
async def add_song(song: UserCreate, session: AsyncSession = Depends(get_session)):
    song = User(**song.dict())
    session.add(song)
    await session.commit()
    await session.refresh(song)

    return song