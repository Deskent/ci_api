from pydantic import BaseModel


class AvatarBase(BaseModel):
    as_bytes: str | bytes
