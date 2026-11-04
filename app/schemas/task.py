from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.task import TaskStatus


class TaskCreate(BaseModel):
    lead_id: int = Field(gt=0)
    title: str = Field(min_length=3, max_length=150)
    description: str | None = None
    due_at: datetime


class TaskResponse(BaseModel):
    id: int
    lead_id: int
    title: str
    description: str | None
    due_at: datetime
    status: TaskStatus
    created_at: datetime
    completed_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class TaskStatusUpdate(BaseModel):
    status: TaskStatus