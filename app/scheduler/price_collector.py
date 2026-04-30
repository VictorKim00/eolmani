"""
APScheduler 설정 및 가격 수집 작업.
매일 06:00 / 15:00 (Asia/Seoul) KAMIS에서 전 지역·전 품목 가격을 수집해 DB에 적재한다.
"""

import logging
from datetime import date

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.dialects.postgresql import insert

from app.database import SessionLocal
from app.models.item import Item
from app.models.price_history import PriceHistory
from app.services.kamis_client import extract_avg_year_price, extract_price_and_date, extract_reference_prices, fetch_category, find_item_row
from app.services.regions import REGIONS

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler(timezone="Asia/Seoul")


async def _collect_one_region(
    db,
    items_by_category: dict[str, list[Item]],
    today: str,
    region_code: str,
    region_name: str,
) -> int:
    """단일 지역 전체 카테고리 수집. 저장된 row 수 반환."""
    saved = 0
    for category_code, cat_items in items_by_category.items():
        if not category_code:
            continue
        try:
            rows = await fetch_category(category_code, today, country_code=region_code)
        except Exception as e:
            logger.warning(f"[{region_name}/{category_code}] fetch 실패: {e}")
            continue
        if not rows:
            continue

        for item in cat_items:
            row = find_item_row(rows, item.kamis_item_code, item.kamis_kind_code, item.kamis_rank)
            if row is None:
                continue

            result = extract_price_and_date(row, today)
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

            # 평년 가격(dpr7)은 전국 평균(region='')에서만 Item 컬럼 갱신
            if region_code == "":
                avg_year = extract_avg_year_price(row)
                if avg_year is not None:
                    item.avg_year_price = avg_year

            for ref_price, ref_date in extract_reference_prices(row, today):
                ref_stmt = (
                    insert(PriceHistory)
                    .values(
                        item_id=item.id,
                        price=ref_price,
                        recorded_date=date.fromisoformat(ref_date),
                        source="kamis",
                        region_code=region_code,
                    )
                    .on_conflict_do_nothing(constraint="uq_price_item_date_source_region")
                )
                db.execute(ref_stmt)

    return saved


async def collect_prices() -> None:
    """KAMIS 전 지역 가격 수집 → DB 적재 (upsert). 지역별로 commit해 부분 실패에 강함."""
    today = date.today().isoformat()
    logger.info(f"[수집 시작] {today}")

    db = SessionLocal()
    try:
        items: list[Item] = db.query(Item).all()
        items_by_category: dict[str, list[Item]] = {}
        for item in items:
            items_by_category.setdefault(item.kamis_category_code, []).append(item)

        total = 0
        for region_code, region_name in REGIONS:
            try:
                saved = await _collect_one_region(db, items_by_category, today, region_code, region_name)
                db.commit()
                logger.info(f"[수집/{region_name}] {saved}건")
                total += saved
            except Exception as e:
                logger.error(f"[수집/{region_name}] 실패: {e}", exc_info=True)
                db.rollback()

        logger.info(f"[수집 완료] {today} — total {total}건")

    except Exception as e:
        logger.error(f"[수집 오류] {e}", exc_info=True)
        db.rollback()
    finally:
        db.close()


def start_scheduler() -> None:
    scheduler.add_job(collect_prices, CronTrigger(hour=6, minute=0))
    scheduler.add_job(collect_prices, CronTrigger(hour=15, minute=0))
    scheduler.start()
    logger.info("스케줄러 시작 — 매일 06:00 / 15:00 가격 수집")


def stop_scheduler() -> None:
    scheduler.shutdown(wait=False)
    logger.info("스케줄러 종료")
