from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.item import Item
from app.models.price_history import PriceHistory
from app.schemas.price import PriceItem, PricesTodayResponse


def get_today_prices(db: Session) -> PricesTodayResponse:
    """
    품목별 가장 최근 가격을 반환한다.
    오늘 데이터가 없으면 어제 데이터로 자동 폴백.
    """
    # 서브쿼리: 품목별 최신 recorded_date
    subq = (
        select(
            PriceHistory.item_id,
            PriceHistory.price,
            PriceHistory.recorded_date,
        )
        .distinct(PriceHistory.item_id)
        .where(PriceHistory.source == "kamis")
        .order_by(PriceHistory.item_id, PriceHistory.recorded_date.desc())
        .subquery()
    )

    rows = db.execute(
        select(Item, subq.c.price, subq.c.recorded_date)
        .join(subq, Item.id == subq.c.item_id)
        .order_by(Item.category, Item.name)
    ).all()

    today = date.today()
    items: list[PriceItem] = []

    for item, price, recorded_date in rows:
        price_float = float(price)
        d7 = recorded_date - timedelta(days=7)
        d30 = recorded_date - timedelta(days=30)

        past_7d = db.execute(
            select(PriceHistory.price)
            .where(PriceHistory.item_id == item.id)
            .where(PriceHistory.recorded_date == d7)
            .limit(1)
        ).scalar_one_or_none()

        past_30d = db.execute(
            select(PriceHistory.price)
            .where(PriceHistory.item_id == item.id)
            .where(PriceHistory.recorded_date == d30)
            .limit(1)
        ).scalar_one_or_none()

        def rate(past) -> float | None:
            if past is None or float(past) == 0:
                return None
            return round((price_float - float(past)) / float(past) * 100, 2)

        items.append(PriceItem(
            item_id=item.id,
            code=item.code,
            name=item.name,
            category=item.category,
            unit=item.unit,
            price=price_float,
            recorded_date=recorded_date,
            change_7d=rate(past_7d),
            change_30d=rate(past_30d),
        ))

    display_date = max((i.recorded_date for i in items), default=today)
    return PricesTodayResponse(date=display_date, count=len(items), items=items)
