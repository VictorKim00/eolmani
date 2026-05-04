"""add coupang_url to items

Revision ID: c9d3e1f7a2b5
Revises: a3f82c9b1d4e
Create Date: 2026-05-05 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c9d3e1f7a2b5"
down_revision: Union[str, None] = "b1c4d8e2f5a9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("items", sa.Column("coupang_url", sa.String(500), nullable=True))


def downgrade() -> None:
    op.drop_column("items", "coupang_url")
