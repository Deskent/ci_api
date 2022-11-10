from pydantic import BaseModel


class VideoBase(BaseModel):
    path: str
    name: str = ''
    description: str = ''


class VideoCreate(VideoBase):
    pass


class VideoInfo(BaseModel):
    id: int
    name: str = ''
    description: str = ''


class ComplexData(BaseModel):
    description: str
    videos: list[VideoInfo] = []
