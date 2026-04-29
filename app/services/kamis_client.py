"""
KAMIS Open API 클라이언트.
API: 일별 부류별 도/소매가격정보 (dailyPriceByCategoryList)
"""

import logging
import ssl

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

_ACTION = "dailyPriceByCategoryList"


def _ssl_context() -> ssl.SSLContext:
    """KAMIS 서버는 구형 SSL을 사용 → 레거시 cipher 허용."""
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ctx.set_ciphers("DEFAULT:@SECLEVEL=0")
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


def _parse_price(value: str) -> float | None:
    """'3,500' → 3500.0, '-' / '' → None."""
    cleaned = value.replace(",", "").strip()
    if not cleaned or cleaned == "-":
        return None
    try:
        return float(cleaned)
    except ValueError:
        return None


async def fetch_category(category_code: str, regday: str) -> list[dict]:
    """
    KAMIS에서 특정 부류의 소매 가격 목록을 조회한다.

    Args:
        category_code: 부류코드 ("100"=식량, "200"=채소, "400"=과일, "500"=축산, "600"=수산)
        regday: 조회일 "YYYY-MM-DD"

    Returns:
        KAMIS item 배열 (각 항목: item_code, kind_code, rank, dpr1~dpr7 등)
        키 미설정 시 빈 리스트.
    """
    if not settings.kamis_cert_key:
        logger.warning("KAMIS API 키 미설정 — 수집 건너뜀")
        return []

    params = {
        "action": _ACTION,
        "p_cert_key": settings.kamis_cert_key,
        "p_cert_id": settings.kamis_cert_id,
        "p_returntype": "json",
        "p_product_cls_code": "01",        # 소매
        "p_item_category_code": category_code,
        "p_country_code": "1101",          # 서울
        "p_regday": regday,
        "p_convert_kg_yn": "N",
    }

    async with httpx.AsyncClient(
        timeout=15.0,
        follow_redirects=True,
        verify=_ssl_context(),
    ) as client:
        resp = await client.get(settings.kamis_base_url, params=params)
        resp.raise_for_status()
        data = resp.json()

    items: list[dict] = data.get("data", {}).get("item", [])
    logger.info(f"[KAMIS] category={category_code} / {regday} → {len(items)}건")
    return items


def find_item_row(
    rows: list[dict],
    kamis_item_code: str,
    kamis_kind_code: str,
    kamis_rank: str | None,
) -> dict | None:
    """rows에서 item_code + kind_code + rank가 일치하는 첫 번째 항목을 반환."""
    for row in rows:
        if row.get("item_code") != kamis_item_code:
            continue
        if row.get("kind_code") != kamis_kind_code:
            continue
        if kamis_rank and row.get("rank") != kamis_rank:
            continue
        return row
    return None


def extract_avg_year_price(row: dict) -> float | None:
    """dpr7(평년 가격)을 파싱해 반환. 없으면 None."""
    return _parse_price(row.get("dpr7", "-"))


def extract_price_and_date(row: dict, today: str) -> tuple[float, str] | None:
    """
    dpr1(당일) → dpr2(1일 전) 순으로 유효한 가격을 찾아 (price, date) 반환.
    둘 다 없으면 None.
    """
    from datetime import date, timedelta

    dpr1 = _parse_price(row.get("dpr1", "-"))
    if dpr1 is not None and dpr1 > 0:
        return dpr1, today

    dpr2 = _parse_price(row.get("dpr2", "-"))
    if dpr2 is not None and dpr2 > 0:
        yesterday = (date.fromisoformat(today) - timedelta(days=1)).isoformat()
        return dpr2, yesterday

    return None
