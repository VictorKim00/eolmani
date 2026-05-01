# 얼마니 — 진행도

> 이 파일은 **사람과 AI가 같이 보는 진행도 추적 문서**입니다.
> 다른 AI에게 컨텍스트 전달 시 `PROJECT.md`와 함께 읽도록 안내해주세요.

- **시작일**: 2026-04-27
- **현재 주차**: Phase 22 완료 + 서비스 오픈 (도메인 연결)
- **마지막 업데이트**: 2026-05-01 (eolmani.com 도메인 연결 + U3/U5 완료 + 품목 64종)
- **라이브 URL**: https://www.eolmani.com

---

## 🎯 현재 목표

**서비스 오픈 완료 · 품목 64종 · 다음: 홍보 + 공산품 섹션**:
eolmani.com 도메인 연결, 품목 64종(복숭아·포도·봄배추·봄무 추가), U3/U5 UX 개선 완료.
다음: 커뮤니티 홍보 + Week 4~5 공산품 섹션 착수.

---

## 📊 전체 진행률

```
Week 1 (MVP)               ██████████  100%  ✅ 라이브
Week 2 (신호등+그래프)      ██████████  100%  ✅ 완료
Week 3 (날씨+행동유도)      ██████████  100%  ✅ Phase 15(브리핑) 보류 확정
UX 현대화 + 품목 확장       ██████████  100%  ✅ 64종, 그룹 시스템, 탭 필터
Phase 22 지역별 가격         ██████████  100%  ✅ 24개 도시, 헤더 선택기, 백필 완료
도메인 + UX 마무리          ██████████  100%  ✅ eolmani.com, U3/U5 완료
Week 4~5 (공산품)           ░░░░░░░░░░    0%
보류 (가격 알림)            ░░░░░░░░░░    0%
보류 (영수증 OCR)           ░░░░░░░░░░    0%
보류 (개인 CPI/슈링크)      ░░░░░░░░░░    0%
보류 (AI 예측)              ░░░░░░░░░░    0%
```

---

## 🔌 KAMIS API 명세

### 사용 API: 일별 부류별 도/소매가격정보

- **공식 문서**: https://www.kamis.or.kr/customer/reference/openapi_list.do?action=detail&boardno=1
- **엔드포인트**: `http://www.kamis.or.kr/service/price/xml.do` (302 → https로 리다이렉트됨)
- **Action**: `dailyPriceByCategoryList`
- **반환 형식**: JSON (`p_returntype=json`)

### 요청 파라미터

| 파라미터 | 타입 | 필수 | 설명 |
|---------|------|------|------|
| `p_cert_key` | string | ✅ | 인증 Key (KAMIS 발급) |
| `p_cert_id` | string | ✅ | 요청자 ID — **숫자 ID** (이메일 아님) |
| `p_returntype` | string | ✅ | `json` 사용 |
| `p_product_cls_code` | string | 선택 | `01`=소매(우리 기준), `02`=도매 |
| `p_item_category_code` | string | 선택 | 부류코드 (아래 표) |
| `p_country_code` | string | 선택 | 지역코드 — 빈 문자열(`''`) = 전체(전국 평균), 아래 표 참조 |
| `p_regday` | string | 선택 | `YYYY-MM-DD` |
| `p_convert_kg_yn` | string | 선택 | `N` 사용 (원래 단위 유지) |

### p_country_code 지역 코드

**소매가격 선택 가능 지역** (24개):

| 코드 | 지역 | 코드 | 지역 | 코드 | 지역 |
|------|------|------|------|------|------|
| `1101` | 서울 | `2100` | 부산 | `2200` | 대구 |
| `2300` | 인천 | `2401` | 광주 | `2501` | 대전 |
| `2601` | 울산 | `2701` | 세종 | `3111` | 수원 |
| `3112` | 성남 | `3113` | 의정부 | `3138` | 고양 |
| `3145` | 용인 | `3211` | 춘천 | `3214` | 강릉 |
| `3311` | 청주 | `3411` | 천안 | `3511` | 전주 |
| `3613` | 순천 | `3711` | 포항 | `3714` | 안동 |
| `3814` | 창원 | `3818` | 김해 | `3911` | 제주 |

**도매가격 선택 가능 지역** (5개): 서울`1101`, 부산`2100`, 대구`2200`, 광주`2401`, 대전`2501`

> **현재 구현**: 전국 평균(`''`) + 6대 도시(서울·부산·대구·인천·광주·대전).
> 향후 확장 시 소매 지원 24개 지역 모두 추가 가능.

### 부류 코드

| 코드 | 부류 |
|-----|------|
| 100 | 식량작물 |
| 200 | 채소류 |
| 400 | 과일류 |
| 500 | 축산물 |
| 600 | 수산물 |

### 응답 필드 (실제 확인된 필드명)

**한 번 호출로 시계열 7개 수신 → 변동률 계산 단순.**

| 필드 | 의미 |
|------|------|
| `item_name` | 품목명 (예: 사과) |
| `item_code` | 품목코드 (**언더스코어** — `itemcode` 아님) |
| `kind_name` | 품종명 (예: 후지(10개)) |
| `kind_code` | 품종코드 (**언더스코어** — `kindcode` 아님) |
| `rank` | 등급 (상품 / 중품 / 大 / 1등급 등) |
| `unit` | 단위 (예: 10개, 1kg) |
| `dpr1` | **당일 가격** (미수집 시 `"-"`) |
| `dpr2` | 1일 전 가격 ← dpr1 없을 때 폴백 |
| `dpr3` | 1주일 전 가격 |
| `dpr5` | 1개월 전 가격 |
| `dpr6` | 1년 전 가격 |
| `dpr7` | 평년 가격 |

### 주의사항
- 가격 문자열에 콤마 포함 (`"3,500"`) → `.replace(",", "")` 필요
- 데이터 없는 날은 `"-"` 반환 → 방어 처리 필요
- 당일(dpr1)은 농수산물의 경우 저녁 전까지 `"-"`인 경우 많음 → dpr2 폴백 적용
- `https://` 엔드포인트는 구형 SSL → `ssl.SSLContext` + `SECLEVEL=0` 필요

### 에러 코드

| code | Message | 대응 |
|------|---------|------|
| 000 | Success | 정상 |
| 001 | no data | 해당 조건 데이터 없음 |
| 200 | Wrong Parameters | 파라미터 점검 |
| 900 | Unauthenticated request | cert_key / cert_id 잘못됨 |

---

