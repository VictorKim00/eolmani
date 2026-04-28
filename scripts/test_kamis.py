"""
KAMIS API 연결 테스트 스크립트.
실행: uv run python scripts/test_kamis.py

응답 전체를 출력해서 실제 필드 구조를 확인한다.
"""

import asyncio
import json
import ssl
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import httpx
from app.config import settings

# KAMIS는 구형 SSL을 사용 → 레거시 cipher 허용 컨텍스트 필요
def _kamis_ssl_context() -> ssl.SSLContext:
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ctx.set_ciphers("DEFAULT:@SECLEVEL=0")
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx

CATEGORY_NAMES = {
    "100": "식량작물",
    "200": "채소류",
    "400": "과일류",
    "500": "축산물",
    "600": "수산물",
}


async def test_category(category_code: str, regday: str = "2026-04-28"):
    params = {
        "action": "dailyPriceByCategoryList",
        "p_cert_key": settings.kamis_cert_key,
        "p_cert_id": settings.kamis_cert_id,
        "p_returntype": "json",
        "p_product_cls_code": "01",        # 소매
        "p_item_category_code": category_code,
        "p_country_code": "1101",          # 서울
        "p_regday": regday,
        "p_convert_kg_yn": "N",
    }

    async with httpx.AsyncClient(timeout=15.0, follow_redirects=True, verify=_kamis_ssl_context()) as client:
        resp = await client.get(settings.kamis_base_url, params=params)
        resp.raise_for_status()
        data = resp.json()

    label = CATEGORY_NAMES.get(category_code, category_code)
    print(f"\n{'='*60}")
    print(f"[{category_code}] {label}")
    print(f"{'='*60}")

    # 에러 코드 확인
    result_code = data.get("condition", [{}])
    print(f"condition: {result_code}")

    items = data.get("data", {}).get("item", [])
    print(f"items 개수: {len(items)}")

    if items:
        print("\n--- 첫 번째 item 전체 필드 ---")
        print(json.dumps(items[0], ensure_ascii=False, indent=2))
        print("\n--- 전체 품목 요약 ---")
        for item in items:
            name = item.get("item_name", "?")
            kind = item.get("kind_name", "?")
            unit = item.get("unit", "?")
            dpr1 = item.get("dpr1", "-")
            dpr3 = item.get("dpr3", "-")
            dpr5 = item.get("dpr5", "-")
            icode = item.get("item_code", "?")
            kcode = item.get("kind_code", "?")
            rank = item.get("rank", "?")
            print(f"  [{icode}/{kcode}][{rank}] {name} {kind} ({unit}) | 오늘:{dpr1} / 7일전:{dpr3} / 1달전:{dpr5}")


async def main():
    print(f"cert_id: {settings.kamis_cert_id}")
    print(f"cert_key: {settings.kamis_cert_key[:8]}...")

    for code in ["100", "200", "400", "500", "600"]:
        await test_category(code)


if __name__ == "__main__":
    asyncio.run(main())
