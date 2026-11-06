"""create users table with roles

Revision ID: 12f8eb110769
Revises: 589fdd0eac61
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "12f8eb110769"
down_revision: Union[str, Sequence[str], None] = "589fdd0eac61"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    op.create_table(
        "users",

        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True
        ),

        sa.Column(
            "full_name",
            sa.String(length=100),
            nullable=False
        ),

        sa.Column(
            "email",
            sa.String(length=255),
            nullable=False
        ),

        sa.Column(
            "hashed_password",
            sa.String(length=255),
            nullable=False
        ),

        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False
        ),

        sa.Column(
            "role",
            sa.Enum(
                "ADMIN",
                "SALESPERSON",
                name="user_role"
            ),
            server_default="SALESPERSON",
            nullable=False
        ),

        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False
        )
    )

    op.create_index(
        op.f("ix_users_email"),
        "users",
        ["email"],
        unique=True
    )


def downgrade() -> None:

    op.drop_index(
        op.f("ix_users_email"),
        table_name="users"
    )

    op.drop_table("users")

    sa.Enum(
        "ADMIN",
        "SALESPERSON",
        name="user_role"
    ).drop(op.get_bind(), checkfirst=True)