## 🌦 기상청 API 명세 (Week 3 도입 예정)

### 사용 API: 중기예보 (10일치) + 단기예보 (3일치, 보강용)

- **공급처**: 공공데이터포털 (data.go.kr)
- **라이선스**: 공공누리 1유형 (출처표시) — 상업적 이용 가능
- **신청 방법**: 공공데이터포털 → 기상청_중기예보 조회서비스 → 활용신청

### 활용 데이터
- **중기육상예보**: 4~10일 후 일별 강수확률, 날씨 상태
- **중기기온예보**: 4~10일 후 일별 최저/최고 기온
- **단기예보** (보강): 1~3일 후 시간 단위 정밀 예보
- **지역**: 서울(서울지방기상청 코드) 1차, 추후 확장

### 호출 빈도
- 매일 06:30 (KAMIS 수집 직후) 1회 호출
- DB 캐시 (`weather_forecast` 테이블) → 사용자 요청 시 DB만 조회

---

## 🗂 KAMIS 코드 — 확정된 품목 59종 (2026-04-30 기준, 실제 검증)

> 2026-04-30에 20→42종으로 확장. 엑셀 코드표 검증 + 라이브 API 호출로 확인.

### 곡물 (category 100)

| code | 품목명 | group_code | item_code | kind_code | rank | 단위 |
|------|--------|-----------|-----------|-----------|------|------|
| rice | 쌀 20kg | rice | 111 | 01 | 상품 | 20kg |
| rice_10kg | 쌀 10kg | rice | 111 | 10 | 상품 | 10kg |
| glutinous_rice | 찹쌀 | — | 112 | 01 | 상품 | 1kg |
| sweet_potato | 고구마 | — | 151 | 00 | 상품 | 1kg |
| potato | 감자 | — | 152 | 04 | 상품 | 100g |
| bean | 콩 | — | 141 | 01 | 상품 | 500g |

### 채소 (category 200) + 버섯 (category 300 → 앱에서 채소 표시)

| code | 품목명 | group_code | item_code | kind_code | rank | 단위 |
|------|--------|-----------|-----------|-----------|------|------|
| oyster_mushroom | 느타리버섯 | — | 315(300) | 00 | 상품 | 100g |
| enoki_mushroom | 팽이버섯 | — | 316(300) | 00 | 상품 | 150g |
| king_mushroom | 새송이버섯 | — | 317(300) | 00 | 상품 | 100g |
| cabbage | 배추(월동) | cabbage | 211 | 06 | 상품 | 1포기 |
| cabbage_spring | 배추(봄) | cabbage | 211 | 01 | 상품 | 1포기 |
| radish | 무(월동) | radish | 231 | 06 | 상품 | 1개 |
| radish_spring | 무(봄) | radish | 231 | 01 | 상품 | 1개 |
| onion | 양파 | — | 245 | 00 | 상품 | 1kg |
| green_onion | 대파 | — | 246 | 00 | 상품 | 1kg |
| garlic | 마늘 | — | 258 | 01 | 상품 | 1kg |
| spinach | 시금치 | — | 213 | 00 | 상품 | 100g |
| cucumber | 오이(다다기) | cucumber | 223 | 02 | 상품 | 10개 |
| cucumber_spiny | 오이(가시) | cucumber | 223 | 01 | 상품 | 10개 |
| cucumber_green | 오이(취청) | cucumber | 223 | 03 | 상품 | 10개 |
| zucchini | 호박(애호박) | pumpkin | 224 | 01 | 상품 | 1개 |
| zucchini_green | 호박(쥬키니) | pumpkin | 224 | 02 | 상품 | 1개 |
| lettuce | 상추(청) | lettuce | 214 | 02 | 상품 | 100g |
| lettuce_red | 상추(적) | lettuce | 214 | 01 | 상품 | 100g |
| chili | 청양고추 | — | 242 | 03 | 상품 | 100g |
| carrot | 당근 | — | 232 | 01 | 상품 | 1kg |
| perilla | 깻잎 | — | 253 | 00 | 상품 | 100g |
| tomato | 토마토 | — | 225 | 00 | 상품 | 1kg |
| cabbage_head | 양배추 | — | 212 | 00 | 상품 | 1포기 |
| yeolgal | 얼갈이배추 | — | 215 | 00 | 상품 | 1kg |
| young_radish | 열무 | — | 233 | 00 | 상품 | 1kg |
| green_pepper | 풋고추 | — | 242 | 00 | 상품 | 100g |
| red_pepper | 붉은고추 | — | 243 | 00 | 상품 | 100g |
| paprika | 파프리카 | — | 256 | 00 | 상품 | 200g |
| mini_cabbage | 알배기배추 | — | 279 | 00 | 상품 | 1포기 |
| broccoli | 브로콜리 | — | 280 | 00 | 상품 | 1개 |
| cherry_tomato | 방울토마토 | — | 422(400) | 01 | 상품 | 1kg |

### 과일 (category 400 + KAMIS 200 일부)

| code | 품목명 | group_code | item_code | kind_code | rank | 단위 |
|------|--------|-----------|-----------|-----------|------|------|
| apple | 사과 | — | 411 | 05 | 상품 | 10개 |
| pear | 배 | — | 412 | 01 | 상품 | 10개 |
| mandarin | 감귤 | — | 415 | 01 | 상품 | 10개 (비시즌 4~9월) |
| strawberry | 딸기 | — | 226(200) | 00 | 상품 | 100g |
| watermelon | 수박 | — | 221(200) | 00 | 상품 | 1개 |
| korean_melon | 참외 | — | 222(200) | 00 | 상품 | 10개 |
| melon | 멜론 | — | 257(200) | 00 | 상품 | 1개 |
| banana | 바나나 | — | 418 | 02 | 상품 | 100g |
| peach | 복숭아 | — | 413 | 01 | 상품 | 10개 (시즌 7~9월) |
| grape_campbell | 포도(캠벨) | grape | 414 | 01 | 상품 | 1kg (시즌 8~9월) |
| grape_shine | 포도(샤인머스켓) | grape | 414 | 12 | 상품 | 2kg (시즌 8~10월) |

### 축산 (category 500)

