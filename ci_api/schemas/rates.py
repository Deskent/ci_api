from pydantic import BaseModel


class RateLink(BaseModel):
    link: str
