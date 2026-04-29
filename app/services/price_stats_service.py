"""
KAMIS 누적 데이터 기반 월별 가격 통계.
품목별로 '이번 달이 연평균 대비 얼마나 싼지/비싼지'를 계산한다.
"""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.item import Item
from app.models.price_history import PriceHistory


def get_month_vs_annual(db: Session, item_code: str, month: int) -> dict | None:
    """
    해당 품목의 특정 월 평균가 vs 연간 평균가 비교.
    반환: {month_avg, annual_avg, pct_diff, label, data_days}
    데이터 부족(30일 미만)이면 None 반환.
    """
    item = db.execute(select(Item).where(Item.code == item_code)).scalar_one_or_none()
    if item is None:
        return None

    # 특정 월 평균가 (모든 연도 합산)
    month_avg = db.execute(
        select(func.avg(PriceHistory.price))
        .where(PriceHistory.item_id == item.id)
        .where(PriceHistory.source == "kamis")
        .where(func.extract("month", PriceHistory.recorded_date) == month)
    ).scalar()

    # 특정 월 데이터 수
    month_days = db.execute(
        select(func.count(PriceHistory.id))
        .where(PriceHistory.item_id == item.id)
        .where(PriceHistory.source == "kamis")
        .where(func.extract("month", PriceHistory.recorded_date) == month)
    ).scalar() or 0

    # 연간 전체 평균가
    annual_avg = db.execute(
        select(func.avg(PriceHistory.price))
        .where(PriceHistory.item_id == item.id)
        .where(PriceHistory.source == "kamis")
    ).scalar()

    if month_avg is None or annual_avg is None or month_days < 10:
        return None

    month_avg = float(month_avg)
    annual_avg = float(annual_avg)
    pct_diff = round((month_avg - annual_avg) / annual_avg * 100, 1)

    if pct_diff <= -8:
        label = f"역사적으로 저렴한 달 ({pct_diff:+.0f}%)"
    elif pct_diff <= -3:
        label = f"연평균보다 저렴한 편 ({pct_diff:+.0f}%)"
    elif pct_diff >= 8:
        label = f"역사적으로 비싼 달 ({pct_diff:+.0f}%)"
    elif pct_diff >= 3:
        label = f"연평균보다 비싼 편 ({pct_diff:+.0f}%)"
    else:
        label = f"연평균과 비슷한 시기 ({pct_diff:+.0f}%)"

    return {
        "month_avg": month_avg,
        "annual_avg": annual_avg,
        "pct_diff": pct_diff,
        "label": label,
        "data_days": month_days,
    }


def enrich_season_picks(db: Session, picks: list[dict], month: int) -> list[dict]:
    """
    시즌 picks에 실제 월별 통계를 붙여 반환.
    item_code가 있는 품목만 통계 추가, 없으면 그대로.
    """
    for pick in picks:
        code = pick.get("item_code")
        if not code:
            continue
        stats = get_month_vs_annual(db, code, month)
        pick["stats"] = stats  # None이면 아직 데이터 부족

    return picks