| code | 품목명 | group_code | item_code | kind_code | rank | 단위 |
|------|--------|-----------|-----------|-----------|------|------|
| beef_sirloin | 한우 등심 | beef_korean | 4301 | 22 | 1등급 | 100g |
| beef_tenderloin | 한우 안심 | beef_korean | 4301 | 21 | 1등급 | 100g |
| beef_brisket | 한우 양지 | beef_korean | 4301 | 40 | 1등급 | 100g |
| beef_ribs | 한우 갈비 | beef_korean | 4301 | 50 | 1등급 | 100g |
| pork_belly | 돼지 삼겹살 | pork | 4304 | 27 | 삼겹살 | 100g |
| pork_neck | 돼지 목심 | pork | 4304 | 68 | 목심 | 100g |
| pork_foreleg | 돼지 앞다리 | pork | 4304 | 25 | 앞다리 | 100g |
| chicken | 닭고기 | — | 9901 | 99 | 육계(kg) | 1kg |
| egg_30 | 계란 | — | 9903 | 23 | 일반란 | 30구 |

### 수산 (category 600)

| code | 품목명 | group_code | item_code | kind_code | rank | 단위 |
|------|--------|-----------|-----------|-----------|------|------|
| hairtail | 갈치 | — | 613 | 03 | 大 | 1마리 |
| mackerel | 고등어 | — | 611 | 05 | 大 | 1마리 |
| squid | 오징어 | — | 619 | 04 | 中 | 1마리 |
| croaker | 조기 | — | 614 | 06 | 中 | 1마리 |
| spanish_mackerel | 삼치 | — | 616 | 01 | 大 | 1마리 |
| pollack | 명태 | — | 615 | 04 | 大 | 1마리 |
| laver | 김 | — | 641 | 00 | 중품 | 10장 |

---

## ✅ Week 1 (MVP) — 완료

### Phase 0~7 모두 완료

- [x] **Phase 0: 준비** — KAMIS API 신청, GitHub 레포, Python+uv 셋업
- [x] **Phase 1: 환경** — Docker PostgreSQL, .env, config, database
- [x] **Phase 2: 데이터 탐색** — KAMIS 명세 분석, SSL 해결, 코드 매핑 완료, kamis_client 구현
- [x] **Phase 3: 도메인 모델** — Item, PriceHistory, KAMIS 매핑 컬럼, 시드 20종
- [x] **Phase 4: 백엔드 API** — `/api/prices/today`, Pydantic 스키마, 변동률 계산
- [x] **Phase 5: 데이터 수집** — kamis_client 본 구현, collect_prices, APScheduler 06:00 KST
- [x] **Phase 6: 프론트** — Tailwind, 카테고리 섹션, 변동률 배지, 모바일 반응형
- [x] **Phase 7: 배포** — Dockerfile, Railway 배포, 도메인 발급, Public 전환
- [x] **추가**: 30일 백필 (399건), 오늘의 특가 TOP5

---

## ✅ Week 2 — 완료

### Phase 8: 30일 그래프 (Chart.js)

- [x] `app/api/prices.py`에 `/api/prices/{item_code}/history` 엔드포인트 추가
- [x] `app/templates/item_detail.html` 신규 페이지 (품목 클릭 시)
- [x] Chart.js 라인 차트 구현 (날짜 X축, 가격 Y축)
- [x] 평년 가격 점선 표시 (dpr7 기준) — avg_year_price 수집 후 자동 표시
- [ ] 메인 카드에 미니 스파크라인 추가 (50px 높이) — 선택사항, 추후

### Phase 9: 메인 카피 + 데이터 출처 라벨링

- [x] 헤더 슬로건 수정 — "오늘 사과 얼마니? 다음 주에는 얼마니?"
- [x] 각 품목 카드에 "전국 평균" 라벨 추가
- [x] Footer에 데이터 출처 명시 강화 ("KAMIS 도소매 조사 평균, 마트 가격과 다를 수 있음")
- [x] 요약 배너에 "KAMIS 도소매 조사 평균 · 트렌드 지표" 추가

### Phase 10: 신호등 + 통합 카드

- [x] `app/services/signal_service.py` 신규
  - 가중치 로직: 평년 50% + 1개월 30% + 1주일 20% (평년 없으면 정규화)
  - 종합 점수 ≤ -5% → 🟢 / -5%~+5% → 🟡 / ≥ +5% → 🔴
- [x] 메인 카드 신호등 이모지 표시
- [x] 품목 카드 클릭 → 상세 페이지 이동
- [x] Item.avg_year_price 컬럼 추가 + 마이그레이션 + 매일 수집
- [ ] 절약금액 표시 ("1박스 사면 약 X원 절약") — Week 3
- [ ] 모바일 카드 탭 펼침 — Week 3

### Phase 11: 시즌 대량구매 캘린더

- [x] 월별 인사이트 데이터 — `app/services/season_service.py` (1~12월 수동 큐레이션)
- [x] 메인 페이지에 "이번 달 추천 구매" 섹션 (요약 배너 바로 아래)
- [x] 11월 김장 시즌 강조 포함

---

## ✅ Week 3 — 완료

### Phase 12: 날씨 API 연동 ✅

> 기상청 대신 Open-Meteo 채택 (API 키 불필요, 무료, 10일 예보).

- [x] `app/services/weather_client.py` — Open-Meteo 클라이언트 (past_days 파라미터로 과거 포함)
- [x] 이번 주 일~토 7일 날씨 조회
- [x] 인메모리 1시간 캐시 (Railway 단일 인스턴스 기준 충분)
- [ ] WeatherForecast DB 모델 — 보류 (인메모리 캐시로 충분)
- [ ] APScheduler 날씨 수집 — 보류 (요청 시 실시간 조회가 더 단순)

### Phase 13: 날씨 → 가격 영향 룰 ✅

- [x] `app/services/weather_impact_service.py` 구현
- [x] 사전 정의 룰 5종 (한파/추위/폭염/강수/태풍·폭우)
- [x] `get_impacts()` — 날짜별 영향 품목 매칭
- [x] `get_week_summary()` — 주간 날씨 경보 요약 (최대 3개)
- [ ] DB WeatherImpactRule 모델 — 보류 (코드 내 룰 테이블로 충분)

### Phase 14: 주간 날씨 카드 ✅

- [x] 메인 페이지 인라인 구현 (일~토 가로 스크롤)
- [x] 날짜·날씨 아이콘·기온·강수확률·영향 이모지 표시
- [x] 과거 날짜 흐리게, 오늘 강조, 날씨 경보 주황 테두리
- [x] Open-Meteo 출처 표시

### Phase 15: 일일 브리핑 카드 ⏸️ 보류

- GPT API 비용 및 우선순위 검토 후 보류. 지역 지원 + 품목 확장 완료 후 재검토.

### Phase 16: 행동유도 메시지 ✅

