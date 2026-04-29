"""
과거 N일치 가격 백필 스크립트.

사용법:
    uv run python scripts/backfill.py          # 기본 30일
    uv run python scripts/backfill.py --days 7

Railway에서 실행하려면 Railway CLI 또는 Railway 콘솔에서:
    python scripts/backfill.py --days 30
"""

import asyncio
import argparse
import logging
import sys
from datetime import date, timedelta

# 프로젝트 루트를 sys.path에 추가
sys.path.insert(0, ".")

from sqlalchemy.dialects.postgresql import insert

from app.database import SessionLocal
from app.models.item import Item
from app.models.price_history import PriceHistory
from app.services.kamis_client import extract_price_and_date, fetch_category, find_item_row

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)


async def backfill_date(target_date: date, items: list[Item]) -> int:
    """특정 날짜의 전 품목 가격을 수집해 DB에 upsert. 저장 건수 반환."""
    regday = target_date.isoformat()

    # 카테고리별로 묶어서 API 호출 최소화
    categories: dict[str, list[Item]] = {}
    for item in items:
        if item.kamis_category_code:
            categories.setdefault(item.kamis_category_code, []).append(item)

    saved = 0
    db = SessionLocal()
    try:
        for category_code, cat_items in categories.items():
            rows = await fetch_category(category_code, regday)
            if not rows:
                logger.warning(f"  [{category_code}] 응답 없음")
                continue

            for item in cat_items:
                row = find_item_row(
                    rows,
                    item.kamis_item_code,
                    item.kamis_kind_code,
                    item.kamis_rank,
                )
                if row is None:
                    continue

                result = extract_price_and_date(row, regday)
                if result is None:
                    continue

                price, price_date = result

                stmt = (
                    insert(PriceHistory)
                    .values(
                        item_id=item.id,
                        price=price,
                        recorded_date=date.fromisoformat(price_date),
                        source="kamis",
                    )
                    .on_conflict_do_update(
                        constraint="uq_price_item_date_source",
                        set_={"price": price},
                    )
                )
                db.execute(stmt)
                saved += 1

        db.commit()
    except Exception as e:
        logger.error(f"  오류: {e}", exc_info=True)
        db.rollback()
    finally:
        db.close()

    return saved


async def main(days: int) -> None:
    today = date.today()
    db = SessionLocal()
    items: list[Item] = db.query(Item).all()
    db.close()

    logger.info(f"백필 시작 — 과거 {days}일, 품목 {len(items)}종")

    total = 0
    for i in range(days, -1, -1):  # -1 포함: 오늘(i=0)도 수집
        target = today - timedelta(days=i)

        # 주말(토=5, 일=6)은 KAMIS 데이터 없음 → 건너뜀
        if target.weekday() >= 5:
            logger.info(f"{target} (주말) — 건너뜀")
            continue

        logger.info(f"{target} 수집 중...")
        saved = await backfill_date(target, items)
        logger.info(f"  → {saved}건 저장")
        total += saved

        # API 부하 방지
        await asyncio.sleep(1.5)

    logger.info(f"백필 완료 — 총 {total}건 저장")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="KAMIS 가격 백필")
    parser.add_argument("--days", type=int, default=30, help="과거 몇 일치 수집 (기본 30)")
    args = parser.parse_args()

    asyncio.run(main(args.days))
