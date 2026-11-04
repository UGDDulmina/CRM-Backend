from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status
)

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.customer import Customer
from app.models.company import Company
from app.models.lead import Lead, LeadStatus
from app.schemas.lead import (
    LeadCreate,
    LeadResponse,
    LeadStatusUpdate,
    LeadListResponse
)

ALLOWED_TRANSITIONS = {
    LeadStatus.NEW: {LeadStatus.CONTACTED},
    LeadStatus.CONTACTED: {LeadStatus.QUALIFIED},
    LeadStatus.QUALIFIED: {
        LeadStatus.WON,
        LeadStatus.LOST
    },
    LeadStatus.WON: set(),
    LeadStatus.LOST: set()
}


router = APIRouter(
    prefix="/api/v1/leads",
    tags=["Leads"]
)

@router.post(
    "",
    response_model=LeadResponse,
    status_code=status.HTTP_201_CREATED
)
def create_lead(
    lead_data: LeadCreate,
    database_session: Session = Depends(get_db)
):
    customer = database_session.get(
        Customer,
        lead_data.customer_id
    )

    if customer is None or not customer.is_active:
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    if lead_data.company_id is not None:
        company = database_session.get(
            Company,
            lead_data.company_id
        )

        if company is None:
            raise HTTPException(
                status_code=404,
                detail="Company not found"
            )

        if customer.company_id != company.id:
            raise HTTPException(
                status_code=422,
                detail="Customer does not belong to this company"
            )

    lead = Lead(
        title=lead_data.title,
        description=lead_data.description,
        estimated_value=lead_data.estimated_value,
        source=lead_data.source,
        customer_id=lead_data.customer_id,
        company_id=lead_data.company_id,
        status=LeadStatus.NEW
    )

    database_session.add(lead)

    try:
        database_session.commit()
        database_session.refresh(lead)
    except Exception:
        database_session.rollback()
        raise

    return lead

@router.get(
    "/{lead_id}",
    response_model=LeadResponse
)
def get_lead(
    lead_id: int,
    database_session: Session = Depends(get_db)
):
    lead = database_session.get(Lead, lead_id)

    if lead is None:
        raise HTTPException(
            status_code=404,
            detail="Lead not found"
        )

    return lead

@router.get(
    "",
    response_model=LeadListResponse
)
def get_leads(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
    lead_status: LeadStatus | None = Query(
        default=None,
        alias="status"
    ),
    customer_id: int | None = Query(default=None, gt=0),
    company_id: int | None = Query(default=None, gt=0),
    source: str | None = Query(default=None),
    database_session: Session = Depends(get_db)
):
    statement = select(Lead)

    if lead_status is not None:
        statement = statement.where(
            Lead.status == lead_status
        )

    if customer_id is not None:
        statement = statement.where(
            Lead.customer_id == customer_id
        )

    if company_id is not None:
        statement = statement.where(
            Lead.company_id == company_id
        )

    if source:
        statement = statement.where(
            Lead.source.ilike(source)
        )

    count_statement = select(
        func.count()
    ).select_from(
        statement.order_by(None).subquery()
    )

    total = database_session.scalar(count_statement) or 0

    offset = (page - 1) * limit

    statement = (
        statement
        .order_by(Lead.id)
        .offset(offset)
        .limit(limit)
    )

    leads = database_session.scalars(statement).all()

    return {
        "items": leads,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": (total + limit - 1) // limit
    }

@router.patch(
    "/{lead_id}/status",
    response_model=LeadResponse
)
def update_lead_status(
    lead_id: int,
    status_data: LeadStatusUpdate,
    database_session: Session = Depends(get_db)
):
    lead = database_session.get(Lead, lead_id)

    if lead is None:
        raise HTTPException(
            status_code=404,
            detail="Lead not found"
        )

    allowed_statuses = ALLOWED_TRANSITIONS[lead.status]

    if status_data.status not in allowed_statuses:
        raise HTTPException(
            status_code=409,
            detail=(
                f"Cannot change status from "
                f"{lead.status.value} to "
                f"{status_data.status.value}"
            )
        )

    lead.status = status_data.status

    try:
        database_session.commit()
        database_session.refresh(lead)
    except Exception:
        database_session.rollback()
        raise

    return lead