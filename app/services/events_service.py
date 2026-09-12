"""
명절·시즌 이벤트 프리셋 — 홈 화면에서 특정 품목만 모아 보여주는 용도.
season_service.py(월별 추천)와 달리, 사용자가 ?event=slug 로 명시적으로 선택했을 때만 노출된다.

새 명절(설날 등) 추가 시 이 딕셔너리에 항목만 추가하면 되고,
렌더링(카드·합산 배너·공유)은 index.html/main.py 로직을 그대로 재사용한다.
"""

EVENTS: dict[str, dict] = {
    "chuseok": {
        "title": "추석 성수품",
        "emoji": "🎑",
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
    return EVENTS.get(slug)
