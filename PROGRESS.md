# 얼마니 — 진행도

> 이 파일은 **사람과 AI가 같이 보는 진행도 추적 문서**입니다.
> 다른 AI에게 컨텍스트 전달 시 `PROJECT.md`와 함께 읽도록 안내해주세요.

- **시작일**: 2026-04-27
- **현재 주차**: Week 1
- **마지막 업데이트**: 2026-04-28

---

## 🎯 현재 목표

**Week 1 — MVP 출시**: KAMIS 데이터 → DB 적재 → 웹 페이지에 가격/변동률 표시 → 배포

---

## 📊 전체 진행률

```
Week 1 (MVP)              ██████████  100%  ✅ 완료 (https://eolmani-production.up.railway.app)
Week 2 (그래프+레시피)    ░░░░░░░░░░   0%
Week 3 (알림)             ░░░░░░░░░░   0%
Week 4 (영수증 OCR)       ░░░░░░░░░░   0%
Week 5~6 (가격 캘린더)    ░░░░░░░░░░   0%   ← 1년치 데이터 누적 후
Week 5~6 (개인 CPI)       ░░░░░░░░░░   0%
Week 6~7 (슈링크플레이션) ░░░░░░░░░░   0%
Week 7+ (AI 예측)         ░░░░░░░░░░   0%
```

---

## 🔌 KAMIS API 명세 (정리)

> 다른 AI가 KAMIS 클라이언트를 작성할 때 이 섹션만 보면 됨.

### 사용 API: 일별 부류별 도/소매가격정보

- **공식 문서**: https://www.kamis.or.kr/customer/reference/openapi_list.do?action=detail&boardno=1
- **엔드포인트**: `http://www.kamis.or.kr/service/price/xml.do` (302 → https로 리다이렉트됨)
- **Action**: `dailyPriceByCategoryList`
- **메서드**: GET (쿼리 파라미터)
- **반환 형식**: JSON (`p_returntype=json`)

### 요청 파라미터

| 파라미터 | 타입 | 필수 | 설명 |
|---------|------|------|------|
| `p_cert_key` | string | ✅ | 인증 Key (KAMIS 발급) |
| `p_cert_id` | string | ✅ | 요청자 ID — **숫자 ID** (이메일 아님) |
| `p_returntype` | string | ✅ | `json` 사용 |
| `p_product_cls_code` | string | 선택 | `01`=소매(우리 기준), `02`=도매 |
| `p_item_category_code` | string | 선택 | 부류코드 (아래 표 참조) |
| `p_country_code` | string | 선택 | 지역코드 — 서울 `1101` 사용 |
| `p_regday` | string | 선택 | `YYYY-MM-DD` |
| `p_convert_kg_yn` | string | 선택 | `N` 사용 (원래 단위 유지) |

### 부류 코드 (`p_item_category_code`)

| 코드 | 부류 |
|-----|------|
| 100 | 식량작물 |
| 200 | 채소류 |
| 400 | 과일류 |
| 500 | 축산물 |
| 600 | 수산물 |

### 응답 필드 ⭐ (실제 확인된 필드명)

**한 번 호출로 시계열 7개가 다 옴 → 변동률 계산이 단순함.**

| 필드 | 의미 |
|------|------|
| `item_name` | 품목명 (예: 사과) |
| `item_code` | 품목코드 (**언더스코어** — `itemcode` 아님) |
| `kind_name` | 품종명 (예: 후지(10개)) |
| `kind_code` | 품종코드 (**언더스코어** — `kindcode` 아님) |
| `rank` | 등급 (상품 / 중품 / 大 / 1등급 등) |
| `unit` | 단위 (예: 10개, 1kg) |
| `dpr1` | **당일 가격** ⭐ (미수집 시 `"-"`) |
| `dpr2` | 1일 전 가격 ← dpr1 없을 때 폴백 |
| `dpr3` | 1주일 전 가격 |
| `dpr5` | 1개월 전 가격 |
| `dpr6` | 1년 전 가격 |
| `dpr7` | 평년 가격 |

**주의사항:**
- 가격 문자열에 콤마 포함 (`"3,500"`) → 파싱 시 `.replace(",", "")` 필요
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

### 호출 예시

