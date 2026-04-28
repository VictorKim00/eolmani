"""
품목 마스터 시드 데이터 스크립트
실행: uv run python scripts/seed_items.py

KAMIS 품목 코드는 API 키 수령 후 실제 코드로 교체 필요.
현재 코드는 KAMIS 문서 기준 잠정값.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import SessionLocal
from app.models.item import Item

ITEMS = [
    # 곡물
    {"code": "111", "name": "쌀", "category": "곡물", "unit": "20kg"},
    {"code": "121", "name": "콩", "category": "곡물", "unit": "1kg"},
    # 채소
    {"code": "211", "name": "배추", "category": "채소", "unit": "1포기"},
    {"code": "212", "name": "무", "category": "채소", "unit": "1개"},
    {"code": "214", "name": "양파", "category": "채소", "unit": "1kg"},
    {"code": "215", "name": "대파", "category": "채소", "unit": "1kg"},
    {"code": "217", "name": "마늘", "category": "채소", "unit": "1kg"},
    {"code": "231", "name": "시금치", "category": "채소", "unit": "1kg"},
    {"code": "241", "name": "오이", "category": "채소", "unit": "10개"},
    {"code": "243", "name": "애호박", "category": "채소", "unit": "1개"},
    # 과일
    {"code": "411", "name": "사과", "category": "과일", "unit": "10개"},
    {"code": "412", "name": "배", "category": "과일", "unit": "10개"},
    {"code": "413", "name": "감귤", "category": "과일", "unit": "10개"},
    # 축산
    {"code": "511", "name": "소고기(한우 등심)", "category": "축산", "unit": "100g"},
    {"code": "512", "name": "돼지고기(삼겹살)", "category": "축산", "unit": "100g"},
    {"code": "513", "name": "닭고기", "category": "축산", "unit": "1kg"},
    {"code": "514", "name": "계란", "category": "축산", "unit": "30개"},
    # 수산
    {"code": "611", "name": "갈치", "category": "수산", "unit": "1마리"},
    {"code": "612", "name": "고등어", "category": "수산", "unit": "1마리"},
    {"code": "613", "name": "오징어", "category": "수산", "unit": "1마리"},
]


def seed():
    db = SessionLocal()
    try:
        existing_codes = {row.code for row in db.query(Item.code).all()}
        new_items = [Item(**i) for i in ITEMS if i["code"] not in existing_codes]

        if not new_items:
            print("이미 모든 품목이 등록되어 있습니다.")
            return

        db.add_all(new_items)
        db.commit()
        print(f"{len(new_items)}개 품목 등록 완료.")
        for item in new_items:
            print(f"  [{item.code}] {item.name} ({item.category}) — {item.unit}")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
