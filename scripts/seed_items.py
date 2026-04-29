"""
품목 마스터 시드 데이터 스크립트 (KAMIS 실제 코드 기반)
실행: uv run python scripts/seed_items.py

KAMIS API 실제 호출로 확인된 코드값 사용 (2026-04-28 기준).
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
    {"code": "rice",    "name": "쌀",              "category": "곡물", "unit": "20kg",  "kamis_category_code": "100", "kamis_item_code": "111",  "kamis_kind_code": "01", "kamis_rank": "상품"},
    {"code": "bean",    "name": "콩",              "category": "곡물", "unit": "500g",  "kamis_category_code": "100", "kamis_item_code": "141",  "kamis_kind_code": "01", "kamis_rank": "상품"},
    # ── 채소 (category 200) ─────────────────────────────────────────
    {"code": "cabbage", "name": "배추",            "category": "채소", "unit": "1포기", "kamis_category_code": "200", "kamis_item_code": "211",  "kamis_kind_code": "06", "kamis_rank": "상품"},
    {"code": "radish",  "name": "무",              "category": "채소", "unit": "1개",   "kamis_category_code": "200", "kamis_item_code": "231",  "kamis_kind_code": "06", "kamis_rank": "상품"},
    {"code": "onion",   "name": "양파",            "category": "채소", "unit": "1kg",   "kamis_category_code": "200", "kamis_item_code": "245",  "kamis_kind_code": "00", "kamis_rank": "상품"},
    {"code": "green_onion", "name": "대파",        "category": "채소", "unit": "1kg",   "kamis_category_code": "200", "kamis_item_code": "246",  "kamis_kind_code": "00", "kamis_rank": "상품"},
    {"code": "garlic",  "name": "마늘",            "category": "채소", "unit": "1kg",   "kamis_category_code": "200", "kamis_item_code": "258",  "kamis_kind_code": "01", "kamis_rank": "상품"},
    {"code": "spinach", "name": "시금치",          "category": "채소", "unit": "100g",  "kamis_category_code": "200", "kamis_item_code": "213",  "kamis_kind_code": "00", "kamis_rank": "상품"},
    {"code": "cucumber","name": "오이",            "category": "채소", "unit": "10개",  "kamis_category_code": "200", "kamis_item_code": "223",  "kamis_kind_code": "02", "kamis_rank": "상품"},
    {"code": "zucchini","name": "애호박",          "category": "채소", "unit": "1개",   "kamis_category_code": "200", "kamis_item_code": "224",  "kamis_kind_code": "01", "kamis_rank": "상품"},
    {"code": "lettuce",  "name": "상추",           "category": "채소", "unit": "100g",  "kamis_category_code": "200", "kamis_item_code": "214",  "kamis_kind_code": "02", "kamis_rank": "상품"},  # 청상추 100g
    {"code": "chili",   "name": "청양고추",        "category": "채소", "unit": "100g",  "kamis_category_code": "200", "kamis_item_code": "242",  "kamis_kind_code": "03", "kamis_rank": "상품"},
    {"code": "carrot",  "name": "당근",            "category": "채소", "unit": "1kg",   "kamis_category_code": "200", "kamis_item_code": "232",  "kamis_kind_code": "01", "kamis_rank": "상품"},
    {"code": "perilla", "name": "깻잎",            "category": "채소", "unit": "100g",  "kamis_category_code": "200", "kamis_item_code": "253",  "kamis_kind_code": "00", "kamis_rank": "상품"},
    {"code": "tomato",  "name": "토마토",          "category": "채소", "unit": "1kg",   "kamis_category_code": "200", "kamis_item_code": "225",  "kamis_kind_code": "00", "kamis_rank": "상품"},
    # ── 과일 (category 400) ─────────────────────────────────────────
    {"code": "apple",   "name": "사과",            "category": "과일", "unit": "10개",  "kamis_category_code": "400", "kamis_item_code": "411",  "kamis_kind_code": "05", "kamis_rank": "상품"},
    {"code": "pear",    "name": "배",              "category": "과일", "unit": "10개",  "kamis_category_code": "400", "kamis_item_code": "412",  "kamis_kind_code": "01", "kamis_rank": "상품"},
    {"code": "mandarin","name": "감귤",            "category": "과일", "unit": "10개",  "kamis_category_code": "400", "kamis_item_code": "413",  "kamis_kind_code": "01", "kamis_rank": "상품"},  # 비시즌 시 데이터 없음
    # ── 축산 (category 500) ─────────────────────────────────────────
    {"code": "beef_sirloin", "name": "소고기(한우 등심)", "category": "축산", "unit": "100g", "kamis_category_code": "500", "kamis_item_code": "4301", "kamis_kind_code": "22", "kamis_rank": "1등급"},
    {"code": "pork_belly",   "name": "돼지고기(삼겹살)", "category": "축산", "unit": "100g", "kamis_category_code": "500", "kamis_item_code": "4304", "kamis_kind_code": "27", "kamis_rank": "삼겹살"},
    {"code": "chicken",      "name": "닭고기",          "category": "축산", "unit": "1kg",  "kamis_category_code": "500", "kamis_item_code": "9901", "kamis_kind_code": "99", "kamis_rank": "육계(kg)"},
    {"code": "egg_30",       "name": "계란",            "category": "축산", "unit": "30구", "kamis_category_code": "500", "kamis_item_code": "9903", "kamis_kind_code": "23", "kamis_rank": "일반란"},
    # ── 수산 (category 600) ─────────────────────────────────────────
    {"code": "hairtail", "name": "갈치",          "category": "수산", "unit": "1마리", "kamis_category_code": "600", "kamis_item_code": "613",  "kamis_kind_code": "03", "kamis_rank": "大"},
    {"code": "mackerel", "name": "고등어",        "category": "수산", "unit": "1마리", "kamis_category_code": "600", "kamis_item_code": "611",  "kamis_kind_code": "05", "kamis_rank": "大"},
    {"code": "squid",    "name": "오징어",        "category": "수산", "unit": "1마리", "kamis_category_code": "600", "kamis_item_code": "619",  "kamis_kind_code": "04", "kamis_rank": "中"},
]
# fmt: on


def seed():
    db = SessionLocal()
    try:
        for item_data in ITEMS:
            existing = db.query(Item).filter(Item.code == item_data["code"]).first()
            if existing:
                # 코드 업데이트 (기존 레코드 갱신)
                for key, value in item_data.items():
                    setattr(existing, key, value)
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
