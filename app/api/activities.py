from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.activity import Activity
from app.models.lead import Lead
from app.schemas.activity import ActivityCreate, ActivityResponse


router = APIRouter(
    prefix="/api/v1/activities",
    tags=["Activities"]
)


@router.post(
    "",
    response_model=ActivityResponse,
    status_code=status.HTTP_201_CREATED
)
def create_activity(
    activity_data: ActivityCreate,
    database_session: Session = Depends(get_db)
):
    lead = database_session.get(
        Lead,
        activity_data.lead_id
    )

    if lead is None:
        raise HTTPException(
            status_code=404,
            detail="Lead not found"
        )

    activity = Activity(
        lead_id=activity_data.lead_id,
        activity_type=activity_data.activity_type,
        description=activity_data.description
    )

    database_session.add(activity)

    try:
        database_session.commit()
        database_session.refresh(activity)
    except Exception:
        database_session.rollback()
        raise

    return activity