from fastapi import APIRouter, Depends , status, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db.session import get_db
from app.models.customer import Customer
from app.schemas.customer import CustomerCreate, CustomerResponse
 

 

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

@router.get(
    "",
    response_model=list[CustomerResponse]
)

def get_customers(
    database_session: Session = Depends(get_db)
):
    statement = select(Customer).order_by(Customer.id)

    customers = database_session.scalars(
        statement
    ).all()

    return customers

 