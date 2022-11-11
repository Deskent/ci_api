from datetime import time

from pydantic import BaseModel


class VideoBase(BaseModel):
    path: str
    name: str = ''
    description: str = ''


class VideoUpload(BaseModel):
    file_name: str
    name: str
    description: str
    complex_id: int


class VideoInfo(BaseModel):
    id: int
    name: str = ''
    description: str = ''


class ComplexData(BaseModel):
    description: str
    videos: list[VideoInfo] = []
