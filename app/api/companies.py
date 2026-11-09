from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.company import Company
from app.schemas.company import CompanyCreate, CompanyResponse
from app.models.users import UserRole, User
from app.core.dependencies import require_roles

router = APIRouter(
    prefix="/api/v1/companies",
    tags=["Companies"]
)

@router.post(
    "",
    response_model=CompanyResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(require_roles(UserRole.ADMIN))
    ]
)
def create_company(
    company_data: CompanyCreate,
    database_session: Session = Depends(get_db),
    # current_user: User = Depends(
    #     require_roles(UserRole.ADMIN)
    # )
):
    company = Company(
        name=company_data.name,
        city=company_data.city
    )

    database_session.add(company)
    database_session.commit()
    database_session.refresh(company)

    return company