- [x] `get_action()` — 신호등+변동률+월별통계 기반 buy_now/buy_soon/neutral/wait
- [x] 품목 상세 페이지 구매 타이밍 카드 (색상·아이콘 분기)
- [ ] 날씨·시즌 연계 심화 — 보류 (Phase 15 브리핑과 함께 구현 예정)

### 추가 완료 (Phase 미포함)

- [x] 시즌 캘린더 실제 월별 통계 연동 (`enrich_season_picks`, `get_month_vs_annual`)
- [x] 신호등 정확도 수정 — 메인↔상세 일치, `_price_near` 4일 윈도우
- [x] dpr3/dpr5 기준가 매일 저장 → 30일 변동률 데이터 확보
- [x] 데이터 희소 품목(쌀·콩) 365일 자동 확장
- [x] 품목 상세 페이지 월별 통계 카드 + 구매 행동 추천
- [x] 코드 전수 리뷰 (기본 + Opus 심층) → 17개 버그·이슈 수정 완료

---

## ✅ UX 현대화 + 품목 확장 (2026-04-30)

### Phase 20: UX 현대화 + 그룹/변형 시스템 ✅

> 품목이 20→42종으로 늘면서 단순 목록 방식이 한계. 그룹 카드로 변형 품목을 묶고 현대적 카드 디자인 적용.

- [x] **DB 마이그레이션**: `items` 테이블에 `group_code VARCHAR(30)`, `variant_label VARCHAR(50)`, `sort_order INTEGER` 추가
  - `migrations/versions/a3f82c9b1d4e_add_group_fields_to_items.py`
- [x] **Item 모델** 3개 필드 추가 (`app/models/item.py`)
- [x] **PriceItem 스키마** 3개 필드 추가 (`app/schemas/price.py`)
- [x] **`_build_category_cards()`** 함수 추가 (`app/main.py`)
  - group_code 기준으로 변형 품목을 ONE 그룹 카드로 묶음
  - 첫 등장 위치 유지, sort_order 기준 정렬
- [x] **그룹 카드 UI** — 변형 chip 목록 + 대표 변형 가격 표시
- [x] **품목 상세 탭** — 같은 group_code 형제들 탭 전환 (`/items/{code}`)
- [x] **품목 42종 확장** (`scripts/seed_items.py` 전면 재작성)
  - 그룹: rice(2), beef_korean(4), pork(3), cucumber(3), pumpkin(2), lettuce(2)
  - 신규 단독: 찹쌀, 고구마, 감자, 딸기, 느타리버섯, 팽이버섯, 새송이버섯
  - 버그 수정: 감귤 kamis_item_code `413`→`415` (413=복숭아, 415=감귤)
  - 버섯류: category_code=300 (특용작물) 으로 정정
- [x] **카드 리디자인** — 신호등 이모지 + signal_pill 배지 + per-unit 환산 가격
- [x] **UNIT_DIVISOR**, **GROUP_DISPLAY_NAMES** 상수 추가

### Phase 21: 탭 필터 + 실시간 검색 ✅

> 42종이 되면서 스크롤이 너무 길어짐. Sticky 필터로 탐색 체감 향상.

- [x] **Sticky 필터 바** — `top-14` 고정, 카테고리 탭 + 검색창
- [x] **카테고리 탭** — 전체 / 곡물 / 채소 / 과일 / 축산 / 수산, 카드 수 표시
- [x] **실시간 검색** — 타이핑 즉시 필터링, 탭 무관 전체 검색
  - 탭 선택 시 검색 초기화 / 검색 중 탭 시각적으로 전체 표시
- [x] **`data-cat`**, **`data-name`** 속성 → JS 필터링 훅
- [x] **"검색 결과 없어요"** fallback 메시지
- [x] `category_counts` main.py에서 계산 후 템플릿으로 전달
- [x] U6(품목 검색) 완료

---

## ✅ Phase 22 — 지역별 가격 지원 (완료)

> 전국 평균 + 24개 도시 지원. 헤더 드롭다운으로 지역 선택, localStorage 유지.

- [x] `price_history.region_code` 컬럼 + Unique constraint (`item_id, date, source, region`)
- [x] `price_collector.py` — 24개 지역 순차 수집, 지역 실패 시 skip
- [x] `price_service.py` — `region_code` 파라미터 추가, 전국 평균 폴백
- [x] `app/services/regions.py` — REGIONS(24개), REGION_GROUPS(optgroup), REGION_COORDS, REGION_LABEL, REGION_WEATHER_LABEL
- [x] 헤더 지역 선택기 (optgroup 그룹: 광역시/경기/강원/충청/전라/경상/제주)
- [x] localStorage 동기화 + URL `?region=` 파라미터 연동
- [x] 날씨도 지역 좌표 기반으로 변경 (`REGION_COORDS` 사용)
- [x] 전국 평균 선택 시 날씨 섹션 dimming (opacity-50)
- [x] `scripts/backfill.py` — `--new-regions`/`--all-regions` 플래그, 24개 지역 30일 백필 완료
- [x] 그래프 X축 `type: 'time'` 전환 (chartjs-adapter-date-fns), 기간 탭(1개월/3개월/전체)

---

## ⬜ Week 4~5 — 공산품 별도 섹션

### Phase 17: 참가격 API 연동

- [ ] 공공데이터포털에서 참가격 데이터 신청
- [ ] `app/services/chamga_client.py`
- [ ] `CommodityItem`, `CommodityPrice` 모델

### Phase 18: 공산품 페이지

- [ ] `/commodities` 라우트
- [ ] 마트별 비교 카드 (이마트/홈플러스/롯데마트)
- [ ] 최저가 마트 강조

### Phase 19: 통합 네비게이션

- [ ] 메인 페이지에 "농수산물 / 공산품" 탭
- [ ] 데이터 출처 명확히 분리 표시

---

## ⏸️ 보류 중인 기능

다음 기능들은 정체성/우선순위 재검토 결과 보류 (사용자 모이거나 데이터 누적 시 재검토):

| 기능 | 보류 사유 | 재검토 시점 |
|------|---------|-----------|
| **가격 알림 (이메일 → 카톡)** | 회원가입 동기 부족, MVP 안정화 우선 | 사용자 100명+ |
| **영수증 OCR** | 사용자 1,000명 모여야 데이터 의미 있음 | 사용자 1,000명+ |
| **개인화 CPI** | 영수증 데이터 의존 | OCR 도입 후 |
| **슈링크플레이션 감지** | 가공식품 이슈 (현재 농수산물) | 공산품 섹션 안정화 후 |
| **AI 가격 예측 (ML)** | 룰 기반(Week 3)이 부족해질 때 도입 | 1년 데이터 누적 후 |
| **쿠팡 파트너스** | 사용자 신뢰 안정화 후 | 사용자 1,000명+ |
| **레시피 기능** | 데이터 갭(가공식품 가격 부족), 본질에서 벗어남 | 제거 (재검토 안 함) |

