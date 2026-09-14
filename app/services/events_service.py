"""
명절·시즌 이벤트 프리셋 — 홈 화면에서 특정 품목만 모아 보여주는 용도.
season_service.py(월별 추천)와 달리 홈 전체를 덮는 배너 형태.

- date_from~date_to 기간 안에는 ?event= 파라미터 없이도 홈에 자동으로 뜬다
  (공유 안 해도 그냥 들어온 사람도 보게 하기 위함).
- ?event=slug 로 명시적으로 접근하면 기간과 무관하게 항상 뜬다 — 공유 링크가
  기간 종료 후에도 깨지지 않게 하기 위함.

새 명절(설날 등) 추가 시 이 딕셔너리에 항목만 추가하면 되고,
렌더링(카드·합산 배너·공유)은 index.html/main.py 로직을 그대로 재사용한다.
"""

from datetime import date

EVENTS: dict[str, dict] = {
    "chuseok": {
        "title": "추석 성수품",
        "emoji": "🎑",
        "date_from": date(2026, 9, 1),
        "date_to": date(2026, 9, 27),  # 추석(9/25) + 이틀 여유
        # 배너의 개별 품목 링크(쿠팡에서 보기)는 평균가와 단위가 맞는 일반 상품 그대로 둔다.
        # 이건 별도의 "선물세트" CTA용 — 품목별(9개) 대신 카테고리 3개로 묶음
        # (과일/한우/수산은 실제로도 세트 상품이 부위·품종 안 가리고 묶여서 팔림).
        # url이 None인 동안은 일반(비추적) 쿠팡 검색 링크로 대체된다.
        # 파트너스에서 링크 만들면 url 자리만 채워넣으면 됨.
        "gift_sets": [
            {"label": "🍎 과일 선물세트", "query": "추석 과일 선물세트", "url": None},
            {"label": "🥩 정육 선물세트", "query": "한우 선물세트", "url": None},
            {"label": "🐟 수산물 세트", "query": "수산물 선물세트", "url": None},
        ],
        # 차례상·선물세트에서 자주 쓰이는 품목 순서대로. item_code는 seed_items.py 기준.
        "item_codes": [
            "apple", "pear",
            "beef_sirloin", "beef_tenderloin", "beef_brisket", "beef_ribs",
            "egg_30",
            "pollack", "hairtail",
            # croaker(조기)는 제외 — 전국 평균 소스가 7월 초부터 끊겨 있어(별도 조사 필요)
            # 여기 넣으면 두 달 된 가격이 "오늘 합산"에 섞이게 됨. 고쳐지면 다시 추가할 것.
        ],
    },
}


def get_event(slug: str) -> dict | None:
    """slug로 명시 조회 — 기간과 무관하게 항상 반환(공유 링크용)."""
    return EVENTS.get(slug)


def get_active_event(today: date | None = None) -> tuple[str, dict] | None:
    """오늘 날짜가 기간에 포함되는 이벤트를 자동으로 찾는다 (?event= 없이 홈 기본 노출용).
    여러 개가 겹치면 date_from이 더 이른 것을 우선한다."""
    today = today or date.today()
    candidates = [
        (slug, ev) for slug, ev in EVENTS.items()
        if ev["date_from"] <= today <= ev["date_to"]
    ]
    if not candidates:
        return None
    return min(candidates, key=lambda pair: pair[1]["date_from"])
