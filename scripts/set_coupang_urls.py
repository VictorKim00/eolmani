"""
쿠팡 파트너스 수동 링크 등록 스크립트

사용법:
  uv run python scripts/set_coupang_urls.py

파트너스(partners.coupang.com) → 링크생성 → 상품탐색 → 링크복사 후
아래 COUPANG_URLS 딕셔너리에 item code: URL 형태로 추가하면 됩니다.

[그룹 변형 안내]
계절 변형(cabbage_spring, radish_spring)이나 품종 변형(cucumber_spiny 등)은
같은 상품 카테고리이므로 동일 파트너스 URL을 재사용해도 됩니다.
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

    # ── 곡물 ─────────────────────────────────────────────────────────
    "rice":             "https://link.coupang.com/a/eCP0Ue",
    "rice_10kg":        "https://link.coupang.com/a/eCP1K0",
    "potato":           "https://link.coupang.com/a/eCP23j",
    "sweet_potato":     "https://link.coupang.com/a/eCP4iz",
    # "glutinous_rice": "https://link.coupang.com/a/XXXXXX",  # 찹쌀
    # "bean":           "https://link.coupang.com/a/XXXXXX",  # 콩

    # ── 버섯 ─────────────────────────────────────────────────────────
    # "oyster_mushroom": "https://link.coupang.com/a/XXXXXX",  # 느타리버섯
    # "enoki_mushroom":  "https://link.coupang.com/a/XXXXXX",  # 팽이버섯
    # "king_mushroom":   "https://link.coupang.com/a/XXXXXX",  # 새송이버섯

    # ── 채소 ─────────────────────────────────────────────────────────
    "cabbage":          "https://link.coupang.com/a/eCP6id",
    "cabbage_spring":   "https://link.coupang.com/a/eCP6id",   # 봄배추 — 동일 URL 재사용
    "radish":           "https://link.coupang.com/a/eCP71q",
    "radish_spring":    "https://link.coupang.com/a/eCP71q",   # 봄무 — 동일 URL 재사용
    "onion":            "https://link.coupang.com/a/eCPYK0",
    "green_onion":      "https://link.coupang.com/a/eCQb4z",
    "garlic":           "https://link.coupang.com/a/eCQd9b",
    "spinach":          "https://link.coupang.com/a/eCQfzC",
    "tomato":           "https://link.coupang.com/a/eCPXbj",
    "carrot":           "https://link.coupang.com/a/eCPU4g",
    # "cucumber":         "https://link.coupang.com/a/XXXXXX",  # 오이(다다기)
    # "cucumber_spiny":   "https://link.coupang.com/a/XXXXXX",  # 오이(가시) — cucumber와 동일 URL 가능
    # "cucumber_green":   "https://link.coupang.com/a/XXXXXX",  # 오이(취청) — cucumber와 동일 URL 가능
    # "zucchini":         "https://link.coupang.com/a/XXXXXX",  # 호박(애호박)
    # "zucchini_green":   "https://link.coupang.com/a/XXXXXX",  # 호박(쥬키니) — zucchini와 동일 URL 가능
    # "lettuce":          "https://link.coupang.com/a/XXXXXX",  # 상추(청)
    # "lettuce_red":      "https://link.coupang.com/a/XXXXXX",  # 상추(적) — lettuce와 동일 URL 가능
    # "chili":            "https://link.coupang.com/a/XXXXXX",  # 청양고추
    # "perilla":          "https://link.coupang.com/a/XXXXXX",  # 깻잎
    # "cabbage_head":     "https://link.coupang.com/a/XXXXXX",  # 양배추
    # "yeolgal":          "https://link.coupang.com/a/XXXXXX",  # 얼갈이배추
    # "young_radish":     "https://link.coupang.com/a/XXXXXX",  # 열무
    # "green_pepper":     "https://link.coupang.com/a/XXXXXX",  # 풋고추
    # "red_pepper":       "https://link.coupang.com/a/XXXXXX",  # 붉은고추
    # "paprika":          "https://link.coupang.com/a/XXXXXX",  # 파프리카
    # "mini_cabbage":     "https://link.coupang.com/a/XXXXXX",  # 알배기배추
    # "broccoli":         "https://link.coupang.com/a/XXXXXX",  # 브로콜리
    # "cherry_tomato":    "https://link.coupang.com/a/XXXXXX",  # 방울토마토

    # ── 과일 ─────────────────────────────────────────────────────────
    "apple":            "https://link.coupang.com/a/eCPCtu",
    "pear":             "https://link.coupang.com/a/eCPF7i",
    "strawberry":       "https://link.coupang.com/a/eCPHKY",
    "banana":           "https://link.coupang.com/a/eCPJuW",
    "watermelon":       "https://link.coupang.com/a/eCPLCN",
    # "mandarin":         "https://link.coupang.com/a/XXXXXX",  # 감귤 (비시즌 4~9월)
    # "korean_melon":     "https://link.coupang.com/a/XXXXXX",  # 참외
    # "melon":            "https://link.coupang.com/a/XXXXXX",  # 멜론
    # "peach":            "https://link.coupang.com/a/XXXXXX",  # 복숭아 (시즌 7~9월)
    # "grape_campbell":   "https://link.coupang.com/a/XXXXXX",  # 포도(캠벨) (시즌 8~9월)
    # "grape_shine":      "https://link.coupang.com/a/XXXXXX",  # 포도(샤인머스켓) (시즌 8~10월)

    # ── 축산 ─────────────────────────────────────────────────────────
    "pork_belly":       "https://link.coupang.com/a/eCPqAo",
    "chicken":          "https://link.coupang.com/a/eCPmmq",
    "egg_30":           "https://link.coupang.com/a/eCPjPv",
    # "pork_neck":        "https://link.coupang.com/a/XXXXXX",  # 돼지 목심
    # "pork_foreleg":     "https://link.coupang.com/a/XXXXXX",  # 돼지 앞다리
    # "beef_sirloin":     "https://link.coupang.com/a/XXXXXX",  # 한우 등심
    # "beef_tenderloin":  "https://link.coupang.com/a/XXXXXX",  # 한우 안심
    # "beef_brisket":     "https://link.coupang.com/a/XXXXXX",  # 한우 양지
    # "beef_ribs":        "https://link.coupang.com/a/XXXXXX",  # 한우 갈비

    # ── 수산 ─────────────────────────────────────────────────────────
    "mackerel":         "https://link.coupang.com/a/eCPvrM",
    "hairtail":         "https://link.coupang.com/a/eCPwVI",
    "laver":            "https://link.coupang.com/a/eCPAw0",
    # "squid":            "https://link.coupang.com/a/XXXXXX",  # 오징어
    # "croaker":          "https://link.coupang.com/a/XXXXXX",  # 조기
    # "spanish_mackerel": "https://link.coupang.com/a/XXXXXX",  # 삼치
    # "pollack":          "https://link.coupang.com/a/XXXXXX",  # 명태
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
