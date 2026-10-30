from fastapi import APIRouter, Depends , status, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, func, or_


from app.db.session import get_db
from app.models.customer import Customer
from app.schemas.customer import CustomerCreate, CustomerResponse, CustomerListResponse
 

 

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
    customer = Customer(
        name = customer_data.name,
        email = customer_data.email,
        phone= customer_data.phone,
        city=customer_data.city
    )

    database_session.add(customer)
    database_session.commit()
    database_session.refresh(customer)

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
        Customer.id == customer_id
    )

    customer = database_session.scalar(statement)

    if customer is None:
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

 