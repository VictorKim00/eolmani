"""
쿠팡 파트너스 수동 링크 등록 스크립트

사용법:
  uv run python scripts/set_coupang_urls.py

파트너스(partners.coupang.com) → 링크생성 → 상품탐색 → 링크복사 후
아래 COUPANG_URLS 딕셔너리에 item code: URL 형태로 추가하면 됩니다.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models.item import Item

# ── 여기에 파트너스 링크 채워넣기 ──────────────────────────────────
# key: items.code 값 (seed_items.py 참고)
# value: 파트너스에서 생성한 추적 URL
COUPANG_URLS: dict[str, str] = {
    # 곡물
    # "rice":            "https://link.coupang.com/a/XXXXXX",
    # "rice_10kg":       "https://link.coupang.com/a/XXXXXX",
    # "potato":          "https://link.coupang.com/a/XXXXXX",
    # "sweet_potato":    "https://link.coupang.com/a/XXXXXX",

    # 채소
    # "cabbage":         "https://link.coupang.com/a/XXXXXX",
    # "radish":          "https://link.coupang.com/a/XXXXXX",
    # "onion":           "https://link.coupang.com/a/XXXXXX",
    # "green_onion":     "https://link.coupang.com/a/XXXXXX",
    # "garlic":          "https://link.coupang.com/a/XXXXXX",
    # "spinach":         "https://link.coupang.com/a/XXXXXX",
    # "tomato":          "https://link.coupang.com/a/XXXXXX",
    # "carrot":          "https://link.coupang.com/a/XXXXXX",

    # 과일
    # "apple":           "https://link.coupang.com/a/XXXXXX",
    # "pear":            "https://link.coupang.com/a/XXXXXX",
    # "strawberry":      "https://link.coupang.com/a/XXXXXX",
    # "banana":          "https://link.coupang.com/a/XXXXXX",
    # "watermelon":      "https://link.coupang.com/a/XXXXXX",

    # 축산
    # "pork_belly":      "https://link.coupang.com/a/XXXXXX",
    # "chicken":         "https://link.coupang.com/a/XXXXXX",
    # "egg_30":          "https://link.coupang.com/a/XXXXXX",

    # 수산
    # "mackerel":        "https://link.coupang.com/a/XXXXXX",
    # "hairtail":        "https://link.coupang.com/a/XXXXXX",
    # "laver":           "https://link.coupang.com/a/XXXXXX",
}
# ────────────────────────────────────────────────────────────────────


def main():
    db = SessionLocal()
    try:
        updated = 0
        for code, url in COUPANG_URLS.items():
            item = db.query(Item).filter(Item.code == code).first()
            if item is None:
                print(f"  ⚠️  코드 없음: {code}")
                continue
            item.coupang_url = url
            updated += 1
            print(f"  ✅ {item.name} ({code})")
        db.commit()
        print(f"\n총 {updated}개 업데이트 완료.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