### 카카오 알림 도입 시 방향 (참고)
- **1단계**: 이메일 (무료, 즉시)
- **2단계**: 카카오 "나에게 보내기" API — 무료, 사업자등록 불필요, 한국 사용자 친화
- **3단계**: 카카오톡 채널 친구톡 — 사용자 1,000명+ 시, 비용 발생 (15~23원/건)
- 알림톡(공식)은 사업자등록 + 딜러사 계약 필요 → 도입 부담 큼

---

## 📋 다음 액션 (Top 5)

1. **커뮤니티 홍보** — 에펨코리아·클리앙·82cook·맘카페 타겟별 포스팅. 5월 = 수박/참외/마늘 시즌 훅 활용
2. **Week 4~5: 공산품 섹션** — 참가격 API 연동, `/commodities` 라우트, 마트별 비교 카드
3. **U4: 차트 기간 탭** — 30일/90일/전체 탭 (이미 일부 구현됨, 세부 조정)
4. **U2: grey 신호등** — 데이터 없을 때 "보통" 오해 방지 (grey 처리)
5. **일일 브리핑 재검토** — 사용자 재방문 동기. 데이터 누적 확인 후 GPT-4o-mini 도입 여부 결정

---

## 📚 결정 로그

| 날짜 | 결정 | 이유 |
|------|------|------|
| 2026-04-27 | 프로젝트명 "얼마니" 확정 | 가격을 묻는 본질적 질문, 모든 기능을 하나로 묶는 컨셉 |
| 2026-04-27 | Java/Spring Boot → Python/FastAPI 전환 | 사용자 주력 언어가 Python, 데이터/AI 기능에 더 적합 |
| 2026-04-27 | 비상업 무료 서비스로 운영 | KAMIS 등 공공 데이터 라이선스 부담 회피, 신뢰 기반 |
| 2026-04-27 | GitHub 레포 처음엔 Private | 시크릿 실수 방어, MVP 완성 후 Public 전환 |
| 2026-04-27 | 패키지 관리는 uv 채택 | 빠르고 표준화 추세, pip/poetry 대비 우수 |
| 2026-04-27 | Flask 대신 FastAPI 채택 | 자동 API 문서, Pydantic 타입 안전, async, 취업 가치 |
| 2026-04-27 | psycopg2 대신 psycopg3 | 신버전, 성능/기능 우수 |
| 2026-04-28 | `dailyPriceByCategoryList` 액션 채택 | 한 번 호출로 7개 시점 시계열 수신, API 효율 최적 |
| 2026-04-28 | 소매가 (`p_product_cls_code=01`) 우선 | 소비자 체감 물가가 목표 |
| 2026-04-28 | 서울(`1101`) 기준 | 데이터 가장 풍부, 도·소매 모두 지원 |
| 2026-04-28 | dpr1 → dpr2 폴백 | 당일 미수집 시 유효 가격 항상 표시 |
| 2026-04-28 | PostgreSQL upsert (ON CONFLICT) | 중복 수집 방어, 재실행 안전 |
| 2026-04-28 | 품목별 최신 날짜 조회 | 축산물(당일)/농수산물(전일) 날짜 혼재 해결 |
| 2026-04-28 | SSL SECLEVEL=0 우회 | KAMIS 서버 구형 TLS 핸드셰이크 실패 해결 |
| 2026-04-28 | Public 전환 + 30일 백필 + 오늘의 특가 TOP5 | MVP 마무리, 즉시 가치 제공 |
| **2026-04-28** | **레시피 기능 제거** | 데이터 갭(가공식품 부족), 본질("타이밍")에서 벗어남, 친구 피드백 |
| **2026-04-28** | **정체성 확장: 가격 표시 → 구매 타이밍 가이드** | 친구 피드백 — "마트별 가격 비교가 아니라 언제 살지가 진짜 가치" |
| **2026-04-28** | **신호등 판단: 가중치 방식** | 평년 50% + 1개월 30% + 1주일 20%. 평년이 가장 중요한 기준선 |
| **2026-04-28** | **통합 카드 4요소** | 숫자(신뢰) + 신호등(직관) + 절약금액(임팩트) + 행동유도(다음 액션) |
| **2026-04-28** | **시즌 대량구매 캘린더 도입** | 친구 피드백 — 김장/장아찌/제철 한국 식문화 정확히 타격 |
| **2026-04-28** | **기상청 중기예보 API 채택** | 무료, 공공누리 1유형, 7일 커버 가능 |
| **2026-04-28** | **날씨 영향 매핑: 룰 테이블 우선** | Week 3엔 사전 정의 룰로 시작, ML(Week 7+)은 1년 데이터 후 |
| **2026-04-28** | **일일 브리핑: 룰 + GPT-4o-mini** | 데이터는 룰로, 문장만 GPT로. 비용 월 $0.05 |
| **2026-04-28** | **공산품 별도 섹션 (Week 4~5)** | 농수산물(타이밍)과 공산품(마트 비교)은 다른 영역, 통합 X |
| **2026-04-28** | **공산품 데이터: 참가격 우선** | 공식 공공데이터, 라이선스 깨끗, 마트별 가격 |
| **2026-04-28** | **가격 알림 후순위 보류** | MVP 안정화 + 차별화 기능(신호등/날씨) 우선 |
| **2026-04-28** | **카톡 알림 방향: 카카오 "나에게 보내기"** | 무료, 사업자등록 불필요, 한국 사용자 친화 |
| **2026-04-28** | **영수증/CPI/슈링크/AI예측 보류** | 사용자/데이터 누적 후 재검토. MVP 직후엔 차별화에 집중 |
| **2026-04-30** | **그룹/변형 시스템: 별도 테이블 아닌 컬럼 추가** | group_code/variant_label/sort_order 3개 컬럼으로 단순화. 라우팅 변경 없이 `/items/{code}` 유지 |
| **2026-04-30** | **품목 42종으로 확장** | KAMIS 엑셀 코드표 검증. 변형 그룹(오이·호박·상추·쌀·한우·돼지) + 신규 단독 7종(찹쌀·고구마·감자·딸기·버섯 3종) |
| **2026-04-30** | **지역별 가격 지원을 다음 큰 기능으로 결정** | 현재 서울 고정으로 지방 사용자 괴리. KAMIS `p_country_code`로 6대 도시 지원 가능. 품목 확장보다 체감 가치 큼 |
| **2026-04-30** | **Phase 15 일일 브리핑 보류 확정** | 지역 지원이 더 체감 임팩트 큼. 데이터 누적 후 재검토 |
| **2026-05-01** | **도메인: eolmani.com → www.eolmani.com** | 가비아 구입(.com 1년). 루트 CNAME 충돌 문제로 www 서브도메인으로 설정 |
| **2026-05-01** | **비시즌 품목 등록 (복숭아·포도)** | 코드만 등록, 시즌 도래 시 자동 수집. 시즌 캘린더와 연결해 비시즌엔 "현재 데이터 없음" 표시 |
| **2026-05-01** | **배추·무 그룹화** | 월동/봄 계절 변형을 cucumber 그룹처럼 탭 전환. 5월 이후 봄배추·봄무 수집 자동 시작 |

