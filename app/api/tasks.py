from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db.session import get_db
from app.models.lead import Lead
from app.models.task import Task, TaskStatus
from app.schemas.task import (
    TaskCreate,
    TaskResponse,
    TaskStatusUpdate
)

ALLOWED_TASK_TRANSITIONS = {
    TaskStatus.PENDING: {
        TaskStatus.IN_PROGRESS,
        TaskStatus.COMPLETED,
        TaskStatus.CANCELLED
    },
    TaskStatus.IN_PROGRESS: {
        TaskStatus.COMPLETED,
        TaskStatus.CANCELLED
    },
    TaskStatus.COMPLETED: set(),
    TaskStatus.CANCELLED: set()
}


router = APIRouter(
    prefix="/api/v1/tasks",
    tags=["Tasks"]
)


@router.post(
    "",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED
)
def create_task(
    task_data: TaskCreate,
    database_session: Session = Depends(get_db)
):
    lead = database_session.get(
        Lead,
        task_data.lead_id
    )

    if lead is None:
        raise HTTPException(
            status_code=404,
            detail="Lead not found"
        )

    if task_data.due_at.utcoffset() is None:
        raise HTTPException(
            status_code=422,
            detail="due_at must include timezone information"
        )

    due_at_utc = task_data.due_at.astimezone(timezone.utc)

    if due_at_utc <= datetime.now(timezone.utc):
        raise HTTPException(
            status_code=422,
            detail="Task due date must be in the future"
        )

    task = Task(
        lead_id=task_data.lead_id,
        title=task_data.title,
        description=task_data.description,
        due_at=due_at_utc,
        status=TaskStatus.PENDING
    )

    database_session.add(task)

    try:
        database_session.commit()
        database_session.refresh(task)
    except Exception:
        database_session.rollback()
        raise

    return task

@router.patch(
    "/{task_id}/status",
    response_model=TaskResponse
)
def update_task_status(
    task_id: int,
    status_data: TaskStatusUpdate,
    database_session: Session = Depends(get_db)
):
    task = database_session.get(Task, task_id)

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    allowed = ALLOWED_TASK_TRANSITIONS[task.status]

    if status_data.status not in allowed:
        raise HTTPException(
            status_code=409,
            detail="Invalid task status transition"
        )

    task.status = status_data.status

    if status_data.status == TaskStatus.COMPLETED:
        task.completed_at = datetime.now(timezone.utc)

    try:
        database_session.commit()
        database_session.refresh(task)
    except Exception:
        database_session.rollback()
        raise

    return task

@router.get(
    "",
    response_model=list[TaskResponse]
)
def get_tasks(
    task_status: TaskStatus | None = Query(
        default=None,
        alias="status"
    ),
    lead_id: int | None = Query(default=None, gt=0),
    due_before: datetime | None = None,
    overdue: bool = False,
    database_session: Session = Depends(get_db)
):
    statement = select(Task)

    if task_status is not None:
        statement = statement.where(
            Task.status == task_status
        )

    if lead_id is not None:
        statement = statement.where(
            Task.lead_id == lead_id
        )

    if due_before is not None:
        if due_before.utcoffset() is None:
            raise HTTPException(
                status_code=422,
                detail="due_before must include timezone information"
            )

        statement = statement.where(
            Task.due_at <= due_before.astimezone(timezone.utc)
        )

    if overdue:
        statement = statement.where(
            Task.due_at < datetime.now(timezone.utc),
            Task.status.in_([
                TaskStatus.PENDING,
                TaskStatus.IN_PROGRESS
            ])
        )

    statement = statement.order_by(
        Task.due_at,
        Task.id
    ).limit(100)

    return database_session.scalars(statement).all()

