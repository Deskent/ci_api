from datetime import time

from fastapi import UploadFile
from pydantic import BaseModel


class VideoBase(BaseModel):
    name: str = ''
    description: str = ''


class VideoUpload(VideoBase):
    file_name: str
    complex_id: int
    file: UploadFile


class VideoInfo(VideoBase):
    id: int
    duration: time


class ComplexData(BaseModel):
    name: str
    description: str
    videos: list[VideoInfo] = []
