"""add region_code to price_history

Revision ID: b1c4d8e2f5a9
Revises: a3f82c9b1d4e
Create Date: 2026-04-30
"""

import sqlalchemy as sa
from alembic import op

revision = "b1c4d8e2f5a9"
down_revision = "a3f82c9b1d4e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1) 컬럼 추가 — server_default='1101' 로 기존 row 전부 서울로 백필
    op.add_column(
        "price_history",
        sa.Column("region_code", sa.String(10), nullable=False, server_default="1101"),
    )
    # 2) 안전장치: NULL이 혹시 있을 경우 방어
    op.execute("UPDATE price_history SET region_code='1101' WHERE region_code IS NULL OR region_code=''")
    # 3) 신규 row 기본값을 ''(전국 평균)으로 변경
    op.alter_column("price_history", "region_code", server_default=sa.text("''"))

    # 4) 조회 패턴(item + region + date desc) 가속 인덱스
    op.create_index(
        "ix_price_history_item_region_date",
        "price_history",
        ["item_id", "region_code", "recorded_date"],
    )
    # 5) Unique constraint 교체
    op.drop_constraint("uq_price_item_date_source", "price_history", type_="unique")
    op.create_unique_constraint(
        "uq_price_item_date_source_region",
        "price_history",
        ["item_id", "recorded_date", "source", "region_code"],
    )


def downgrade() -> None:
    op.drop_constraint("uq_price_item_date_source_region", "price_history", type_="unique")
    op.create_unique_constraint(
        "uq_price_item_date_source",
        "price_history",
        ["item_id", "recorded_date", "source"],
    )
    op.drop_index("ix_price_history_item_region_date", table_name="price_history")
    op.drop_column("price_history", "region_code")
