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

# data.go.kr는 numOfRows를 최대 1000으로 캡한다. 그 이상은 pageNo로 순회해야 한다.
_MAX_ROWS_PER_PAGE = 1000
_MAX_PAGES = 50  # 안전장치 (품목·기간당 5만건이면 충분)


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


def _total_count(data: dict) -> int:
    try:
        return int(data.get("response", {}).get("body", {}).get("totalCount", 0))
    except (TypeError, ValueError):
        return 0


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

    base_params: dict = {
        "serviceKey": settings.data_go_kr_key,
        "returnType": "json",
        "numOfRows": str(_MAX_ROWS_PER_PAGE),
        "cond[exmn_ymd::GTE]": date_from,
        "cond[exmn_ymd::LTE]": date_to,
        "cond[se_cd::EQ]": "01",
        "cond[ctgry_cd::EQ]": category_code,
        "cond[item_cd::EQ]": item_code,
    }
    if region_code:
        base_params["cond[sgg_cd::EQ]"] = region_code

    rows: list[dict] = []
    async with httpx.AsyncClient(timeout=20.0) as client:
        for page in range(1, _MAX_PAGES + 1):
            resp = await client.get(_PER_DAY_URL, params={**base_params, "pageNo": str(page)})
            if not resp.is_success:
                logger.warning(f"[기간별] HTTP {resp.status_code} item={item_code} page={page}")
                resp.raise_for_status()
            data = resp.json()
            page_rows = _extract_items(data)
            rows.extend(page_rows)
            total = _total_count(data)
            if len(rows) >= total or len(page_rows) < _MAX_ROWS_PER_PAGE:
                break
        else:
            logger.warning(f"[기간별] item={item_code} {date_from}~{date_to} — {_MAX_PAGES}페이지 초과, 잘림")

    logger.debug(f"[기간별] item={item_code} {date_from}~{date_to} → {len(rows)}건")
    return rows


def find_grade_row(
    rows: list[dict],
    kamis_rank: str | None,
    kind_code: str | None = None,
) -> dict | None:
    """
    등급명(grd_nm) 기준으로 일치하는 row 선택.
    kind_code 제공 시 vrty_cd+grd_nm 완전 일치를 우선하고, 없으면 grd_nm만 일치하는 row.
    둘 다 없으면 None — 엉뚱한 품종·등급 가격을 저장하느니 결측이 낫다.
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
    # 매칭 실패: 조용히 rows[0]을 쓰면 다른 품종 가격이 저장되므로 결측 처리 + 경고
    grades = sorted({r.get("grd_nm") for r in rows})
    varieties = sorted({r.get("vrty_cd") for r in rows})
    logger.warning(
        f"[등급 매칭 실패] rank={kamis_rank!r} kind={kind_code!r} — "
        f"응답 등급={grades} 품종={varieties} — 이 건 건너뜀"
    )
    return None


def group_by_region(rows: list[dict]) -> dict[str, list[dict]]:
    """기간별 API 결과를 sgg_cd 별로 그루핑."""
    groups: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        sgg_cd = row.get("sgg_cd", "")
        groups[sgg_cd].append(row)
    return dict(groups)
