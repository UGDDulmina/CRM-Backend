from datetime import datetime

from pydantic import BaseModel, Field

class CompanyCreate(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    city: str | None = Field(default=None , max_length=100)


class CompanyResponse(BaseModel):
    id: int
    name: str
    city: str | None
    created_at: datetime

    model_config = {
        "from_attributes": True
    }