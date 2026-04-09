from pydantic import BaseModel, Field
from datetime import date

class Link(BaseModel):
    name: str = Field(..., example="Instagram")
    url: str = Field(..., example="https://www.instagram.com/your_username")

class PeriodInfo(BaseModel):
    from_date: date
    to_date: date