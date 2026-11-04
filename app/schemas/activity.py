from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.activity import ActivityType


class ActivityCreate(BaseModel):
    lead_id: int = Field(gt=0)
    activity_type: ActivityType
    description: str = Field(min_length=3)


class ActivityResponse(ActivityCreate):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)