"""
APScheduler 설정 및 가격 수집 작업.
매일 06:00 (Asia/Seoul) KAMIS에서 전 품목 가격을 수집해 DB에 적재한다.
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

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler(timezone="Asia/Seoul")


async def collect_prices() -> None:
    """KAMIS 일별 가격 수집 → DB 적재 (upsert)."""
    today = date.today().isoformat()
    logger.info(f"[수집 시작] {today}")

    db = SessionLocal()
    try:
        items: list[Item] = db.query(Item).all()

        # 카테고리별로 묶어서 API 호출 최소화
        categories: dict[str, list[Item]] = {}
        for item in items:
            categories.setdefault(item.kamis_category_code, []).append(item)

        total_saved = 0

        for category_code, cat_items in categories.items():
            if not category_code:
                continue

            rows = await fetch_category(category_code, today)
            if not rows:
                logger.warning(f"[{category_code}] 응답 없음 — 건너뜀")
                continue

            for item in cat_items:
                row = find_item_row(
                    rows,
                    item.kamis_item_code,
                    item.kamis_kind_code,
                    item.kamis_rank,
                )
                if row is None:
                    logger.debug(f"매핑 없음: {item.name} ({item.kamis_item_code}/{item.kamis_kind_code})")
                    continue

                result = extract_price_and_date(row, today)
                if result is None:
                    logger.debug(f"유효 가격 없음: {item.name}")
                    continue

                price, price_date = result

                # upsert: 같은 (item_id, recorded_date, source) 있으면 price 갱신
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
                total_saved += 1
                logger.debug(f"저장: {item.name} = {price:,.0f}원 ({price_date})")

                # 평년 가격(dpr7) 갱신
                avg_year = extract_avg_year_price(row)
                if avg_year is not None:
                    item.avg_year_price = avg_year

                # dpr3(1주일 전)·dpr5(1개월 전) 기준가 저장 — 별도 백필 없이 변동률 확보
                for ref_price, ref_date in extract_reference_prices(row, today):
                    ref_stmt = (
                        insert(PriceHistory)
                        .values(
                            item_id=item.id,
                            price=ref_price,
                            recorded_date=date.fromisoformat(ref_date),
                            source="kamis",
                        )
                        .on_conflict_do_nothing(
                            constraint="uq_price_item_date_source",
                        )
                    )
                    db.execute(ref_stmt)

        db.commit()
        logger.info(f"[수집 완료] {today} — {total_saved}건 저장")

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
