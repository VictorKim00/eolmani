from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.item import Item
from app.models.price_history import PriceHistory
from app.schemas.price import PriceHistoryPoint, PriceHistoryResponse, PriceItem, PricesTodayResponse


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

        change_avg = rate(item.avg_year_price) if item.avg_year_price else None

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
            change_avg=change_avg,
        ))

    display_date = max((i.recorded_date for i in items), default=today)
    return PricesTodayResponse(date=display_date, count=len(items), items=items)


def get_item_history(db: Session, item_code: str, days: int = 30) -> PriceHistoryResponse | None:
    item = db.execute(select(Item).where(Item.code == item_code)).scalar_one_or_none()
    if item is None:
        return None

    def _fetch_points(since: date) -> list[PriceHistoryPoint]:
        rows = db.execute(
            select(PriceHistory.recorded_date, PriceHistory.price)
            .where(PriceHistory.item_id == item.id)
            .where(PriceHistory.source == "kamis")
            .where(PriceHistory.recorded_date >= since)
            .order_by(PriceHistory.recorded_date)
        ).all()
        return [PriceHistoryPoint(date=r.recorded_date, price=float(r.price)) for r in rows]

    points = _fetch_points(date.today() - timedelta(days=days))

    # 쌀·곡물처럼 주간 업데이트 품목은 30일 창이 너무 좁음 → 1년으로 확장
    if len(points) < 7:
        points = _fetch_points(date.today() - timedelta(days=365))

    # current_price: 30일 창 데이터가 없어도 전체 이력에서 최신값 사용
    latest_row = db.execute(
        select(PriceHistory.recorded_date, PriceHistory.price)
        .where(PriceHistory.item_id == item.id)
        .where(PriceHistory.source == "kamis")
        .order_by(PriceHistory.recorded_date.desc())
        .limit(1)
    ).one_or_none()

    current_price = float(latest_row.price) if latest_row else 0.0
    current_date = latest_row.recorded_date if latest_row else date.today()

    def _price_at(d: date) -> float | None:
        row = db.execute(
            select(PriceHistory.price)
            .where(PriceHistory.item_id == item.id)
            .where(PriceHistory.source == "kamis")
            .where(PriceHistory.recorded_date == d)
        ).scalar_one_or_none()
        return float(row) if row else None

    def _rate(past: float | None) -> float | None:
        if past is None or past == 0 or current_price == 0:
            return None
        return round((current_price - past) / past * 100, 2)

    change_7d = _rate(_price_at(current_date - timedelta(days=7)))
    change_30d = _rate(_price_at(current_date - timedelta(days=30)))
    change_avg = _rate(float(item.avg_year_price)) if item.avg_year_price else None

    return PriceHistoryResponse(
        item_code=item.code,
        item_name=item.name,
        unit=item.unit,
        category=item.category,
        current_price=current_price,
        avg_year_price=float(item.avg_year_price) if item.avg_year_price else None,
        change_7d=change_7d,
        change_30d=change_30d,
        change_avg=change_avg,
        points=points,
    )
