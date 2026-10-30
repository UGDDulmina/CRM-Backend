from datetime import datetime

from sqlalchemy import DateTime, String , Boolean 
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

from typing import Optional

class Customer(Base):
    __tablename__ = "customers"
    id: Mapped[int] = mapped_column(
        primary_key=True
    )
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )
    phone: Mapped[Optional[str]] = mapped_column(
        String(30),
        nullable=True
    )
    city: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )
    

