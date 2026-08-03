"""
공공데이터포털(data.go.kr) 농산물 가격 API 클라이언트.

APIs (KAMIS 데이터, WAF 우회):
  - 최근일자: GET https://apis.data.go.kr/B552845/recent/price
    → 전국 평균 최신가격 + 1일전/1주전/1개월전 기준가
  - 기간별:   GET https://apis.data.go.kr/B552845/perDay/price
    → 날짜 범위 + 지역(sgg_cd)별 소매가격
"""

import logging
from collections import defaultdict

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

_RECENT_URL = "https://apis.data.go.kr/B552845/recent/price"
_PER_DAY_URL = "https://apis.data.go.kr/B552845/perDay/price"


def _parse_price(value: str | None) -> float | None:
    if not value:
        return None
    cleaned = value.replace(",", "").strip()
    if not cleaned or cleaned == "-":
        return None
    try:
        v = float(cleaned)
        return v if v > 0 else None
    except ValueError:
        return None


def _extract_items(data: dict) -> list[dict]:
    items = data.get("response", {}).get("body", {}).get("items", {})
    if not items:
        return []
    item = items.get("item", [])
    return [item] if isinstance(item, dict) else (item or [])


async def fetch_recent(
    category_code: str,
    item_code: str,
    kind_code: str | None = None,  # 참고용, 필터에는 사용하지 않음 (계절별 품종 변동)
) -> list[dict]:
    """최근일자 API: 전국 평균 최신가격 조회 (날짜 지정 불필요)."""
    if not settings.data_go_kr_key:
        logger.warning("DATA_GO_KR_KEY 미설정 — 수집 건너뜀")
        return []

    params: dict = {
        "serviceKey": settings.data_go_kr_key,
        "returnType": "json",
        "pageNo": "1",
        "numOfRows": "100",
        "cond[se_cd::EQ]": "01",
        "cond[ctgry_cd::EQ]": category_code,
        "cond[item_cd::EQ]": item_code,
    }

    async with httpx.AsyncClient(timeout=20.0) as client:
        resp = await client.get(_RECENT_URL, params=params)
        if not resp.is_success:
            logger.warning(f"[최근일자] HTTP {resp.status_code} item={item_code}")
            resp.raise_for_status()
        data = resp.json()

    rows = _extract_items(data)
    logger.debug(f"[최근일자] item={item_code} → {len(rows)}건")
    return rows


async def fetch_per_day(
    category_code: str,
    item_code: str,
    date_from: str,  # YYYYMMDD
    date_to: str,    # YYYYMMDD
    kind_code: str | None = None,  # 참고용, 필터에는 사용하지 않음 (계절별 품종 변동)
    region_code: str | None = None,
) -> list[dict]:
    """기간별 소매가격 API. region_code 미지정 시 전 지역 반환."""
    if not settings.data_go_kr_key:
        return []

    params: dict = {
        "serviceKey": settings.data_go_kr_key,
        "returnType": "json",
        "pageNo": "1",
        "numOfRows": "500",
        "cond[exmn_ymd::GTE]": date_from,
        "cond[exmn_ymd::LTE]": date_to,
        "cond[se_cd::EQ]": "01",
        "cond[ctgry_cd::EQ]": category_code,
        "cond[item_cd::EQ]": item_code,
    }
    if region_code:
        params["cond[sgg_cd::EQ]"] = region_code

    async with httpx.AsyncClient(timeout=20.0) as client:
        resp = await client.get(_PER_DAY_URL, params=params)
        if not resp.is_success:
            logger.warning(f"[기간별] HTTP {resp.status_code} item={item_code}")
            resp.raise_for_status()
        data = resp.json()

    rows = _extract_items(data)
    logger.debug(f"[기간별] item={item_code} {date_from}~{date_to} → {len(rows)}건")
    return rows


def find_grade_row(
    rows: list[dict],
    kamis_rank: str | None,
    kind_code: str | None = None,
) -> dict | None:
    """
    등급명(grd_nm) 기준으로 일치하는 row 선택.
    kind_code 제공 시 vrty_cd+grd_nm 완전 일치를 우선하고,
    없으면 grd_nm만 일치하는 row, 그래도 없으면 첫 번째 row를 반환.
    """
    if not rows:
        return None
    if not kamis_rank:
        return rows[0]
    # 1순위: 품종 + 등급 완전 일치
    if kind_code:
        for row in rows:
            if row.get("vrty_cd") == kind_code and row.get("grd_nm") == kamis_rank:
                return row
    # 2순위: 등급만 일치
    for row in rows:
        if row.get("grd_nm") == kamis_rank:
            return row
    # 3순위: 첫 번째 row (계절 품종 변동 시 폴백)
    return rows[0]


def group_by_region(rows: list[dict]) -> dict[str, list[dict]]:
    """기간별 API 결과를 sgg_cd 별로 그루핑."""
    groups: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        sgg_cd = row.get("sgg_cd", "")
        groups[sgg_cd].append(row)
    return dict(groups)
