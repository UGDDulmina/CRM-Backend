from datetime import datetime, timezone
from decimal import Decimal

from fastapi import APIRouter, Depends
from sqlalchemy import select, func, case
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.dependencies import require_roles

from app.models.users import User, UserRole
from app.models.customer import Customer
from app.models.company import Company
from app.models.lead import Lead, LeadStatus
from app.models.task import Task, TaskStatus

from app.schemas.dashboard import (
    DashboardSummaryResponse,
    LeadStatusCount,
    LeadStatusReportResponse,
    SalesPipelineResponse,
    TaskOverviewResponse
)

router = APIRouter(
    prefix="/api/v1/dashboard",
    tags=["Dashboard"],
    dependencies=[
        Depends(require_roles(UserRole.ADMIN))
    ]
)

@router.get(
    "/summary",
    response_model=DashboardSummaryResponse
)
def get_dashboard_summary(
    database_session: Session = Depends(get_db)
):
    # 1. Active customers
    total_customers = database_session.scalar(
        select(func.count(Customer.id)).where(
            Customer.is_active.is_(True)
        )
    ) or 0

    # 2. Companies
    total_companies = database_session.scalar(
        select(func.count(Company.id))
    ) or 0

    # 3. All leads
    total_leads = database_session.scalar(
        select(func.count(Lead.id))
    ) or 0

    # 4. Lead status counts
    lead_status_rows = database_session.execute(
        select(
            Lead.status,
            func.count(Lead.id)
        ).group_by(Lead.status)
    ).all()

    lead_counts = {
        status: count
        for status, count in lead_status_rows
    }

    new_leads = lead_counts.get(LeadStatus.NEW, 0)

    contacted_leads = lead_counts.get(
        LeadStatus.CONTACTED, 0
    )

    qualified_leads = lead_counts.get(
        LeadStatus.QUALIFIED, 0
    )

    won_leads = lead_counts.get(LeadStatus.WON, 0)

    lost_leads = lead_counts.get(LeadStatus.LOST, 0)

    # 5. Total value of won leads
    total_won_value = database_session.scalar(
        select(func.sum(Lead.estimated_value)).where(
            Lead.status == LeadStatus.WON
        )
    ) or Decimal("0.00")

    # 6. Lead win rate
    lead_win_rate = (
        round((won_leads / total_leads) * 100, 2)
        if total_leads > 0
        else 0.0
    )

    # 7. Task status counts
    task_status_rows = database_session.execute(
        select(
            Task.status,
            func.count(Task.id)
        ).group_by(Task.status)
    ).all()

    task_counts = {
        status: count
        for status, count in task_status_rows
    }

    pending_tasks = task_counts.get(
        TaskStatus.PENDING, 0
    )

    in_progress_tasks = task_counts.get(
        TaskStatus.IN_PROGRESS, 0
    )

    completed_tasks = task_counts.get(
        TaskStatus.COMPLETED, 0
    )

    # 8. Overdue tasks
    now = datetime.now(timezone.utc)

    overdue_tasks = database_session.scalar(
        select(func.count(Task.id)).where(
            Task.due_at < now,
            Task.status.in_([
                TaskStatus.PENDING,
                TaskStatus.IN_PROGRESS
            ])
        )
    ) or 0

    return DashboardSummaryResponse(
        total_customers=total_customers,
        total_companies=total_companies,
        total_leads=total_leads,
        new_leads=new_leads,
        contacted_leads=contacted_leads,
        qualified_leads=qualified_leads,
        won_leads=won_leads,
        lost_leads=lost_leads,
        total_won_value=total_won_value,
        lead_win_rate=lead_win_rate,
        pending_tasks=pending_tasks,
        in_progress_tasks=in_progress_tasks,
        completed_tasks=completed_tasks,
        overdue_tasks=overdue_tasks
    )

@router.get(
    "/leads-by-status",
    response_model=LeadStatusReportResponse
)
def get_leads_by_status(
    database_session: Session = Depends(get_db)
):
    statement = (
        select(
            Lead.status,
            func.count(Lead.id).label("count")
        )
        .group_by(Lead.status)
        .order_by(Lead.status)
    )

    rows = database_session.execute(statement).all()

    items = [
        LeadStatusCount(
            status=lead_status.value,
            count=count
        )
        for lead_status, count in rows
    ]

    return LeadStatusReportResponse(
        total=sum(item.count for item in items),
        items=items
    )

@router.get(
    "/pipeline",
    response_model=list[SalesPipelineResponse]
)
def get_sales_pipeline(
    database_session: Session = Depends(get_db)
):
    statement = (
        select(
            Lead.status,
            func.count(Lead.id).label("lead_count"),
            func.sum(
                Lead.estimated_value
            ).label("total_value")
        )
        .group_by(Lead.status)
        .order_by(Lead.status)
    )

    rows = database_session.execute(statement).all()

    return [
        SalesPipelineResponse(
            status=lead_status.value,
            lead_count=lead_count,
            total_value=total_value or Decimal("0.00")
        )
        for lead_status, lead_count, total_value in rows
    ]