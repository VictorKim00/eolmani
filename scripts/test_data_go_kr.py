"""
data.go.kr API 연결 테스트.
사용법: DATA_GO_KR_KEY=<인증키> python scripts/test_data_go_kr.py
"""

import asyncio
import os
import sys

sys.path.insert(0, ".")
os.environ.setdefault("DATABASE_URL", "postgresql://localhost/test")

KEY = os.environ.get("DATA_GO_KR_KEY", "")
if not KEY:
    print("ERROR: DATA_GO_KR_KEY 환경변수를 설정하세요.")
    print("  export DATA_GO_KR_KEY=<일반인증키>")
    sys.exit(1)

os.environ["DATA_GO_KR_KEY"] = KEY

import httpx

RECENT_URL = "https://apis.data.go.kr/B552845/recent/price"
PER_DAY_URL = "https://apis.data.go.kr/B552845/perDay/price"


async def test():
    async with httpx.AsyncClient(timeout=20.0) as client:
        # 1) 최근일자 API — 쌀(ctgry=100, item=111, vrty=01)
        print("=== 최근일자 API 테스트 (쌀) ===")
        resp = await client.get(RECENT_URL, params={
            "serviceKey": KEY,
            "returnType": "json",
            "pageNo": "1",
            "numOfRows": "10",
            "cond[se_cd::EQ]": "01",
            "cond[ctgry_cd::EQ]": "100",
            "cond[item_cd::EQ]": "111",
            "cond[vrty_cd::EQ]": "01",
        })
        print(f"  HTTP {resp.status_code}")
        data = resp.json()
        items = data.get("response", {}).get("body", {}).get("items", {})
        item_list = items.get("item", []) if items else []
        if isinstance(item_list, dict):
            item_list = [item_list]
        for row in item_list[:3]:
            print(f"  날짜={row.get('exmn_ymd')} 등급={row.get('grd_nm')} 가격={row.get('exmn_dd_prc')} 1주전={row.get('ww1_bfr_prc')} 1개월전={row.get('mm1_bfr_prc')}")

        # 2) 기간별 API — 배추(ctgry=200, item=211, vrty=06), 오늘 날짜
        from datetime import date
        today = date.today().strftime("%Y%m%d")
        print(f"\n=== 기간별 API 테스트 (배추, {today}) ===")
        resp2 = await client.get(PER_DAY_URL, params={
            "serviceKey": KEY,
            "returnType": "json",
            "pageNo": "1",
            "numOfRows": "50",
            "cond[exmn_ymd::GTE]": today,
            "cond[exmn_ymd::LTE]": today,
            "cond[se_cd::EQ]": "01",
            "cond[ctgry_cd::EQ]": "200",
            "cond[item_cd::EQ]": "211",
            "cond[vrty_cd::EQ]": "06",
        })
        print(f"  HTTP {resp2.status_code}")
        data2 = resp2.json()
        items2 = data2.get("response", {}).get("body", {}).get("items", {})
        item_list2 = items2.get("item", []) if items2 else []
        if isinstance(item_list2, dict):
            item_list2 = [item_list2]
        print(f"  총 {len(item_list2)}건")
        for row in item_list2[:5]:
            print(f"  날짜={row.get('exmn_ymd')} 지역코드={row.get('sgg_cd')} 지역={row.get('sgg_nm')} 등급={row.get('grd_nm')} 가격={row.get('exmn_dd_prc')}")

asyncio.run(test())
