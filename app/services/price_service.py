from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.item import Item
from app.models.price_history import PriceHistory
from app.schemas.price import PriceItem, PricesTodayResponse


def _get_price_on(db: Session, item_id: int, target_date: date) -> float | None:
    row = db.execute(
        select(PriceHistory.price)
        .where(PriceHistory.item_id == item_id)
        .where(PriceHistory.recorded_date == target_date)
        .limit(1)
    ).scalar_one_or_none()
    return float(row) if row is not None else None


def _change_rate(today: float, past: float | None) -> float | None:
    if past is None or past == 0:
        return None
    return round((today - past) / past * 100, 2)


def get_today_prices(db: Session) -> PricesTodayResponse:
    today = date.today()
    d7 = today - timedelta(days=7)
    d30 = today - timedelta(days=30)

    rows = db.execute(
        select(Item, PriceHistory.price, PriceHistory.recorded_date)
        .join(PriceHistory, Item.id == PriceHistory.item_id)
        .where(PriceHistory.recorded_date == today)
        .order_by(Item.category, Item.name)
    ).all()

    items: list[PriceItem] = []
    for item, price, recorded_date in rows:
        price_float = float(price)
        past_7d = _get_price_on(db, item.id, d7)
        past_30d = _get_price_on(db, item.id, d30)

        items.append(PriceItem(
            item_id=item.id,
            code=item.code,
            name=item.name,
            category=item.category,
            unit=item.unit,
            price=price_float,
            recorded_date=recorded_date,
            change_7d=_change_rate(price_float, past_7d),
            change_30d=_change_rate(price_float, past_30d),
        ))

    return PricesTodayResponse(date=today, count=len(items), items=items)