---

## ⚠️ 알려진 이슈

| 항목 | 상태 | 메모 |
|------|------|------|
| 감귤 데이터 없음 | 🟡 비시즌 | 4~9월 KAMIS 미수집. 품목 등록됨, 시즌 복귀 시 자동 수집. 상세 페이지 진입 시 "현재 데이터 없음" 표시됨 |
| N+1 쿼리 | 🟡 성능 | `get_today_prices`에서 품목 42개 × 2 = 84개 추가 쿼리. 현재 트래픽 무방, 규모 확장 시 최적화 필요 (P1) |
| KAMIS SSL CERT_NONE | 🟡 보안 | KAMIS 서버 구형 TLS로 인증서 검증 비활성화. KAMIS 자체 한계라 수정 불가 (O5) |
| 404 page 깨짐 | ✅ 수정 | HTTPException(404)으로 교체 (B1) |
| "30일 최고/최저" 라벨 | ✅ 수정 | 실제 데이터 기간(span_days)으로 동적 표시 (B2) |
| /admin/collect 인증 없음 | ✅ 수정 | X-Admin-Key 헤더 검증 추가. ADMIN_SECRET env 설정 시 적용 (B3) |
| 메인 페이지 데이터 정체성 모호 | ✅ 해결 | Week 2 카피 수정으로 해결 |
| Chart.js 그래프 없음 | ✅ 해결 | Week 2에 구현 완료 |

---

## 🔧 리팩토링 / 버그 / 개선 포인트

> 코드 전체 리뷰 결과 (2026-04-29). 우선순위 순 정렬.

---

### 🔴 버그 — 즉시 수정 권장

| # | 파일/위치 | 문제 | 상태 |
|---|---------|------|------|
| B1 | `app/main.py` | `item_detail` 404 시 index.html 컨텍스트 없이 렌더링 → 500 에러 | ✅ 수정완료 |
| B2 | `app/templates/item_detail.html` | 365일 데이터에도 "30일 최고/최저" 라벨 고정 | ✅ 수정완료 |
| B3 | `app/main.py` | `/admin/collect` 인증 없음 | ✅ 수정완료 |

---

### 🟠 성능 — 트래픽 증가 시 문제 될 수 있음

| # | 파일/위치 | 문제 | 상태 |
|---|---------|------|------|
| P1 | `price_service.py` | N+1 쿼리: 품목 20개 × `_price_near` 2회 = 40개 추가 쿼리 | 🟡 잔존 (트래픽 낮아 무방) |
| P2 | `price_stats_service.py` | `get_month_vs_annual` 내 4개 분리 쿼리 | 🟡 잔존 |
| P3 | `weather_client.py` | 날씨 캐시 모듈 글로벌 변수 (멀티워커 비공유) | 🟡 잔존 (단일 인스턴스 무방) |

---

### 🟡 코드 품질

| # | 파일/위치 | 문제 | 상태 |
|---|---------|------|------|
| Q1 | `main.py` + `weather_client.py` | `_KO_DAYS` / `WEEKDAY_KO` 중복 | ✅ 수정완료 |
| Q2 | `price_service.py` | `rate()` 루프 내 재정의 | ✅ 수정완료 (모듈 레벨 `_change_rate`로 통합) |
| Q3 | `main.py` | index async / item_detail sync 불일치 | ✅ 수정완료 |
| Q4 | `price_stats_service.py` | `enrich_season_picks` in-place + return 혼재 | 🟡 잔존 (기능 정상, 저우선순위) |
| Q5 | `price_stats_service.py` | `if not month_avg` 0.0 처리 오류 | ✅ 수정완료 |

---

### 🟢 소규모 UX 개선

| # | 위치 | 개선 내용 | 상태 |
|---|------|---------|------|
| U1 | `item_detail.html` | 비시즌 품목 current_price=0 → "현재 데이터 없음" 표시 | ✅ 수정완료 |
| U2 | `signal_service.py` | 데이터 없을 때 "보통" 오해 유발 → grey 신호등 고려 | 🟡 잔존 |
| U3 | `item_detail.html` | 🟢 신호 시 절약 금액 표시 | ✅ 완료 (2026-05-01) |
| U4 | `item_detail.html` | 차트 기간 탭 (30일/90일/1년) | 🟡 미구현 |
| U5 | 메인/상세 | 마지막 수집 시각 표시 | ✅ 완료 (2026-05-01) |
| U6 | 메인 | 품목 검색 | ✅ 완료 (Phase 21, 2026-04-30) |

---

### 📊 데이터 정확성 이슈

| # | 위치 | 문제 | 메모 |
|---|------|------|------|
| D1 | `item_detail.html` | `avg_year_price`(KAMIS dpr7 = 5년 평년) vs `month_stats.annual_avg`(당사 누적 평균) 두 값이 동시 표시 — 혼란 가능 | 데이터 1년+ 누적 후 dpr7 대신 자체 통계로 대체 고려 |
| D2 | `kamis_client.py:134–141` | dpr3/dpr5를 "today - 7일" / "today - 30일"로 고정 저장 — KAMIS 실제 기준일(주말·휴일 반영)과 정확히 불일치 가능 | `_price_near` 4일 윈도우로 실용적 커버 중. 현재 무방 |

---

## 🔬 Opus 심층 리뷰 추가 발견 이슈 (2026-04-29)

