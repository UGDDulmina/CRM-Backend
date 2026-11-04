from datetime import datetime, timezone

from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.customer import Customer
    from app.models.lead import Lead

class Company(Base):
    __tablename__= "companies"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    city: Mapped[str | None] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    customers: Mapped[list["Customer"]] = relationship(
        "Customer",
        back_populates="company"
    )

    leads: Mapped[list["Lead"]] = relationship(
        "Lead",
        back_populates="company"
    )