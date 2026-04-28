"""
KAMIS Open API 클라이언트.
API 키 수령 후 fetch_daily_prices 내부를 채울 것.
현재: 키 없으면 빈 리스트 반환.
"""

import logging

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

# KAMIS 소매가격 일별 조회 액션
_ACTION = "dailySalesList"


async def fetch_daily_prices(item_code: str, target_date: str) -> list[dict]:
    """
    KAMIS에서 특정 품목의 특정일 소매 가격을 조회한다.

    Args:
        item_code: KAMIS 품목 코드 (예: "411" = 사과)
        target_date: 조회일 "YYYY-MM-DD"

    Returns:
        KAMIS API item 배열. 키 미설정 시 빈 리스트.
    """
    if not settings.kamis_cert_key:
        logger.warning("KAMIS API 키 미설정 — 수집 건너뜀")
        return []

    params = {
        "action": _ACTION,
        "p_cert_key": settings.kamis_cert_key,
        "p_cert_id": settings.kamis_cert_id,
        "p_returntype": "json",
        "p_itemcode": item_code,
        "p_startday": target_date,
        "p_endday": target_date,
        "p_convert_kg_yn": "N",
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(settings.kamis_base_url, params=params)
        resp.raise_for_status()
        data = resp.json()

    items = data.get("data", {}).get("item", [])
    logger.info(f"[KAMIS] {item_code} / {target_date} → {len(items)}건")
    return items
