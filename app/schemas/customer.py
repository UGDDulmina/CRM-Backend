from pydantic import BaseModel, EmailStr
from datetime import datetime

class CustomerCreate(BaseModel):
    name: str
    email: EmailStr
    phone: str | None = None
    city: str | None = None

class CustomerResponse(BaseModel):
    id:int
    name: str
    email: EmailStr
    phone: str | None
    city: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes" : True
    }

class CustomerListResponse(BaseModel):
    items: list[CustomerResponse]
    total:int
    page:int
    limit:int
    total_pages:int