```
http://www.kamis.or.kr/service/price/xml.do?
  action=dailyPriceByCategoryList
  &p_product_cls_code=01
  &p_item_category_code=200
  &p_country_code=1101
  &p_regday=2026-04-28
  &p_convert_kg_yn=N
  &p_cert_key={KEY}
  &p_cert_id={ID}
  &p_returntype=json
```

---

## 🗂 KAMIS 코드 — 확정된 품목 20종

> 실제 API 호출로 검증된 코드 (2026-04-28 기준)

| code (내부키) | 품목명 | category_code | item_code | kind_code | rank | 단위 |
|--------------|--------|--------------|-----------|-----------|------|------|
| rice | 쌀 | 100 | 111 | 01 | 상품 | 20kg |
| bean | 콩 | 100 | 141 | 01 | 상품 | 500g |
| cabbage | 배추 | 200 | 211 | 06 | 상품 | 1포기 |
| radish | 무 | 200 | 231 | 06 | 상품 | 1개 |
| onion | 양파 | 200 | 245 | 00 | 상품 | 1kg |
| green_onion | 대파 | 200 | 246 | 00 | 상품 | 1kg |
| garlic | 마늘 | 200 | 258 | 01 | 상품 | 1kg |
| spinach | 시금치 | 200 | 213 | 00 | 상품 | 100g |
| cucumber | 오이 | 200 | 223 | 02 | 상품 | 10개 |
| zucchini | 애호박 | 200 | 224 | 01 | 상품 | 1개 |
| apple | 사과 | 400 | 411 | 05 | 상품 | 10개 |
| pear | 배 | 400 | 412 | 01 | 상품 | 10개 |
| mandarin | 감귤 | 400 | 413 | 01 | 상품 | 10개 (비시즌 시 데이터 없음) |
| beef_sirloin | 소고기(한우 등심) | 500 | 4301 | 22 | 1등급 | 100g |
| pork_belly | 돼지고기(삼겹살) | 500 | 4304 | 27 | 삼겹살 | 100g |
| chicken | 닭고기 | 500 | 9901 | 99 | 육계(kg) | 1kg |
| egg_30 | 계란 | 500 | 9903 | 23 | 일반란 | 30구 |
| hairtail | 갈치 | 600 | 613 | 03 | 大 | 1마리 |
| mackerel | 고등어 | 600 | 611 | 05 | 大 | 1마리 |
| squid | 오징어 | 600 | 619 | 04 | 中 | 1마리 |

---

## ✅ Week 1 상세 진행

### Phase 0: 준비 ✅ 완료

- [x] KAMIS Open API 신청 → cert_key + cert_id 발급 수령
- [x] GitHub 레포 생성 (eolmani, private)
- [x] Python 3.12 + uv 환경 셋업
- [x] FastAPI 기본 프로젝트 (`app/main.py`)
- [x] `.gitignore` Python용 정비
- [x] 첫 커밋 + 푸시

### Phase 1: 환경 구성 ✅ 완료

- [x] PostgreSQL Docker 컨테이너 띄우기 (`docker-compose.yml`)
- [x] `.env` + `.env.example` 파일 작성
- [x] `app/config.py` (pydantic-settings)
- [x] `app/database.py` (SQLAlchemy 엔진/세션)
- [x] `/health/db` 엔드포인트로 DB 연결 확인

### Phase 2: 데이터 탐색 ✅ 완료

- [x] KAMIS API 명세 분석 (`dailyPriceByCategoryList` 액션 확정)
- [x] 응답 구조 파악 (dpr1~dpr7 시계열, 실제 필드명 `item_code`/`kind_code`)
- [x] 부류/품목/지역 코드 체계 파악 (`data/농축수산물 품목 및 등급 코드표.xlsx`)
- [x] cert_id 확인 (숫자 ID, 이메일 아님)
- [x] SSL 문제 진단 및 해결 (`SECLEVEL=0` 레거시 컨텍스트)
- [x] `scripts/test_kamis.py` 작성 및 전 카테고리 실제 호출 성공
- [x] 품목별 item_code / kind_code / rank 매핑 완료 (위 표 참조)
- [x] `kamis_client.py` 본 구현 완료

### Phase 3: 도메인 모델 ✅ 완료

- [x] Alembic 초기화 및 마이그레이션 2회 적용
- [x] `Item` 모델: `id`, `code`, `name`, `category`, `unit` + KAMIS 매핑 4개 컬럼
  - `kamis_category_code`, `kamis_item_code`, `kamis_kind_code`, `kamis_rank`
