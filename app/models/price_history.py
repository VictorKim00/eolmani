from datetime import date

from sqlalchemy import Date, ForeignKey, Index, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class PriceHistory(Base):
    __tablename__ = "price_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"), nullable=False)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    recorded_date: Mapped[date] = mapped_column(Date, nullable=False)
    source: Mapped[str] = mapped_column(String(50), nullable=False, default="kamis")
    region_code: Mapped[str] = mapped_column(String(10), nullable=False, default="")  # ''=전국 평균

    item: Mapped["Item"] = relationship(back_populates="price_history")

    __table_args__ = (
        UniqueConstraint(
            "item_id", "recorded_date", "source", "region_code",
            name="uq_price_item_date_source_region",
        ),
        Index("ix_price_history_item_region_date", "item_id", "region_code", "recorded_date"),
    )
