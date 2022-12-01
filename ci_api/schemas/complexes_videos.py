from datetime import time

from fastapi import UploadFile, Form
from pydantic import BaseModel


class VideoBase(BaseModel):
    name: str = ''
    description: str = ''


class VideoUpload(VideoBase):
    file_name: str
    name: str
    description: str
    complex_id: int
    file: UploadFile
    video_number: int
    duration: int = 0

    @classmethod
    def as_form(
            cls,
            file_name: str = Form(...),
            name: str = Form(...),
            description: str = Form(...),
            complex_id: int = Form(...),
            video_number: int = Form(...),
            file: UploadFile = Form(...)
    ):
        return cls(
            file_name=file_name,
            name=name,
            description=description,
            complex_id=complex_id,
            file=file,
            video_number=video_number,
            duration=0
        )


class VideoInfo(VideoBase):
    id: int
    duration: time


class ComplexData(BaseModel):
    name: str
    description: str
    videos: list[VideoInfo] = []
