"""
APScheduler 설정 및 가격 수집 작업.
매일 06:00 KAMIS에서 전 품목 가격을 수집해 DB에 적재한다.
"""

import logging
from datetime import date

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler(timezone="Asia/Seoul")


async def collect_prices() -> None:
    """
    KAMIS 일별 가격 수집 → DB 적재.
    API 키 수령 후 아래 TODO 블록을 채울 것.
    """
    today = date.today().isoformat()
    logger.info(f"[수집 시작] {today}")

    # TODO: API 키 수령 후 구현
    # from app.database import SessionLocal
    # from app.models.item import Item
    # from app.models.price_history import PriceHistory
    # from app.services.kamis_client import fetch_daily_prices
    #
    # db = SessionLocal()
    # try:
    #     items = db.query(Item).all()
    #     for item in items:
    #         rows = await fetch_daily_prices(item.code, today)
    #         for row in rows:
    #             price = float(row.get("price", 0))
    #             if price <= 0:
    #                 continue
    #             record = PriceHistory(
    #                 item_id=item.id,
    #                 price=price,
    #                 recorded_date=date.fromisoformat(today),
    #                 source="kamis",
    #             )
    #             db.merge(record)  # upsert (UniqueConstraint 기준)
    #     db.commit()
    # except Exception as e:
    #     logger.error(f"[수집 오류] {e}")
    #     db.rollback()
    # finally:
    #     db.close()

    logger.info(f"[수집 완료] {today}")


def start_scheduler() -> None:
    scheduler.add_job(collect_prices, CronTrigger(hour=6, minute=0))
    scheduler.start()
    logger.info("스케줄러 시작 — 매일 06:00 가격 수집")


def stop_scheduler() -> None:
    scheduler.shutdown(wait=False)
    logger.info("스케줄러 종료")