> 위 기본 리뷰에서 발견한 이슈를 **제외**하고 Claude Opus가 별도 코드 전수 검토한 결과.

---

### 🔴 Critical — 현재 동작 오류

| # | 파일:줄 | 문제 | 상태 |
|---|---------|------|------|
| O1 | `weather_client.py:83` | `[:days]` 슬라이스 — 주 후반일수록 미래 날씨 소실 | ✅ 수정완료 |
| O2 | `index.html:139` | `category_emoji[category]` 직접 접근 → KeyError 500 | ✅ 수정완료 |
| O3 | `signal_service.py:1–7` | 독스트링 75%/25% ≠ 실제 코드 60%/40% | ✅ 수정완료 |

---

### 🟠 High — 안정성·보안

| # | 파일:줄 | 문제 | 상태 |
|---|---------|------|------|
| O4 | `database.py:6` | `pool_pre_ping=True` 미설정 → 유휴 후 DB OperationalError | ✅ 수정완료 |
| O5 | `kamis_client.py:19–24` | `ssl.CERT_NONE` 인증서 검증 비활성화 | 🟡 잔존 (KAMIS 서버 한계) |
| O6 | `weather_impact_service.py:22–24` | lambda에 None 가드 없음 → `None <= -5` TypeError | ✅ 수정완료 |

---

### 🟡 Medium — 기능 결함·UX 오류

| # | 파일:줄 | 문제 | 상태 |
|---|---------|------|------|
| O7 | `backfill.py:98–100` | `main()` DB 세션 finally 없음 → 예외 시 연결 누수 | ✅ 수정완료 |
| O8 | `item_detail.html:113–125` | points=0이어도 canvas 렌더링 → 빈 흰 사각형 | ✅ 수정완료 |
| O9 | `item_detail.html:116–119` | 차트 제목 span_days > 60 분기 → 31~60일 구간 오표시 | ✅ 수정완료 |
| O10 | `price_stats_service.py:40–51` | 운영 초기 "연평균"이 실은 수집 기간 평균 | 🟡 잔존 (데이터 누적 후 자연 해소) |
| O11 | `main.py:99` 필터링 | 비시즌 pick `/items/None` URL 가능성 | 🟢 비이슈 (main.py 필터로 이미 방지됨) |

---

### 🟢 Low — 코드 품질·유지보수

| # | 파일:줄 | 문제 | 상태 |
|---|---------|------|------|
| O12 | `price_service.py:33–43` | PostgreSQL `DISTINCT ON` 전용 주석 없음 | ✅ 수정완료 |
| O13 | `seed_items.py:52–56` | SQLAlchemy 1.x `db.query()` 스타일 | 🟡 잔존 (동작 무방, 저우선순위) |
| O14 | `index.html:176–186` | `{% macro %}` 정의가 block 바깥에 위치 | ✅ 수정완료 |
| O15 | `base.html:7` | Tailwind CDN 버전 미고정 | 🟡 잔존 (Play CDN 특성상 버전 URL 없음) |
| O16 | `price_collector.py:115–116` | 앱 시작 시 즉시 수집 없음 | 🟡 잔존 (`/admin/collect`로 수동 커버) |
| O17 | `weather_impact_service.py:99–100` | 주간 요약 최대 2개 하드코딩 | ✅ 수정완료 (상수 `_MAX_WEEK_SUMMARIES=3`으로 추출·조정) |

---

## 🤝 AI 협업 안내

이 프로젝트를 다른 AI(Claude Code, Cursor, ChatGPT 등)와 같이 작업할 때:

1. **`PROJECT.md`** — 프로젝트 전체 그림 (v1.3 지역별 가격 지원 추가)
2. **`PROGRESS.md`** (이 파일) — 현재 진행도 + KAMIS API 명세 + 품목 코드 표 (42종)
3. **`data/농축수산물 품목 및 등급 코드표.xlsx`** — KAMIS 전체 코드 참조용

### 컨텍스트 프롬프트 템플릿

```
나는 "얼마니"라는 식료품 가격 추적 + 구매 타이밍 가이드 서비스를 만들고 있어.
PROJECT.md(v1.3)는 전체 기획서, PROGRESS.md는 진행도 + KAMIS API 명세야.

현재 상태 (2026-04-30):
- Week 1~3 모두 완료, 라이브 중 (https://eolmani-production.up.railway.app)
- 품목 42종, 그룹/변형 시스템(오이·호박·상추·쌀·한우·돼지 그룹), 탭 필터+검색 완료
- 가격 기준: 서울(1101) 소매가. 다음 큰 기능은 지역별 가격 지원 (Phase 22)
- 신호등: 평년 50% + 1개월 30% + 1주일 20% 가중치

기술 스택: Python 3.12, FastAPI, PostgreSQL, SQLAlchemy 2.0, uv, APScheduler, Jinja2, Chart.js, Tailwind CDN
KAMIS 수집: dailyPriceByCategoryList, p_country_code=1101(서울), 소매가(01), 매일 06:00 KST
```

### Claude Code용 다음 작업 프롬프트

```
PROJECT.md, PROGRESS.md 읽고 컨텍스트 잡아줘.

다음 작업: Phase 8 (30일 그래프 Chart.js)
1. /api/prices/{item_code}/history 엔드포인트 추가 (최근 30일)
2. app/templates/item_detail.html 신규 페이지
3. Chart.js 라인 차트 (날짜 X축, 가격 Y축, 평년 점선)
4. 메인 카드에서 품목 클릭 시 상세 페이지로 이동
5. 끝나면 PROGRESS.md Phase 8 체크박스 업데이트해줘
```

---

## 📝 변경 로그

### 2026-05-01 — 서비스 오픈 + 품목 59→64종 + UX 마무리

**도메인 연결**
- 가비아에서 eolmani.com 구입 (1년, .com)
- 가비아 DNS: CNAME `www` → `rgn8kjk6.up.railway.app.`, TXT `_railway-verify.www`
- Railway: `www.eolmani.com` 도메인 인증 완료 (초록 체크)
- 라이브 URL: https://www.eolmani.com

**품목 59→64종 확장**
- 복숭아(peach): 413/01/상품/10개 (비시즌 등록, 7~9월 자동 수집)
- 포도 캠벨(grape_campbell): 414/01/L과/1kg, group:grape
- 포도 샤인머스켓(grape_shine): 414/12/L과/2kg, group:grape
- 배추 그룹화: 배추(월동)(cabbage/sort:1) + 봄배추(cabbage_spring/sort:2)
- 무 그룹화: 무(월동)(radish/sort:1) + 봄무(radish_spring/sort:2)
- GROUP_DISPLAY_NAMES에 grape/cabbage/radish 추가

