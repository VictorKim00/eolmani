"""add avg_year_price to items

Revision ID: 759ac747348b
Revises: 59633ef133e1
Create Date: 2026-04-29 09:47:47.703295

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '759ac747348b'
down_revision: Union[str, Sequence[str], None] = '59633ef133e1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("items", sa.Column("avg_year_price", sa.Numeric(10, 2), nullable=True))


def downgrade() -> None:
    op.drop_column("items", "avg_year_price")
