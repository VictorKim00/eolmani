from sqlalchemy import Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Item(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    unit: Mapped[str] = mapped_column(String(20), nullable=False)

    # KAMIS API 매핑 정보
    kamis_category_code: Mapped[str] = mapped_column(String(10), nullable=False, default="")
    kamis_item_code: Mapped[str] = mapped_column(String(20), nullable=False, default="")
    kamis_kind_code: Mapped[str] = mapped_column(String(20), nullable=False, default="")
    kamis_rank: Mapped[str | None] = mapped_column(String(20), nullable=True)

    # KAMIS dpr7 — 평년 가격 (매일 수집 시 갱신)
    avg_year_price: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)

    # 동일 품목 내 변형(부위·품종·용량) 그룹핑
    group_code: Mapped[str | None] = mapped_column(String(30), nullable=True)
    variant_label: Mapped[str | None] = mapped_column(String(50), nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    price_history: Mapped[list["PriceHistory"]] = relationship(
        back_populates="item", cascade="all, delete-orphan"
    )
