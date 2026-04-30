from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.item import Item
from app.models.price_history import PriceHistory
from app.schemas.price import PriceHistoryPoint, PriceHistoryResponse, PriceItem, PricesTodayResponse


def _price_near(
    db: Session,
    item_id: int,
    target: date,
    region_code: str,
    window: int = 4,
) -> float | None:
    """
    target 날짜 직전 window일 이내 가장 최근 가격 반환.
    KAMIS가 dpr2(전일) 폴백으로 저장하거나 주말·휴일 공백이 생겨도 안전하게 조회.
    """
    row = db.execute(
        select(PriceHistory.price)
        .where(PriceHistory.item_id == item_id)
        .where(PriceHistory.source == "kamis")
        .where(PriceHistory.region_code == region_code)
        .where(PriceHistory.recorded_date <= target)
        .where(PriceHistory.recorded_date >= target - timedelta(days=window))
        .order_by(PriceHistory.recorded_date.desc())
        .limit(1)
    ).scalar_one_or_none()
    return float(row) if row else None


def _change_rate(current: float, past: float | None) -> float | None:
    if past is None or past == 0 or current == 0:
        return None
    return round((current - past) / past * 100, 2)


def get_today_prices(db: Session, region_code: str = "") -> PricesTodayResponse:
    """
    품목별 가장 최근 가격을 반환한다.
    오늘 데이터가 없으면 어제 데이터로 자동 폴백.
    region_code='' 이 전국 평균, '1101'=서울 등.
    """
    subq = (
        select(
            PriceHistory.item_id,
            PriceHistory.price,
            PriceHistory.recorded_date,
        )
        .distinct(PriceHistory.item_id)  # PostgreSQL DISTINCT ON 전용
        .where(PriceHistory.source == "kamis")
        .where(PriceHistory.region_code == region_code)
        .order_by(PriceHistory.item_id, PriceHistory.recorded_date.desc())
        .subquery()
    )

    rows = db.execute(
        select(Item, subq.c.price, subq.c.recorded_date)
        .join(subq, Item.id == subq.c.item_id)
        .order_by(Item.category, Item.name)
    ).all()

    today = date.today()

    # 지역 선택 시 전국 평균 가격을 한 번에 조회 (N+1 없이 vs_nation 계산)
    nation_price_by_item: dict[int, float] = {}
    if region_code != "":
        nation_subq = (
            select(PriceHistory.item_id, PriceHistory.price)
            .distinct(PriceHistory.item_id)
            .where(PriceHistory.source == "kamis")
            .where(PriceHistory.region_code == "")
            .order_by(PriceHistory.item_id, PriceHistory.recorded_date.desc())
            .subquery()
        )
        for item_id, p in db.execute(select(nation_subq.c.item_id, nation_subq.c.price)).all():
            nation_price_by_item[item_id] = float(p)

    items: list[PriceItem] = []

    for item, price, recorded_date in rows:
        price_float = float(price)
        past_7d  = _price_near(db, item.id, recorded_date - timedelta(days=7),  region_code)
        past_30d = _price_near(db, item.id, recorded_date - timedelta(days=30), region_code)

        vs_nation = None
        if region_code != "" and item.id in nation_price_by_item:
            np = nation_price_by_item[item.id]
            if np > 0:
                vs_nation = round((price_float - np) / np * 100, 1)

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
            change_avg=_change_rate(price_float, float(item.avg_year_price)) if item.avg_year_price else None,
            group_code=item.group_code,
            variant_label=item.variant_label,
            sort_order=item.sort_order,
            vs_nation=vs_nation,
        ))

    display_date = max((i.recorded_date for i in items), default=today)
    return PricesTodayResponse(date=display_date, region_code=region_code, count=len(items), items=items)


def get_item_history(db: Session, item_code: str, days: int = 30, region_code: str = "") -> PriceHistoryResponse | None:
    item = db.execute(select(Item).where(Item.code == item_code)).scalar_one_or_none()
    if item is None:
        return None

    def _fetch_points(since: date) -> list[PriceHistoryPoint]:
        rows = db.execute(
            select(PriceHistory.recorded_date, PriceHistory.price)
            .where(PriceHistory.item_id == item.id)
            .where(PriceHistory.source == "kamis")
            .where(PriceHistory.region_code == region_code)
            .where(PriceHistory.recorded_date >= since)
            .order_by(PriceHistory.recorded_date)
        ).all()
        return [PriceHistoryPoint(date=r.recorded_date, price=float(r.price)) for r in rows]

    points = _fetch_points(date.today() - timedelta(days=days))

    # 쌀·곡물처럼 주간 업데이트 품목은 30일 창이 너무 좁음 → 1년으로 확장
    if len(points) < 7:
        points = _fetch_points(date.today() - timedelta(days=365))

    # current_price: 전체 이력에서 해당 지역 최신값 사용
    latest_row = db.execute(
        select(PriceHistory.recorded_date, PriceHistory.price)
        .where(PriceHistory.item_id == item.id)
        .where(PriceHistory.source == "kamis")
        .where(PriceHistory.region_code == region_code)
        .order_by(PriceHistory.recorded_date.desc())
        .limit(1)
    ).one_or_none()

    current_price = float(latest_row.price) if latest_row else 0.0
    current_date  = latest_row.recorded_date if latest_row else date.today()

    change_7d  = _change_rate(current_price, _price_near(db, item.id, current_date - timedelta(days=7),  region_code))
    change_30d = _change_rate(current_price, _price_near(db, item.id, current_date - timedelta(days=30), region_code))
    change_avg = _change_rate(current_price, float(item.avg_year_price)) if item.avg_year_price else None

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
