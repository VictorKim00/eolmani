"""add group_code, variant_label, sort_order to items

Revision ID: a3f82c9b1d4e
Revises: 759ac747348b
Create Date: 2026-04-29 15:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a3f82c9b1d4e"
down_revision: Union[str, None] = "759ac747348b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("items", sa.Column("group_code", sa.String(30), nullable=True))
    op.add_column("items", sa.Column("variant_label", sa.String(50), nullable=True))
    op.add_column("items", sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"))


def downgrade() -> None:
    op.drop_column("items", "sort_order")
    op.drop_column("items", "variant_label")
    op.drop_column("items", "group_code")
