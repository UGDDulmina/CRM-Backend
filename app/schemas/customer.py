from pydantic import BaseModel, EmailStr, Field
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

class CustomerReplace(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    phone: str | None = Field(default=None, max_length=30)
    city: str | None = Field(default=None, max_length=100)

class CustomerUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100
    )
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=30)
    city: str | None = Field(default=None, max_length=100)
    