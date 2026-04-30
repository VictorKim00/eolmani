"""
과거 N일치 가격 백필 스크립트.

사용법:
    uv run python scripts/backfill.py                      # 전국 평균 30일
    uv run python scripts/backfill.py --days 7
    uv run python scripts/backfill.py --new-regions        # 신규 18개 지역만 30일
    uv run python scripts/backfill.py --all-regions        # 전체 24개 지역 30일

Railway에서 실행:
    python scripts/backfill.py --new-regions --days 30
"""

import asyncio
import argparse
import logging
import sys
from datetime import date, timedelta

sys.path.insert(0, ".")

from sqlalchemy.dialects.postgresql import insert

from app.database import SessionLocal
from app.models.item import Item
from app.models.price_history import PriceHistory
from app.services.kamis_client import extract_price_and_date, fetch_category, find_item_row
from app.services.regions import REGIONS

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)

# 기존에 수집하던 6개 지역 (전국 + 5개 광역시)
OLD_REGION_CODES = {"", "1101", "2100", "2200", "2300", "2401", "2501"}

# 이번에 추가된 18개 지역
NEW_REGION_CODES = {code for code, _ in REGIONS if code not in OLD_REGION_CODES}


async def backfill_date(target_date: date, items: list[Item], region_code: str, region_name: str) -> int:
    regday = target_date.isoformat()

    categories: dict[str, list[Item]] = {}
    for item in items:
        if item.kamis_category_code:
            categories.setdefault(item.kamis_category_code, []).append(item)

    saved = 0
    db = SessionLocal()
    try:
        for category_code, cat_items in categories.items():
            try:
                rows = await fetch_category(category_code, regday, country_code=region_code)
            except Exception as e:
                logger.warning(f"  [{region_name}/{category_code}] fetch 실패: {e}")
                continue
            if not rows:
                continue

            for item in cat_items:
                row = find_item_row(rows, item.kamis_item_code, item.kamis_kind_code, item.kamis_rank)
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
                        region_code=region_code,
                    )
                    .on_conflict_do_update(
                        constraint="uq_price_item_date_source_region",
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


async def main(days: int, region_codes: list[tuple[str, str]]) -> None:
    today = date.today()
    db = SessionLocal()
    try:
        items: list[Item] = db.query(Item).all()
    finally:
        db.close()

    logger.info(f"백필 시작 — 과거 {days}일, 품목 {len(items)}종, 지역 {len(region_codes)}개")

    total = 0
    for region_code, region_name in region_codes:
        logger.info(f"\n=== {region_name} ({region_code or '전국'}) ===")
        for i in range(days, -1, -1):
            target = today - timedelta(days=i)

            if target.weekday() >= 5:
                continue

            saved = await backfill_date(target, items, region_code, region_name)
            if saved:
                logger.info(f"  {target} → {saved}건")
            total += saved

            await asyncio.sleep(0.8)

    logger.info(f"\n백필 완료 — 총 {total}건 저장")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="KAMIS 가격 백필")
    parser.add_argument("--days", type=int, default=30, help="과거 몇 일치 수집 (기본 30)")

    group = parser.add_mutually_exclusive_group()
    group.add_argument("--new-regions", action="store_true", help="신규 추가 18개 지역만")
    group.add_argument("--all-regions", action="store_true", help="전체 24개 지역")

    args = parser.parse_args()

    if args.all_regions:
        target_regions = REGIONS
    elif args.new_regions:
        target_regions = [(code, name) for code, name in REGIONS if code in NEW_REGION_CODES]
    else:
        target_regions = [("", "전국 평균")]

    asyncio.run(main(args.days, target_regions))
