"""
시즌 대량구매 캘린더 — 월별 추천 품목.
item_code가 있는 품목은 실제 KAMIS 가격 데이터와 연결됨.
item_code가 None인 품목은 우리가 추적하지 않는 품목 (시즌 팁 제공).
"""

from datetime import date


SEASON_CALENDAR: dict[int, list[dict]] = {
    1: [
        {"emoji": "🍊", "name": "한라봉·감귤", "reason": "겨울 제철 절정", "item_code": "mandarin"},
        {"emoji": "🐟", "name": "갈치", "reason": "겨울 제철 수산물", "item_code": "hairtail"},
        {"emoji": "🍓", "name": "딸기", "reason": "출하 피크 — 1~2월이 연중 최대 물량", "item_code": "strawberry"},
    ],
    2: [
        {"emoji": "🍓", "name": "딸기", "reason": "제철 막바지 — 잼·청 담기 좋은 시기", "item_code": "strawberry"},
        {"emoji": "🐟", "name": "고등어", "reason": "겨울 제철 수산물", "item_code": "mackerel"},
        {"emoji": "🥬", "name": "시금치", "reason": "봄 출하 시작 — 겨울보다 저렴해지는 시기", "item_code": "spinach"},
    ],
    3: [
        {"emoji": "🌿", "name": "봄나물 (냉이·달래·쑥)", "reason": "봄 제철 절정 — 지금 아니면 내년까지", "item_code": None},
        {"emoji": "🥬", "name": "시금치", "reason": "봄 출하 시작", "item_code": "spinach"},
        {"emoji": "🥬", "name": "배추", "reason": "봄 배추 출하", "item_code": "cabbage"},
    ],
    4: [
        {"emoji": "🍓", "name": "딸기", "reason": "봄 제철 막바지 — 마지막 제철 딸기 시기", "item_code": "strawberry"},
        {"emoji": "🧅", "name": "양파", "reason": "햇양파 출하 전, 시즌 직전 가격 확인", "item_code": "onion"},
        {"emoji": "🥬", "name": "시금치", "reason": "봄 출하 피크 시기", "item_code": "spinach"},
    ],
    5: [
        {"emoji": "🍉", "name": "수박", "reason": "초여름 출하 시작 — 6~7월이 연중 최저가", "item_code": "watermelon"},
        {"emoji": "🍈", "name": "참외", "reason": "제철 출하 시작 — 5~6월이 가장 달고 저렴", "item_code": "korean_melon"},
        {"emoji": "🥬", "name": "배추(봄)", "reason": "봄배추 출하 시작 — 월동배추보다 저렴", "item_code": "cabbage_spring"},
    ],
    6: [
        {"emoji": "🍉", "name": "수박", "reason": "여름 수박 절정 — 지금이 연중 최저가", "item_code": "watermelon"},
        {"emoji": "🍈", "name": "참외", "reason": "제철 절정 — 대량 소비 적기", "item_code": "korean_melon"},
        {"emoji": "🧄", "name": "마늘", "reason": "햇마늘 출하 절정 — 1년치 비축 시기", "item_code": "garlic"},
    ],
    7: [
        {"emoji": "🍉", "name": "수박", "reason": "여름 제철 절정 — 무더위 최대 소비 시기", "item_code": "watermelon"},
        {"emoji": "🥒", "name": "오이", "reason": "여름 제철 출하 피크", "item_code": "cucumber"},
        {"emoji": "🥬", "name": "애호박", "reason": "여름 제철 출하 피크", "item_code": "zucchini"},
    ],
    8: [
        {"emoji": "🍑", "name": "복숭아", "reason": "제철 절정 — 8월 안에 소비", "item_code": "peach"},
        {"emoji": "🍇", "name": "포도", "reason": "캠벨·샤인머스켓 출하 피크 — 대량 구매 적기", "item_code": "grape_campbell"},
        {"emoji": "🥒", "name": "오이", "reason": "여름 제철 절정", "item_code": "cucumber"},
    ],
    9: [
        {"emoji": "🍇", "name": "포도", "reason": "샤인머스켓 최성수기 — 추석 전 대량 구매", "item_code": "grape_shine"},
        {"emoji": "🍎", "name": "사과", "reason": "햇사과 출하 — 추석 전 대량 구매", "item_code": "apple"},
        {"emoji": "🍐", "name": "배", "reason": "햇배 출하 — 추석 전 대량 구매", "item_code": "pear"},
    ],
    10: [
        {"emoji": "🍎", "name": "사과", "reason": "추석 이후 가격 안정기", "item_code": "apple"},
        {"emoji": "🥬", "name": "배추(월동)", "reason": "김장 준비 — 10월 말이 가격 저점", "item_code": "cabbage"},
        {"emoji": "🧄", "name": "마늘", "reason": "김장용 양념 채소 — 미리 확보", "item_code": "garlic"},
    ],
    11: [
        {"emoji": "🥬", "name": "배추(월동)", "reason": "⭐ 김장 시즌 — 11월 초·중순 집중 확인", "item_code": "cabbage"},
        {"emoji": "🧅", "name": "양파", "reason": "김장 양념용", "item_code": "onion"},
        {"emoji": "🐟", "name": "갈치", "reason": "겨울 제철 시작", "item_code": "hairtail"},
    ],
    12: [
        {"emoji": "🐟", "name": "갈치", "reason": "겨울 제철 절정", "item_code": "hairtail"},
        {"emoji": "🐟", "name": "고등어", "reason": "겨울 제철 절정", "item_code": "mackerel"},
        {"emoji": "🍊", "name": "감귤", "reason": "겨울 감귤 출하 시작", "item_code": "mandarin"},
    ],
}


def get_this_month_season() -> dict:
    month = date.today().month
    return {
        "month": month,
        "picks": SEASON_CALENDAR.get(month, []),
    }