- [x] `PriceHistory` 모델: `item_id`, `price`, `recorded_date`, `source` + UniqueConstraint
- [x] 시드 데이터 20종 (실제 KAMIS 코드 기반으로 전면 재작성)

### Phase 4: 백엔드 API ✅ 완료

- [x] `GET /api/prices/today` 엔드포인트
- [x] Pydantic 응답 스키마 (`PriceItem`, `PricesTodayResponse`)
- [x] 품목별 최신 날짜 기준 조회 (축산물/농수산물 날짜 혼재 처리)
- [x] 7일/30일 변동률 계산 (DB 조회 기반)
- [x] Swagger UI (`/docs`) 확인

### Phase 5: 데이터 수집 ✅ 완료

- [x] `kamis_client.py` 본 구현
  - `fetch_category()`: 부류별 소매가 조회
  - `find_item_row()`: item_code + kind_code + rank 3중 매핑
  - `extract_price_and_date()`: dpr1 없으면 dpr2(어제)로 폴백
  - SSL: `PROTOCOL_TLS_CLIENT` + `SECLEVEL=0` 커스텀 컨텍스트
- [x] `collect_prices()` 완성
  - 카테고리 5회 호출로 전 품목 커버 (API 호출 최소화)
  - PostgreSQL upsert (`ON CONFLICT DO UPDATE`)
- [x] APScheduler `AsyncIOScheduler` 매일 06:00 Asia/Seoul
- [x] FastAPI `lifespan`에 스케줄러 시작/종료 연결
- [x] **수동 실행 결과: 19/20건 저장 성공** (감귤 비시즌 제외)
- [ ] 초기 데이터 백필 (지난 7~30일) — 배포 후 진행

### Phase 6: 프론트 ✅ 완료

- [x] `app/templates/base.html` — Tailwind CDN, Chart.js CDN, sticky 헤더
- [x] `app/templates/index.html`
  - 카테고리별 섹션 + 이모지
  - 품목 카드: 이름, 단위, 가격, ▲▼ 변동률 배지
  - 데이터 없을 때 안내 화면
  - 모바일 반응형 (`grid sm:grid-cols-2`)
- [x] Footer (KAMIS 출처 표시)
- [ ] Chart.js 7일 변동 그래프 (데이터 7일 쌓이면 추가)

### Phase 7: 배포 ✅ 완료

- [x] `Dockerfile` 작성 (빌드 검증 완료)
- [x] Railway 가입 / GitHub 연동
- [x] 환경변수 등록 (KAMIS 키, DB URL)
- [x] 배포 후 동작 확인 — Uvicorn 정상 기동 확인
- [x] Railway 도메인 발급: https://eolmani-production.up.railway.app
- [ ] GitHub README에 라이브 URL 추가
- [ ] **레포 Public 전환**

---

## 📋 다음 액션 (Top 3)

1. **Chart.js 그래프** — 7일치 데이터 쌓이면 품목별 가격 변동 그래프 추가 (Week 2)
2. **가격 캘린더 + 제철 정보** — 1년치 데이터 누적 후 월별 평균 그래프, 최저가 시즌 안내 (Week 5~6)
3. **레시피 기반 장보기** — "김치찌개 4인분" 입력 → 재료비 자동 계산 (Week 2)

---

## 📚 결정 로그

