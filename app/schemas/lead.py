from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, ConfigDict

from app.models.lead import LeadStatus



class LeadCreate(BaseModel):
    title: str = Field(min_length=3, max_length=150)
    description: str | None = None

    estimated_value: Decimal = Field(
        ge=0,
        max_digits=12,
        decimal_places=2
    )

    source: str | None = Field(
        default=None,
        max_length=50
    )

    customer_id: int = Field(gt=0)
    company_id: int | None = Field(default=None, gt=0)


class LeadResponse(BaseModel):
    id: int
    title: str
    description: str | None
    estimated_value: Decimal
    source: str | None
    status: LeadStatus
    customer_id: int
    company_id: int | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LeadStatusUpdate(BaseModel):
    status: LeadStatus


class LeadListResponse(BaseModel):
    items: list[LeadResponse]
    total: int
    page: int
    limit: int
    total_pages: int