from decimal import Decimal

from pydantic import BaseModel, Field

class DashboardSummaryResponse(BaseModel):
    total_customers: int
    total_companies: int
    total_leads: int

    new_leads: int
    contacted_leads: int
    qualified_leads: int
    won_leads: int
    lost_leads: int

    total_won_value: Decimal
    lead_win_rate: float

    pending_tasks: int
    in_progress_tasks: int
    completed_tasks: int
    overdue_tasks: int


class LeadStatusCount(BaseModel):
    status: str
    count: int


class LeadStatusReportResponse(BaseModel):
    total: int
    items: list[LeadStatusCount]


class SalesPipelineResponse(BaseModel):
    status: str
    lead_count: int
    total_value: Decimal


class TaskOverviewResponse(BaseModel):
    total_tasks: int
    pending: int
    in_progress: int
    completed: int
    cancelled: int
    overdue: int