"""
APScheduler 설정 및 가격 수집 작업.
매일 06:00 / 15:00 (Asia/Seoul) 공공데이터포털 API로 전 지역·전 품목 가격을 수집해 DB에 적재한다.

수집 순서:
  1) 최근일자 API (전국 평균) — 품목당 1 call, 최신가 + 1주전/1개월전 기준가
  2) 기간별 API (지역별)     — 품목당 1 call (sgg_cd 미지정 → 전 지역 한번에)
"""

import asyncio
import logging
from datetime import date, timedelta

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.dialects.postgresql import insert

from app.database import SessionLocal
from app.models.item import Item
from app.models.price_history import PriceHistory
from app.services.kamis_client import (
    _parse_price,
    fetch_per_day,
    fetch_recent,
    find_grade_row,
    group_by_region,
)
from app.services.regions import REGION_CODES

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler(timezone="Asia/Seoul")

_CALL_INTERVAL = 0.3  # data.go.kr API 호출 간격 (초)


def _upsert(db, item_id: int, price: float, recorded_date: date, region_code: str) -> None:
    db.execute(
        insert(PriceHistory)
        .values(
            item_id=item_id,
            price=price,
            recorded_date=recorded_date,
            source="kamis",
            region_code=region_code,
        )
        .on_conflict_do_update(
            constraint="uq_price_item_date_source_region",
            set_={"price": price},
        )
    )


def _insert_ignore(db, item_id: int, price: float, recorded_date: date, region_code: str) -> None:
    db.execute(
        insert(PriceHistory)
        .values(
            item_id=item_id,
            price=price,
            recorded_date=recorded_date,
            source="kamis",
            region_code=region_code,
        )
        .on_conflict_do_nothing(constraint="uq_price_item_date_source_region")
    )


async def _collect_national(db, items: list[Item]) -> int:
    """최근일자 API → 전국 평균 가격 수집."""
    saved = 0
    for item in items:
        try:
            await asyncio.sleep(_CALL_INTERVAL)
            rows = await fetch_recent(
                item.kamis_category_code,
                item.kamis_item_code,
                item.kamis_kind_code or None,
            )
            row = find_grade_row(rows, item.kamis_rank, item.kamis_kind_code or None)
            if row is None:
                continue

            exmn_ymd_str = row.get("exmn_ymd", "")
            if not exmn_ymd_str:
                continue
            price_date = date.fromisoformat(exmn_ymd_str)

            price = _parse_price(row.get("exmn_dd_prc"))
            if price:
                _upsert(db, item.id, price, price_date, "")
                saved += 1

                avg_prc = _parse_price(row.get("yy1_bfr_prc"))
                if avg_prc:
                    item.avg_year_price = avg_prc

            ww1 = _parse_price(row.get("ww1_bfr_prc"))
            if ww1:
                _insert_ignore(db, item.id, ww1, price_date - timedelta(days=7), "")

            mm1 = _parse_price(row.get("mm1_bfr_prc"))
            if mm1:
                _insert_ignore(db, item.id, mm1, price_date - timedelta(days=30), "")

        except Exception as e:
            logger.warning(f"[전국/{item.code}] 최근일자 실패: {e}")

    return saved


async def _collect_regional(db, items: list[Item], today: date) -> int:
    """기간별 API → 지역별 가격 수집 (품목당 1 call, 전 지역 포함)."""
    today_str = today.strftime("%Y%m%d")
    saved = 0

    for item in items:
        try:
            await asyncio.sleep(_CALL_INTERVAL)
            rows = await fetch_per_day(
                item.kamis_category_code,
                item.kamis_item_code,
                today_str,
                today_str,
                item.kamis_kind_code or None,
            )
            if not rows:
                continue

            by_region = group_by_region(rows)
            for sgg_cd, region_rows in by_region.items():
                # '1000'=전국(축산), 그 외 시군구 코드
                if sgg_cd == "1000":
                    target_region = ""
                elif sgg_cd in REGION_CODES and sgg_cd != "":
                    target_region = sgg_cd
                else:
                    continue
                row = find_grade_row(region_rows, item.kamis_rank, item.kamis_kind_code or None)
                if row is None:
                    continue
                price = _parse_price(row.get("exmn_dd_prc"))
                if not price:
                    continue
                exmn_ymd_str = row.get("exmn_ymd", "")
                price_date = date.fromisoformat(exmn_ymd_str) if exmn_ymd_str else today
                # 전국 평균은 최근일자 API가 이미 upsert했을 수 있으므로 DO NOTHING
                if target_region == "":
                    _insert_ignore(db, item.id, price, price_date, "")
                else:
                    _upsert(db, item.id, price, price_date, target_region)
                saved += 1

        except Exception as e:
            logger.warning(f"[지역/{item.code}] 기간별 실패: {e}")

    return saved


async def collect_prices() -> None:
    """공공데이터포털 API → 전국 + 지역별 가격 수집 → DB 적재."""
    today = date.today()
    logger.info(f"[수집 시작] {today}")

    db = SessionLocal()
    try:
        items: list[Item] = db.query(Item).all()

        national = await _collect_national(db, items)
        db.commit()
        logger.info(f"[수집/전국] {national}건")

        regional = await _collect_regional(db, items, today)
        db.commit()
        logger.info(f"[수집/지역] {regional}건")

        logger.info(f"[수집 완료] {today} — total {national + regional}건")

    except Exception as e:
        logger.error(f"[수집 오류] {e}", exc_info=True)
        db.rollback()
    finally:
        db.close()


async def backfill_prices(date_from: date, date_to: date) -> None:
    """누락 날짜 백필용. 날짜 범위로 기간별 API 호출."""
    from_str = date_from.strftime("%Y%m%d")
    to_str = date_to.strftime("%Y%m%d")
    logger.info(f"[백필 시작] {date_from} ~ {date_to}")

    db = SessionLocal()
    try:
        items: list[Item] = db.query(Item).all()
        total = 0

        for item in items:
            try:
                await asyncio.sleep(_CALL_INTERVAL)
                rows = await fetch_per_day(
                    item.kamis_category_code,
                    item.kamis_item_code,
                    from_str,
                    to_str,
                    item.kamis_kind_code or None,
                )
                by_region = group_by_region(rows)

                for sgg_cd, region_rows in by_region.items():
                    if sgg_cd == "1000":
                        target_region = ""
                    elif sgg_cd in REGION_CODES and sgg_cd != "":
                        target_region = sgg_cd
                    else:
                        continue
                    by_date: dict[str, list[dict]] = {}
                    for row in region_rows:
                        d = row.get("exmn_ymd", "")
                        by_date.setdefault(d, []).append(row)

                    for ymd, date_rows in by_date.items():
                        row = find_grade_row(date_rows, item.kamis_rank, item.kamis_kind_code or None)
                        if row is None:
                            continue
                        price = _parse_price(row.get("exmn_dd_prc"))
                        if not price or not ymd:
                            continue
                        _insert_ignore(db, item.id, price, date.fromisoformat(ymd), target_region)
                        total += 1

            except Exception as e:
                logger.warning(f"[백필/{item.code}] 실패: {e}")

        db.commit()
        logger.info(f"[백필 완료] {date_from}~{date_to} — {total}건")

    except Exception as e:
        logger.error(f"[백필 오류] {e}", exc_info=True)
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