**UX 개선 완료**
- U3: 🟢 신호 시 "💰 X원 저렴" 초록 배지 (`item_detail.html`)
- U5: 데이터가 오늘이 아닐 때 헤더에 "어제 기준" / "M/D 기준" 표시 (`base.html`)
- season_service.py 시즌 캘린더 전면 업데이트 (수박·참외·복숭아·포도·봄배추 연결)

### 2026-04-30 (오후) — Phase 22 + 품목 42→59종

**Phase 22: 지역별 가격 지원**
- `price_history.region_code` 컬럼 + Unique constraint 변경
- `price_collector.py` 24개 지역 순차 수집 (전국 평균 + 23개 도시)
- `app/services/regions.py` — REGIONS/REGION_GROUPS/REGION_COORDS/REGION_LABEL/REGION_WEATHER_LABEL
- 헤더 지역 드롭다운 (optgroup: 광역시/경기/강원/충청/전라/경상/제주), localStorage 연동
- 날씨도 지역 좌표 기반 (`fetch_forecast(lat, lon)` 파라미터화)
- 전국 평균 시 날씨 섹션 dimming
- 그래프 X축 `type: 'time'` 전환 + 기간 탭(1개월/3개월/전체), Y축 동적 zoom
- 18개 신규 지역 30일 백필 완료

**품목 42→59종 확장**
- 채소 신규 10종: 양배추, 얼갈이배추, 열무, 풋고추, 붉은고추, 파프리카, 알배기배추, 브로콜리, 방울토마토
- 과일 신규 4종: 수박, 참외, 멜론, 바나나
- 수산 신규 4종: 조기, 삼치, 명태, 김
- Railway 시드 완료, 전체 24개 지역 30일 백필 진행 중

### 2026-04-30 (오전) — UX 현대화 + 품목 확장 + 탭 필터

**Phase 20: 그룹/변형 시스템**
- DB: `group_code`, `variant_label`, `sort_order` 컬럼 추가 (Alembic 마이그레이션)
- `_build_category_cards()` — group_code 기준 ONE 그룹 카드 + 변형 chip 목록
- 품목 상세 sibling 탭 — 같은 그룹 형제 품목 클릭 전환 (`item_detail.html`)
- 카드 리디자인: signal_pill 배지 + per-unit 환산 가격 (10개→1개당 등)
- 그룹 6종: rice(2), beef_korean(4), pork(3), cucumber(3), pumpkin(2), lettuce(2)

**품목 20→42종 확장** (`seed_items.py` 전면 재작성)
- 신규 단독: 찹쌀, 고구마, 감자, 딸기, 느타리버섯, 팽이버섯, 새송이버섯
- 버그 수정: 감귤 item_code `413`→`415` (413=복숭아, 415=감귤 확인)
- 버섯 category_code `300`으로 정정 (기존 200 오류)

**Phase 21: Sticky 탭 필터 + 실시간 검색**
- Sticky 필터 바 (top-14 고정) — 카테고리 탭 6개 + 검색창
- 실시간 검색: 타이핑 즉시 전체 카테고리 필터링, 탭 클릭 시 검색 초기화
- `data-cat`, `data-name` 속성 기반 순수 JS 필터링 (서버 왕복 없음)
- `category_counts` main.py에서 계산 후 전달

### 2026-04-29 — Week 3 완성 + 코드 안정화

**Week 3 핵심 기능 구현 완료**
- Phase 12: Open-Meteo API 날씨 연동 (`weather_client.py`, past_days 지원, 1시간 캐시)
- Phase 13: 날씨→가격 영향 룰 엔진 (`weather_impact_service.py`, 5종 룰)
- Phase 14: 주간 날씨 카드 (일~토 가로 스크롤, 기온·날씨·영향 이모지)
- Phase 16: 구매 행동 추천 (`get_action()`, buy_now/buy_soon/neutral/wait)
- 추가: 시즌 캘린더 실제 월별 통계 연동, 신호등 정확도 수정, 30일 변동률 데이터 확보

**코드 전수 리뷰 + 버그 수정 (17개)**
- 기본 리뷰: B1(404 처리), B2(라벨 고정), B3(인증 없음), Q1~Q3·Q5(품질)
- Opus 심층 리뷰: O1(날씨 슬라이스), O2(KeyError), O3(독스트링), O4(pool_pre_ping), O6(None 가드), O7(finally), O8·O9(차트), O12(주석), O14(매크로), O17(상수)

### 2026-04-28 (오후) — 정체성 확장 v1.2
- **친구 피드백 반영**: 정체성을 "가격 표시"에서 "**구매 타이밍 가이드**"로 확장
- 핵심 기능 재정리: **레시피 제거**, 신호등/시즌 캘린더/날씨 예측/일일 브리핑 추가
- 기능 보류 결정: 가격 알림(후순위), 영수증 OCR / 개인화 CPI / 슈링크플레이션 / AI 예측 / 쿠팡 파트너스 (보류)
- 공산품 별도 섹션 결정 (Week 4~5, 참가격 데이터)
- 카톡 알림 방향: 카카오 "나에게 보내기" API (무료, 사업자등록 불필요)
- 결정 로그 12개 추가, 알려진 이슈 업데이트

### 2026-04-28 (오전) — Week 1 MVP 완성
- Phase 2 완료: API 키 수령, SSL 해결, 실제 호출 성공, 코드 매핑 완료
- Phase 3 업데이트: Item 모델 KAMIS 매핑 컬럼 4개, 시드 데이터 재작성
- Phase 5 완료: kamis_client 본 구현, collect_prices 완성, 19건 수집 성공
- Phase 7 완료: Railway 배포 성공, 도메인 발급
- 30일치 데이터 백필 완료 (399건)
- "오늘의 특가 TOP5" 기능 추가
- 레포 Public 전환 완료
- KAMIS 명세 섹션 정정 (실제 필드명 `item_code`, `kind_code`)
- 품목 코드 표 검증된 20종으로 교체
- 결정 로그 7개 추가 (SSL 우회, 폴백, upsert 등)
- REPORT.md 생성

### 2026-04-27
- 프로젝트 시작, 기획서 v1.0(Java) → v1.1(Python) 전환
- Phase 0 완료 (기본 프로젝트 셋업)
- Phase 1 완료 (PostgreSQL Docker, config.py, database.py)
