# 얼마니 (Eolmani) — 개발 진행 보고서

> 작성일: 2026-04-28  
> 작성자: 개발자  
> 상태: Week 1 MVP 완료 — 라이브 운영 중 (https://eolmani-production.up.railway.app)

---

## 1. 프로젝트 개요

| 항목 | 내용 |
|------|------|
| **서비스명** | 얼마니 (Eolmani) |
| **한 줄 정의** | 공공 데이터 기반 농수산물·축산물 가격 추적 & 개인화 물가 웹 서비스 |
| **데이터 출처** | KAMIS (농산물유통정보) Open API |
| **운영 방침** | 비상업 무료 서비스 (광고 없음, 공익 목적) |
| **시작일** | 2026-04-27 |
| **레포지토리** | github.com/eolmani (public) |

---

## 2. 개발 기간 및 진행률

```
Week 1 (MVP)              ██████████  100%  ✅ 완료
Week 2 (그래프)           ░░░░░░░░░░   0%
Week 3 (알림)             ░░░░░░░░░░   0%
Week 4 (영수증 OCR)       ░░░░░░░░░░   0%
Week 5~6 (가격 캘린더)    ░░░░░░░░░░   0%   ← 1년치 데이터 누적 후
Week 5~6 (개인 CPI)       ░░░░░░░░░░   0%
Week 6~7 (슈링크플레이션) ░░░░░░░░░░   0%
Week 7+ (AI 예측)         ░░░░░░░░░░   0%
```

**총 개발 시간**: 약 1일 (2026-04-27 ~ 2026-04-28)

---

## 3. 기술 스택

| 영역 | 기술 | 버전 |
|------|------|------|
| 언어 | Python | 3.12 |
| 웹 프레임워크 | FastAPI | 최신 |
| DB | PostgreSQL | 16 |
| ORM | SQLAlchemy | 2.0 |
| 마이그레이션 | Alembic | 최신 |
| HTTP 클라이언트 | httpx | 최신 |
| 스케줄러 | APScheduler | 3.x |
| 템플릿 | Jinja2 | 최신 |
| 프론트 스타일 | Tailwind CSS (CDN) | 최신 |
| 차트 | Chart.js (CDN) | 4.4 |
| 패키지 관리 | uv | 최신 |
| 컨테이너 | Docker | - |
| 배포 예정 | Railway | - |

---

## 4. 완료된 작업 (Phase별)

### Phase 0 — 프로젝트 셋업 ✅
- GitHub 레포 생성 (private)
- Python 3.12 + uv 환경 구성
- FastAPI 기본 프로젝트 초기화
- `.gitignore` 설정 및 첫 커밋

### Phase 1 — 환경 구성 ✅
- PostgreSQL Docker 컨테이너 구성 (`docker-compose.yml`)
- `.env` / `.env.example` 파일 작성
- `app/config.py` — pydantic-settings 기반 환경변수 관리
- `app/database.py` — SQLAlchemy 엔진 및 세션 팩토리
- `/health/db` 엔드포인트로 DB 연결 확인

### Phase 2 — 데이터 탐색 ✅
- KAMIS API 명세 분석 완료 (`dailyPriceByCategoryList` 액션 확정)
- 응답 구조 파악: `dpr1`(당일) ~ `dpr7`(평년) 시계열 한 번에 수신
- 부류/품목/지역 코드 체계 확인 (`data/농축수산물 품목 및 등급 코드표.xlsx`)
- 실제 API 호출로 `item_code`, `kind_code`, `rank` 필드 확인
- SSL 문제 진단 및 해결 (레거시 cipher 허용 컨텍스트 적용)
- cert_id 확인 (숫자 ID, 이메일 아님)

### Phase 3 — 도메인 모델 ✅
- `Item` 모델: `id`, `code`, `name`, `category`, `unit` + KAMIS 매핑 필드 4개
- `PriceHistory` 모델: `item_id`, `price`, `recorded_date`, `source` + UniqueConstraint
- Alembic 초기화 및 2회 마이그레이션 적용
- 품목 마스터 시드 데이터 20종 (실제 KAMIS 코드 기반)

**확정된 품목 목록 (19개 수집 중, 감귤 비시즌 제외)**

| 카테고리 | 품목 | KAMIS item/kind | 단위 |
|---------|------|-----------------|------|
| 곡물 | 쌀 | 111/01 | 20kg |
| 곡물 | 콩 | 141/01 | 500g |
| 채소 | 배추 | 211/06 | 1포기 |
| 채소 | 무 | 231/06 | 1개 |
| 채소 | 양파 | 245/00 | 1kg |
| 채소 | 대파 | 246/00 | 1kg |
| 채소 | 마늘 | 258/01 | 1kg |
| 채소 | 시금치 | 213/00 | 100g |
| 채소 | 오이 | 223/02 | 10개 |
| 채소 | 애호박 | 224/01 | 1개 |
| 과일 | 사과 | 411/05 | 10개 |
| 과일 | 배 | 412/01 | 10개 |
| 과일 | 감귤 | 413/01 | 10개 (비시즌) |
| 축산 | 소고기(한우 등심) | 4301/22 | 100g |
| 축산 | 돼지고기(삼겹살) | 4304/27 | 100g |
| 축산 | 닭고기 | 9901/99 | 1kg |
| 축산 | 계란 | 9903/23 | 30구 |
| 수산 | 갈치 | 613/03 | 1마리 |
| 수산 | 고등어 | 611/05 | 1마리 |
| 수산 | 오징어 | 619/04 | 1마리 |

### Phase 4 — 백엔드 API ✅
- `GET /api/prices/today` 엔드포인트 구현
- Pydantic 응답 스키마 (`PriceItem`, `PricesTodayResponse`)
- 7일/30일 변동률 계산 로직 (DB 조회 기반)
- Swagger UI (`/docs`) 자동 생성 확인

### Phase 5 — 데이터 수집 ✅
- `kamis_client.py` 본 구현
  - SSL 문제: `ssl.PROTOCOL_TLS_CLIENT` + `SECLEVEL=0` 커스텀 컨텍스트
  - `fetch_category()`: 부류별 소매가 조회
  - `find_item_row()`: item_code + kind_code + rank 매핑
  - `extract_price_and_date()`: `dpr1` 없으면 `dpr2`(어제)로 폴백
- `price_collector.py` 완성
  - APScheduler `AsyncIOScheduler` — 매일 **06:00 Asia/Seoul** 실행
  - 카테고리 5회 호출로 전 품목 커버 (API 호출 최소화)
  - PostgreSQL upsert (`ON CONFLICT DO UPDATE`)
- FastAPI `lifespan` 이벤트로 스케줄러 자동 시작/종료
- **수동 실행 테스트 결과: 19건 저장 성공**

### Phase 6 — 프론트엔드 ✅
- `app/templates/base.html` — Tailwind CDN, Chart.js CDN, sticky 헤더, 푸터
- `app/templates/index.html`
  - 카테고리별 섹션 (곡물/채소/과일/축산/수산) + 이모지
  - 품목 카드: 이름, 단위, 가격, 변동률 배지 (▲빨강 / ▼파랑)
  - 데이터 없을 때 안내 화면
  - 모바일 반응형 (`grid sm:grid-cols-2`)
- `/static` 마운트 (`StaticFiles`)
- 인덱스 라우트: DB 조회 → 카테고리 그룹핑 → 템플릿 렌더링

---

## 5. 주요 기술 결정 사항

| 날짜 | 결정 | 이유 |
|------|------|------|
| 2026-04-27 | Java/Spring Boot → Python/FastAPI | Python 주력 언어, 데이터/AI 라이브러리 생태계 |
| 2026-04-27 | psycopg2 → psycopg3 (`psycopg[binary]`) | 신버전, 성능 우위 |
| 2026-04-27 | uv 패키지 관리 | pip/poetry 대비 속도·안정성 우수 |
| 2026-04-28 | `dailyPriceByCategoryList` 액션 채택 | 한 번 호출로 7개 시점 시계열 수신, API 효율 최적 |
| 2026-04-28 | 소매가 (`p_product_cls_code=01`) 우선 | 소비자 체감 물가가 서비스 목표 |
| 2026-04-28 | 서울 (`1101`) 기준 | 데이터 가장 풍부, 도/소매 모두 지원 |
| 2026-04-28 | dpr1 → dpr2 폴백 | 당일 데이터 미수집 시 유효 가격 표시 보장 |
| 2026-04-28 | PostgreSQL upsert (ON CONFLICT) | 중복 수집 방어, 재실행 안전 |
| 2026-04-28 | 품목별 최신 날짜 조회 | 축산물(당일)과 농수산물(전일) 날짜 혼재 문제 해결 |
| 2026-04-28 | SSL SECLEVEL=0 우회 | KAMIS 서버의 구형 TLS로 인한 핸드셰이크 실패 해결 |

---

## 6. 현재 시스템 구조

```
[KAMIS API] ──(매일 06:00)──▶ [APScheduler]
                                     │
                              fetch_category() × 5
                              (100/200/400/500/600)
                                     │
                              find_item_row() + extract_price_and_date()
                                     │
                              PostgreSQL: price_history (upsert)
                                     │
                    ┌────────────────┴────────────────┐
                    │                                 │
          GET /api/prices/today              GET /
          (JSON 응답)                  (Jinja2 HTML 렌더링)
```

### 디렉토리 구조 (현재)

```
eolmani/
├── app/
│   ├── api/prices.py           # GET /api/prices/today
│   ├── config.py               # 환경변수 (pydantic-settings)
│   ├── database.py             # SQLAlchemy 엔진/세션
│   ├── main.py                 # FastAPI 앱, 라우터, 스케줄러 lifespan
│   ├── models/
│   │   ├── item.py             # Item (품목 마스터 + KAMIS 코드)
│   │   └── price_history.py    # PriceHistory (일별 가격 기록)
│   ├── scheduler/
│   │   └── price_collector.py  # APScheduler + collect_prices()
│   ├── schemas/price.py        # Pydantic 응답 스키마
│   ├── services/
│   │   ├── kamis_client.py     # KAMIS API 호출 클라이언트
│   │   └── price_service.py    # 가격 조회 비즈니스 로직
│   ├── static/                 # CSS / JS 정적 파일
│   └── templates/
│       ├── base.html           # 공통 레이아웃
│       └── index.html          # 메인 가격 대시보드
├── data/
│   └── 농축수산물 품목 및 등급 코드표.xlsx
├── migrations/                 # Alembic 마이그레이션 파일
├── scripts/
│   ├── seed_items.py           # 품목 마스터 시드
│   └── test_kamis.py           # API 호출 테스트
├── docker-compose.yml
├── pyproject.toml
└── .env (gitignore)
```

---

## 7. 현재 동작 확인 결과

```
GET /api/prices/today (2026-04-28 기준)

date: 2026-04-28, count: 19

  곡물 | 쌀                  62,038원 (20kg)   | 2026-04-27
  곡물 | 콩                   4,996원 (500g)   | 2026-04-27
  과일 | 배                  33,257원 (10개)   | 2026-04-27
  과일 | 사과                 22,850원 (10개)   | 2026-04-27
  수산 | 갈치                 14,000원 (1마리)  | 2026-04-27
  수산 | 고등어                3,860원 (1마리)  | 2026-04-27
  수산 | 오징어                6,650원 (1마리)  | 2026-04-27
  채소 | 대파                  2,171원 (1kg)   | 2026-04-27
  채소 | 마늘                 11,629원 (1kg)   | 2026-04-27
  채소 | 무                   1,900원 (1개)   | 2026-04-27
  채소 | 배추                  4,024원 (1포기) | 2026-04-27
  채소 | 시금치                  700원 (100g)  | 2026-04-27
  채소 | 애호박                1,153원 (1개)   | 2026-04-27
  채소 | 양파                  1,909원 (1kg)   | 2026-04-27
  채소 | 오이                  6,929원 (10개)  | 2026-04-27
  축산 | 계란                  7,015원 (30구)  | 2026-04-28
  축산 | 닭고기                 6,503원 (1kg)   | 2026-04-28
  축산 | 돼지고기(삼겹살)          2,767원 (100g)  | 2026-04-28
  축산 | 소고기(한우 등심)        10,439원 (100g)  | 2026-04-28
```

---

## 8. 알려진 이슈 및 제한사항

| 이슈 | 설명 | 대응 |
|------|------|------|
| 감귤 데이터 없음 | 비시즌 (4~9월)으로 KAMIS 미수집 | 품목은 등록, 시즌 복귀 시 자동 수집 |
| 7일/30일 변동률 없음 | 데이터 수집 시작일로부터 7일/30일 경과 전 | 1주일 후 자동 표시 |
| SSL 우회 | KAMIS 서버 구형 TLS → `SECLEVEL=0` | 공공기관 서버 특성상 불가피, 내부 전용 설정 |
| 당일 농수산물 가격 | 06시 수집 기준이나 당일 KAMIS 업데이트 전이면 전일 가격 사용 | dpr2 폴백으로 항상 최신 유효가 표시 |

---

## 9. Week 1 이후 계획

### Week 2 — 그래프
- [ ] Chart.js 7일 가격 변동 그래프 (데이터 7일 쌓이면)

### Week 3 — 알림
- [ ] 회원가입, 관심 품목 즐겨찾기
- [ ] 목표 가격 도달 시 이메일 알림

### Week 4 — 영수증 OCR
- [ ] 영수증 사진 업로드 → OCR → 평균가 비교 카드

### Week 5~6 — 가격 캘린더 + 제철 정보
- [ ] 품목별 월별 평균 가격 그래프 (1년치 누적 후)
- [ ] "이 달에 사면 이득인 식재료" 제철 안내
- [ ] 개인화 CPI 대시보드

### Week 7+ — AI 예측
- [ ] Prophet / scikit-learn 기반 가격 예측 모델

---

## 10. 커밋 이력 요약

| 커밋 | 내용 |
|------|------|
| `b42b208` | Initial commit |
| `3a184b5` | FastAPI 프로젝트 초기화 (uv) |
| `ccbcc96` | PROJECT.md, PROGRESS.md 추가 |
| `0be0a4b` | PostgreSQL Docker + FastAPI 앱 구조 |
| `9c96df0` | Phase 3: 도메인 모델, Alembic, 시드 데이터 |
| `9ae89b9` | Phase 4: 가격 API 엔드포인트, Pydantic 스키마 |
| `c7dd166` | Phase 2+5 완성: KAMIS 실데이터 파이프라인 완전 작동 |
| `d89199f` | fix: psycopg2 → psycopg3 URL 변환 (Railway 배포 오류) |
| `414f30d` | fix: app/static .gitkeep 추가 (Railway 배포 오류) |
| `43f33ed` | docs: Phase 7 완료 — Railway 배포 성공 |
| `c7d4424` | feat: 오늘의 특가 TOP5 섹션 추가 |

---

*"오늘 사과 얼마니?" — 2026.04.27 시작*
