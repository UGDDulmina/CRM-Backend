from fastapi import (
    APIRouter, 
    Depends , 
    status, 
    HTTPException, 
    Query
)
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, func, or_
from app.models.company import Company

from app.db.session import get_db
from app.models.customer import Customer
from app.schemas.customer import (
    CustomerCreate, 
    CustomerResponse, 
    CustomerListResponse,
    CustomerReplace,
    CustomerUpdate
)
 


router = APIRouter(
    prefix="/api/v1/customers",
    tags=["Customer"]
)

@router.post(
    "",
    response_model=CustomerResponse,
    status_code=status.HTTP_201_CREATED
)

def create_customer(
    customer_data: CustomerCreate,
    database_session: Session = Depends(get_db)
):
    if customer_data.company_id is not None:
        company = database_session.get(
            Company,
            customer_data.company_id
        )
        if company is None:
            raise HTTPException(
                status_code=404,
                detail="Company not found"
            )
        
    customer = Customer(
        name = customer_data.name,
        email = customer_data.email,
        phone= customer_data.phone,
        city=customer_data.city,
        company_id=customer_data.company_id
    )

    database_session.add(customer)

    try:
       database_session.commit()
       database_session.refresh(customer)

    except IntegrityError:
       database_session.rollback()

       raise HTTPException(
        status_code=409,
        detail="Customer conflicts with database constraints"
    )

    return customer

     

@router.get(
    "/{customer_id}",
    response_model = CustomerResponse
)

def get_customer(
    customer_id: int,
    database_session: Session = Depends(get_db)
):
    statement = select(Customer).where(
        Customer.is_active.is_(True)
    )

    customer = database_session.scalar(statement)

    if customer is None or not customer.is_active:
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    return customer

# @router.get(
#     "",
#     response_model=list[CustomerResponse]
# )

# def get_customers(
#     database_session: Session = Depends(get_db)
# ):
#     statement = select(Customer).order_by(Customer.id)

#     customers = database_session.scalars(
#         statement
#     ).all()

#     return customers

@router.get(
    "",
    response_model=CustomerListResponse
)

def get_customers(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
    search: str | None = Query(default=None , max_length=100),
    city: str | None = Query(default=None, max_length=100),
    database_session: Session = Depends(get_db)
):
    statement = select(Customer)

    #Search by name or email
    if search:
        statement = statement.where(
            or_(
                Customer.name.ilike(f"%{search}%"),
                Customer.email.ilike(f"%{search}%")
            )
        )
    # Filter by city
    if city:
        statement = statement.where(
            Customer.city.ilike(city)
        )

    # Count all matching records before pagination
    count_statement = select(
        func.count()
    ).select_from(statement.order_by(None).subquery())

    total = database_session.scalar(count_statement) or 0

    # Calculate pagination
    offset = (page - 1) * limit

    #Retrieve requested page
    statement = (
        statement
        .order_by(Customer.id)
        .offset(offset)
        .limit(limit)
    )

    customers = database_session.scalars(statement).all()

    total_pages = (total + limit -1) // limit

    return {
        "items": customers,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": total_pages 
    }

@router.patch(
    "/{customer_id}",
    response_model=CustomerResponse
)
def update_customer(
    customer_id: int,
    customer_data: CustomerUpdate,
    database_session: Session = Depends(get_db)
):
    customer = database_session.get(Customer, customer_id)

    if customer is None or not customer.is_active:
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )
    update_data = customer_data.model_dump(
        exclude_unset=True
    )
    if "company_id" in update_data:
        company_id = update_data["company_id"]

    if company_id is not None:
        company = database_session.get(
            Company,
            company_id
        )

        if company is None:
            raise HTTPException(
                status_code=404,
                detail="Company not found"
            )

    for field_name, value in update_data.items():
        setattr(customer, field_name, value)

    for field_name, value in update_data.items():
        setattr(customer, field_name, value)

    try:
        database_session.commit()
        database_session.refresh(customer)

    except IntegrityError:
        database_session.rollback()
        raise HTTPException(
            status_code=409,
            detail="Customer update conflicts with database constraints"
        )

    return customer

@router.delete(
    "/{customer_id}",
    status_code=status.HTTP_204_NO_CONTENT
)

def delete_customer(
    customer_id: int,
    database_session: Session = Depends(get_db)
):
    customer = database_session.get(Customer, customer_id)

    if customer is None or not customer.is_active:
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    customer.is_active = False

    database_session.commit()

    return None
