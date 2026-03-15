from pydantic import BaseModel, Field


class Link(BaseModel):
    name: str = Field(..., example="Instagram")
    url: str = Field(..., example="https://www.instagram.com/your_username")