| 날짜 | 결정 | 이유 |
|------|------|------|
| 2026-04-27 | 프로젝트명 "얼마니" 확정 | 가격을 묻는 본질적 질문, 모든 기능을 하나로 묶는 컨셉 |
| 2026-04-27 | Java/Spring Boot → Python/FastAPI 전환 | 사용자 주력 언어가 Python, 데이터/AI 기능에 더 적합 |
| 2026-04-27 | 비상업 무료 서비스로 운영 | KAMIS 등 공공 데이터 라이선스 부담 회피, 신뢰 기반 |
| 2026-04-27 | GitHub 레포 처음엔 Private | 시크릿 실수 방어, MVP 완성 후 Public 전환 예정 |
| 2026-04-27 | 패키지 관리는 uv 채택 | 빠르고 표준화 추세, pip/poetry 대비 우수 |
| 2026-04-27 | Flask 대신 FastAPI 채택 | 자동 API 문서, Pydantic 타입 안전, async, 취업 가치 |
| 2026-04-27 | psycopg2 대신 psycopg3 (`psycopg[binary]`) | 신버전, 성능/기능 우수 |
| 2026-04-28 | `dailyPriceByCategoryList` 액션 채택 | 한 번 호출로 7개 시점 시계열 수신, API 효율 최적 |
| 2026-04-28 | 소매가 (`p_product_cls_code=01`) 우선 | 소비자 체감 물가가 목표 |
| 2026-04-28 | 서울(`1101`) 기준 | 데이터 가장 풍부, 도·소매 모두 지원 |
| 2026-04-28 | dpr1 → dpr2 폴백 | 당일 미수집 시 유효 가격 항상 표시 |
| 2026-04-28 | PostgreSQL upsert (ON CONFLICT) | 중복 수집 방어, 재실행 안전 |
| 2026-04-28 | 품목별 최신 날짜 조회 | 축산물(당일)/농수산물(전일) 날짜 혼재 문제 해결 |
| 2026-04-28 | SSL SECLEVEL=0 우회 | KAMIS 서버 구형 TLS로 인한 핸드셰이크 실패 해결 |

---

## ⚠️ 알려진 이슈

| 항목 | 상태 | 메모 |
|------|------|------|
| 감귤 데이터 없음 | 🟡 비시즌 | 4~9월 KAMIS 미수집. 품목 등록됨, 시즌 복귀 시 자동 수집 |
| 변동률 null | 🟡 데이터 누적 대기 | 7일/30일치 쌓이면 자동 표시 (약 1주일 후) |
| Chart.js 그래프 없음 | 🟡 데이터 대기 | 7일치 수집 후 구현 예정 |

---

## 🤝 AI 협업 안내

이 프로젝트를 다른 AI와 같이 작업할 때:

1. **`PROJECT.md`** — 프로젝트 전체 그림
2. **`PROGRESS.md`** (이 파일) — 현재 진행도 + KAMIS API 명세 + 품목 코드 표
3. **`REPORT.md`** — 전체 개발 진행 보고서 (상세 이력)
4. **`data/농축수산물 품목 및 등급 코드표.xlsx`** — KAMIS 전체 코드 참조용

### 컨텍스트 프롬프트 템플릿

```
나는 "얼마니"라는 식료품 가격 추적 서비스를 만들고 있어.
PROJECT.md는 전체 기획서, PROGRESS.md는 현재 진행도 + KAMIS API 명세야.

현재 상태:
- Phase 0~6 완료 (KAMIS 실데이터 19종 수집 중, 매일 06:00 자동 수집)
- Phase 7 (Railway 배포) 진행 예정

기술 스택: Python 3.12, FastAPI, PostgreSQL, SQLAlchemy 2.0, uv, APScheduler, Jinja2
```

---

## 📝 변경 로그

### 2026-04-28
- Phase 2 완료: API 키 수령, SSL 해결, 실제 호출 성공, 코드 매핑 완료
- Phase 3 업데이트: Item 모델에 KAMIS 매핑 컬럼 4개 추가, 시드 데이터 전면 재작성
- Phase 5 완료: kamis_client.py 본 구현, collect_prices() 완성, 19건 수집 성공
- KAMIS 명세 섹션: 실제 확인된 필드명(`item_code`, `kind_code`)으로 정정
- 품목 코드 표: 실제 검증된 20종 코드 전면 교체
- 결정 로그 7개 추가 (SSL 우회, 폴백 전략, upsert 등)
- REPORT.md 생성 (전체 개발 보고서)
- **Phase 7 완료**: Railway 배포 성공, 도메인 발급 (eolmani-production.up.railway.app)
- Railway 에러 2건 수정: psycopg2 드라이버 → psycopg3 URL 변환, app/static 빈 디렉토리 .gitkeep 추가
- 30일치 데이터 백필 완료 (scripts/backfill.py, 399건)
- **오늘의 특가 TOP5** 기능 추가 (7일 대비 하락폭 큰 순)
- 레포 Public 전환 완료
- 로드맵에 가격 캘린더 + 제철 정보 추가 (Week 5~6)
- 진행률 100% (Week 1 MVP 완성)

### 2026-04-27
- 프로젝트 시작, 기획서 v1.0(Java) → v1.1(Python) 전환
- Phase 0 완료 (기본 프로젝트 셋업)
- Phase 1 완료 (PostgreSQL Docker, config.py, database.py)
