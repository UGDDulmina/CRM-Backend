from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum

from typing import TYPE_CHECKING

if TYPE_CHECKING:
  from app.models.company import Company
  from app.models.customer import Customer

from sqlalchemy import (
    String,
    Text,
    ForeignKey,
    Numeric,
    DateTime,
    Enum as SqlEnum,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

class LeadStatus(str, Enum):
    NEW = "NEW"
    CONTACTED = "CONTACTED"
    QUALIFIED = "QUALIFIED"
    WON = "WON"
    LOST = "LOST"

class Lead(Base):
    __tablename__="leads"

    id: Mapped[int] = mapped_column(primary_key=True)

    title: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=False
    )

    estimated_value: Mapped[Decimal] = mapped_column(
        Numeric(12,2),
        nullable=False
    )

    source: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )

    status: Mapped[LeadStatus] = mapped_column(
        SqlEnum(LeadStatus, name="lead_status"),
        default=LeadStatus.NEW,
        nullable=False
    )

    customer_id: Mapped[int] = mapped_column(
        ForeignKey("customers.id"),
        nullable=False
    )

    company_id: Mapped[int | None] = mapped_column(
        ForeignKey("companies.id"),
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    customer: Mapped["Customer"] = relationship(
        "Customer",
        back_populates="leads"
    )

    company: Mapped["Company | None"] = relationship(
        "Company",
        back_populates="leads"
    )

