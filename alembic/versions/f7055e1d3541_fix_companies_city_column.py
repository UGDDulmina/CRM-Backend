"""Fix companies city column type."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# Revision identifiers
revision: str = "f7055e1d3541"
down_revision: Union[str, Sequence[str], None] = "105618756f1a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "companies",
        "city",
        existing_type=postgresql.TIMESTAMP(timezone=True),
        type_=sa.String(length=100),
        existing_nullable=False,
        nullable=True,
        postgresql_using="city::text",
    )


def downgrade() -> None:
    raise RuntimeError(
        "Cannot automatically convert city names back to timestamps."
    )