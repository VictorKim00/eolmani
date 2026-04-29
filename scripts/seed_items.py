"""
품목 마스터 시드 데이터 스크립트 (KAMIS 실제 코드 기반)
실행: uv run python scripts/seed_items.py

KAMIS API 실제 호출로 확인된 코드값 사용 (2026-04-29 기준).
감귤(413)은 비시즌으로 현재 데이터 없음 — 코드만 등록.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import SessionLocal
from app.models.item import Item

# fmt: off
ITEMS = [
    # ── 곡물 (category 100) ─────────────────────────────────────────
    # 쌀 그룹: 20kg / 10kg (단위 다름 — 그룹으로 묶어 상세 탭에서 전환)
    {"code": "rice",       "name": "쌀 20kg",          "category": "곡물", "unit": "20kg",  "kamis_category_code": "100", "kamis_item_code": "111",  "kamis_kind_code": "01", "kamis_rank": "상품",  "group_code": "rice", "variant_label": "20kg",  "sort_order": 1},
    {"code": "rice_10kg",  "name": "쌀 10kg",          "category": "곡물", "unit": "10kg",  "kamis_category_code": "100", "kamis_item_code": "111",  "kamis_kind_code": "10", "kamis_rank": "상품",  "group_code": "rice", "variant_label": "10kg",  "sort_order": 2},
    {"code": "glutinous_rice", "name": "찹쌀",         "category": "곡물", "unit": "1kg",   "kamis_category_code": "100", "kamis_item_code": "112",  "kamis_kind_code": "01", "kamis_rank": "상품"},
    {"code": "sweet_potato",   "name": "고구마",       "category": "곡물", "unit": "1kg",   "kamis_category_code": "100", "kamis_item_code": "151",  "kamis_kind_code": "00", "kamis_rank": "상품"},
    {"code": "potato",         "name": "감자",         "category": "곡물", "unit": "100g",  "kamis_category_code": "100", "kamis_item_code": "152",  "kamis_kind_code": "04", "kamis_rank": "상품"},
    {"code": "bean",           "name": "콩",           "category": "곡물", "unit": "500g",  "kamis_category_code": "100", "kamis_item_code": "141",  "kamis_kind_code": "01", "kamis_rank": "상품"},
    # ── 버섯 (category 300 특용작물) ────────────────────────────────
    {"code": "oyster_mushroom",  "name": "느타리버섯", "category": "채소", "unit": "100g", "kamis_category_code": "300", "kamis_item_code": "315",  "kamis_kind_code": "00", "kamis_rank": "상품"},
    {"code": "enoki_mushroom",   "name": "팽이버섯",   "category": "채소", "unit": "150g", "kamis_category_code": "300", "kamis_item_code": "316",  "kamis_kind_code": "00", "kamis_rank": "상품"},
    {"code": "king_mushroom",    "name": "새송이버섯", "category": "채소", "unit": "100g", "kamis_category_code": "300", "kamis_item_code": "317",  "kamis_kind_code": "00", "kamis_rank": "상품"},
    # ── 채소 (category 200) ─────────────────────────────────────────
    {"code": "cabbage",     "name": "배추",            "category": "채소", "unit": "1포기", "kamis_category_code": "200", "kamis_item_code": "211",  "kamis_kind_code": "06", "kamis_rank": "상품"},
    {"code": "radish",      "name": "무",              "category": "채소", "unit": "1개",   "kamis_category_code": "200", "kamis_item_code": "231",  "kamis_kind_code": "06", "kamis_rank": "상품"},
    {"code": "onion",       "name": "양파",            "category": "채소", "unit": "1kg",   "kamis_category_code": "200", "kamis_item_code": "245",  "kamis_kind_code": "00", "kamis_rank": "상품"},
    {"code": "green_onion", "name": "대파",            "category": "채소", "unit": "1kg",   "kamis_category_code": "200", "kamis_item_code": "246",  "kamis_kind_code": "00", "kamis_rank": "상품"},
    {"code": "garlic",      "name": "마늘",            "category": "채소", "unit": "1kg",   "kamis_category_code": "200", "kamis_item_code": "258",  "kamis_kind_code": "01", "kamis_rank": "상품"},
    {"code": "spinach",     "name": "시금치",          "category": "채소", "unit": "100g",  "kamis_category_code": "200", "kamis_item_code": "213",  "kamis_kind_code": "00", "kamis_rank": "상품"},
    {"code": "cucumber",    "name": "오이",            "category": "채소", "unit": "10개",  "kamis_category_code": "200", "kamis_item_code": "223",  "kamis_kind_code": "02", "kamis_rank": "상품"},
    {"code": "zucchini",    "name": "애호박",          "category": "채소", "unit": "1개",   "kamis_category_code": "200", "kamis_item_code": "224",  "kamis_kind_code": "01", "kamis_rank": "상품"},
    {"code": "lettuce",     "name": "상추",            "category": "채소", "unit": "100g",  "kamis_category_code": "200", "kamis_item_code": "214",  "kamis_kind_code": "02", "kamis_rank": "상품"},
    {"code": "chili",       "name": "청양고추",        "category": "채소", "unit": "100g",  "kamis_category_code": "200", "kamis_item_code": "242",  "kamis_kind_code": "03", "kamis_rank": "상품"},
    {"code": "carrot",      "name": "당근",            "category": "채소", "unit": "1kg",   "kamis_category_code": "200", "kamis_item_code": "232",  "kamis_kind_code": "01", "kamis_rank": "상품"},
    {"code": "perilla",     "name": "깻잎",            "category": "채소", "unit": "100g",  "kamis_category_code": "200", "kamis_item_code": "253",  "kamis_kind_code": "00", "kamis_rank": "상품"},
    {"code": "tomato",      "name": "토마토",          "category": "채소", "unit": "1kg",   "kamis_category_code": "200", "kamis_item_code": "225",  "kamis_kind_code": "00", "kamis_rank": "상품"},
    # ── 과일 (category 400) ─────────────────────────────────────────
    {"code": "apple",       "name": "사과",            "category": "과일", "unit": "10개",  "kamis_category_code": "400", "kamis_item_code": "411",  "kamis_kind_code": "05", "kamis_rank": "상품"},
    {"code": "pear",        "name": "배",              "category": "과일", "unit": "10개",  "kamis_category_code": "400", "kamis_item_code": "412",  "kamis_kind_code": "01", "kamis_rank": "상품"},
    {"code": "mandarin",    "name": "감귤",            "category": "과일", "unit": "10개",  "kamis_category_code": "400", "kamis_item_code": "415",  "kamis_kind_code": "01", "kamis_rank": "상품"},  # 노지 감귤. 비시즌(4~9월) 데이터 없음
    {"code": "strawberry",  "name": "딸기",            "category": "과일", "unit": "100g",  "kamis_category_code": "200", "kamis_item_code": "226",  "kamis_kind_code": "00", "kamis_rank": "상품"},
    # ── 축산 (category 500) ─────────────────────────────────────────
    # 한우 그룹: 주요 4개 부위 (모두 100g, 1등급 기준)
    {"code": "beef_sirloin",    "name": "한우 등심",   "category": "축산", "unit": "100g", "kamis_category_code": "500", "kamis_item_code": "4301", "kamis_kind_code": "22", "kamis_rank": "1등급",  "group_code": "beef_korean", "variant_label": "등심",  "sort_order": 1},
    {"code": "beef_tenderloin", "name": "한우 안심",   "category": "축산", "unit": "100g", "kamis_category_code": "500", "kamis_item_code": "4301", "kamis_kind_code": "21", "kamis_rank": "1등급",  "group_code": "beef_korean", "variant_label": "안심",  "sort_order": 2},
    {"code": "beef_brisket",    "name": "한우 양지",   "category": "축산", "unit": "100g", "kamis_category_code": "500", "kamis_item_code": "4301", "kamis_kind_code": "40", "kamis_rank": "1등급",  "group_code": "beef_korean", "variant_label": "양지",  "sort_order": 3},
    {"code": "beef_ribs",       "name": "한우 갈비",   "category": "축산", "unit": "100g", "kamis_category_code": "500", "kamis_item_code": "4301", "kamis_kind_code": "50", "kamis_rank": "1등급",  "group_code": "beef_korean", "variant_label": "갈비",  "sort_order": 4},
    # 돼지고기 그룹: 삼겹살 / 목심 / 앞다리
    {"code": "pork_belly",      "name": "돼지 삼겹살", "category": "축산", "unit": "100g", "kamis_category_code": "500", "kamis_item_code": "4304", "kamis_kind_code": "27", "kamis_rank": "삼겹살", "group_code": "pork",        "variant_label": "삼겹살", "sort_order": 1},
    {"code": "pork_neck",       "name": "돼지 목심",   "category": "축산", "unit": "100g", "kamis_category_code": "500", "kamis_item_code": "4304", "kamis_kind_code": "68", "kamis_rank": "목심",   "group_code": "pork",        "variant_label": "목심",   "sort_order": 2},
    {"code": "pork_foreleg",    "name": "돼지 앞다리", "category": "축산", "unit": "100g", "kamis_category_code": "500", "kamis_item_code": "4304", "kamis_kind_code": "25", "kamis_rank": "앞다리", "group_code": "pork",        "variant_label": "앞다리", "sort_order": 3},
    {"code": "chicken",         "name": "닭고기",      "category": "축산", "unit": "1kg",  "kamis_category_code": "500", "kamis_item_code": "9901", "kamis_kind_code": "99", "kamis_rank": "육계(kg)"},
    {"code": "egg_30",          "name": "계란",        "category": "축산", "unit": "30구", "kamis_category_code": "500", "kamis_item_code": "9903", "kamis_kind_code": "23", "kamis_rank": "일반란"},
    # ── 수산 (category 600) ─────────────────────────────────────────
    {"code": "hairtail",  "name": "갈치",             "category": "수산", "unit": "1마리", "kamis_category_code": "600", "kamis_item_code": "613",  "kamis_kind_code": "03", "kamis_rank": "大"},
    {"code": "mackerel",  "name": "고등어",           "category": "수산", "unit": "1마리", "kamis_category_code": "600", "kamis_item_code": "611",  "kamis_kind_code": "05", "kamis_rank": "大"},
    {"code": "squid",     "name": "오징어",           "category": "수산", "unit": "1마리", "kamis_category_code": "600", "kamis_item_code": "619",  "kamis_kind_code": "04", "kamis_rank": "中"},
]
# fmt: on


def seed():
    db = SessionLocal()
    try:
        for item_data in ITEMS:
            existing = db.query(Item).filter(Item.code == item_data["code"]).first()
            if existing:
                for key, value in item_data.items():
                    setattr(existing, key, value)
                # 시드에 없는 group 필드는 None으로 리셋
                for field in ("group_code", "variant_label", "sort_order"):
                    if field not in item_data:
                        setattr(existing, field, 0 if field == "sort_order" else None)
                print(f"  [갱신] {item_data['name']}")
            else:
                db.add(Item(**item_data))
                print(f"  [신규] {item_data['name']}")

        db.commit()
        print(f"\n총 {len(ITEMS)}개 품목 시드 완료.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
