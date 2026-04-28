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
Week 1 (MVP)            ████████░░  80%   ← 진행 중 (Phase 7 배포 남음)
Week 2 (레시피)          ░░░░░░░░░░   0%
Week 3 (알림)           ░░░░░░░░░░   0%
Week 4 (영수증 OCR)     ░░░░░░░░░░   0%
Week 5 (개인 CPI)       ░░░░░░░░░░   0%
Week 6 (슈링크플레이션) ░░░░░░░░░░   0%
Week 7+ (AI 예측)       ░░░░░░░░░░   0%
```

---

## 🔌 KAMIS API 명세 (정리)

> 다른 AI가 KAMIS 클라이언트를 작성할 때 이 섹션만 보면 됨.

### 사용 API: 일별 부류별 도/소매가격정보

- **공식 문서**: https://www.kamis.or.kr/customer/reference/openapi_list.do?action=detail&boardno=1
- **엔드포인트**: `http://www.kamis.or.kr/service/price/xml.do`
- **Action**: `dailyPriceByCategoryList`
- **메서드**: GET (쿼리 파라미터)
- **반환 형식**: JSON 또는 XML (우리는 JSON 사용)

### 요청 파라미터

| 파라미터 | 타입 | 필수 | 설명 |
|---------|------|------|------|
| `p_cert_key` | string | ✅ | 인증 Key (KAMIS 발급) |
| `p_cert_id` | string | ✅ | 요청자 ID (KAMIS 발급) |
| `p_returntype` | string | ✅ | `json` 또는 `xml` (우리는 `json`) |
| `p_product_cls_code` | string | 선택 | `01`=소매, `02`=도매 (default: `02`) |
| `p_item_category_code` | string | 선택 | 부류코드 (default: `100`) |
| `p_country_code` | string | 선택 | 지역코드 (default: 전체) |
| `p_regday` | string | 선택 | `yyyy-mm-dd` (default: 최근 조사일) |
| `p_convert_kg_yn` | string | 선택 | `Y`=1kg 환산, `N`=원래 단위 (default: `N`) |

### 부류 코드 (`p_item_category_code`)

| 코드 | 부류 |
|-----|------|
| 100 | 식량작물 |
| 200 | 채소류 |
| 300 | 특용작물 |
| 400 | 과일류 |
| 500 | 축산물 |
| 600 | 수산물 |

### 주요 지역 코드 (`p_country_code`) — 소매 기준

| 코드 | 지역 | 코드 | 지역 |
|-----|------|-----|------|
| 1101 | 서울 | 3214 | 강릉 |
| 2100 | 부산 | 3211 | 춘천 |
| 2200 | 대구 | 3311 | 청주 |
| 2300 | 인천 | 3511 | 전주 |
| 2401 | 광주 | 3711 | 포항 |
| 2501 | 대전 | 3911 | 제주 |
| 2601 | 울산 | 2701 | 세종 |
| 3111 | 수원 | … | (전체 목록은 `data/kamis_codes.xlsx`) |

> 도매가격(`p_product_cls_code=02`) 선택 가능 지역은 더 적음: 서울, 부산, 대구, 광주, 대전.

### 응답 필드 ⭐

**한 번 호출로 시계열 데이터 7개가 다 옴 → 변동률 계산이 단순함.**

| 필드 | 의미 |
|------|------|
| `condition` | 요청 메시지 |
| `data` | 응답 메시지 |
| `item_name` | 품목명 (예: 사과) |
| `itemcode` | 품목코드 (예: 411) |
| `kind_name` | 품종명 (예: 후지) |
| `kindcode` | 품종코드 |
| `rank` | 등급 상태 (상품 / 중품) |
| `unit` | 단위 (예: 10개, kg) |
| `day1` | 조회일 날짜 |
| `dpr1` | **조회일 가격** ⭐ |
| `day2` | 1일 전 날짜 |
| `dpr2` | 1일 전 가격 |
| `day3` | 1주일 전 날짜 |
| `dpr3` | **1주일 전 가격** ⭐ |
| `day4` | 2주일 전 날짜 |
| `dpr4` | 2주일 전 가격 |
| `day5` | 1개월 전 날짜 |
| `dpr5` | **1개월 전 가격** ⭐ |
| `day6` | 1년 전 날짜 |
| `dpr6` | 1년 전 가격 |
| `day7` | 평년 일자 |
| `dpr7` | 평년 가격 |

**핵심 시사점:**
- 변동률 계산하려고 별도 호출 불필요. `dpr1` ↔ `dpr3` 비교만으로 7일 변동률, `dpr1` ↔ `dpr5`로 1개월 변동률 즉시 산출.
- 가격 문자열에 콤마 포함 가능성 (`"3,500"`) → 파싱 시 제거.
- 데이터 없는 날은 `"-"` 또는 빈 문자열로 올 수 있음 → 방어 코드 필요.

### 에러 코드

| code | Message | 대응 |
|------|---------|------|
| 000 | Success | 정상 |
| 001 | no data | 해당 조건 데이터 없음. 빈 결과 처리 |
| 200 | Wrong Parameters | 파라미터 점검 |
| 900 | Unauthenticated request | `cert_key` / `cert_id` 잘못됨 → `.env` 확인 |

### ⚠️ cert_id 이슈

**상황**: 사용자가 받은 키가 1개. 명세상 `p_cert_key`와 `p_cert_id` 둘 다 필수.

**해결 시도 순서**:
1. **본인 가입 이메일을 `p_cert_id`로 사용** (KAMIS는 가입 이메일을 cert_id로 쓰는 경우가 흔함)
2. 안 되면 KAMIS 마이페이지 → Open API 신청 내역 → 상세 페이지 확인
3. 여전히 안 되면 KAMIS 고객센터 문의

**테스트 방법**: `scripts/test_kamis.py`에서 호출 후
- `code: 000` → 성공, 진행
- `code: 900` → cert_id 잘못됨, 다른 값 시도

### 호출 예시 (서울, 채소류 소매, 2026-04-25)

```
http://www.kamis.or.kr/service/price/xml.do?
  action=dailyPriceByCategoryList
  &p_product_cls_code=01
  &p_item_category_code=200
  &p_country_code=1101
  &p_regday=2026-04-25
  &p_convert_kg_yn=N
  &p_cert_key={KEY}
  &p_cert_id={ID}
  &p_returntype=json
```

---

## 🗂 KAMIS 코드 체계 (정리)

> 엑셀 원본: `data/kamis_codes.xlsx` (8개 시트)

### 시트 구성

| 시트명 | 내용 | 행 수 |
|-------|------|------|
| 부류코드 | 6개 부류 (식량/채소/특용/과일/축산/수산) | 6 |
| 품목코드 | 부류 안의 품목 (예: 쌀, 사과, 배추) | 약 180 |
| 품종코드 | 품목 안의 세부 품종 (예: 사과 → 후지) | 약 234 |
| **코드통합** | 부류+품목+품종 통합 (시드 작업에 가장 유용) | 약 234 |
| 등급코드 | `04`=상품, `05`=중품, `07`=유기농 등 | 약 30 |
| 축산물 코드 | 축평원 별도 API용 (소·돼지·닭) | 약 58 |
| 산물코드 | 결과 검증용 (요청에는 코드통합 사용 권장) | 약 894 |
| 지역 및 시장 코드 | 지역코드 + 세부 시장코드 | 약 233 |

### 주요 품목 20종 (시드 데이터 후보)

이미 Phase 3에서 시드 작업 완료된 목록 — KAMIS 코드와 매핑 필요:

**식량(100)**: 쌀(111), 콩(141)
**채소류(200)**: 배추, 무, 양파, 대파, 마늘, 시금치, 오이, 호박
**과일류(400)**: 사과, 배, 감귤
**축산물(500)**: 돼지고기, 소고기, 닭고기, 계란
**수산물(600)**: 갈치, 고등어, 오징어

→ Phase 5에서 `kamis_client.py` 구현할 때 각 품목의 정확한 `itemcode`/`kindcode` 매핑 필요. 코드는 `data/kamis_codes.xlsx`의 "코드통합" 시트 참조.

---

## ✅ Week 1 상세 진행

### Phase 0: 준비 ✅ 완료

- [x] KAMIS Open API 신청 (cert_key 발급 받음, cert_id는 가입 이메일로 추정)
- [x] GitHub 레포 생성 (eolmani, private)
- [x] Python 3.12 + uv 환경 셋업
- [x] FastAPI 기본 프로젝트 (`main.py`)
- [x] `.gitignore` Python용 정비
- [x] 첫 커밋 + 푸시 (`feat: initialize FastAPI project with uv`)

### Phase 1: 환경 구성 ✅ 완료

- [x] PostgreSQL Docker 컨테이너 띄우기
- [x] `docker-compose.yml` 작성
- [x] `.env` + `.env.example` 파일 만들기
- [x] `app/config.py` (pydantic-settings) 작성
- [x] `app/database.py` (SQLAlchemy 엔진/세션) 작성
- [x] DB 연결 확인 (간단한 헬스체크)

### Phase 2: 데이터 탐색 🟡 진행 중

- [x] **KAMIS API 명세 분석 완료** (위 섹션 참조)
- [x] **응답 구조 파악 완료** (dpr1~dpr7로 시계열 한 번에 받음)
- [x] **부류/품목/지역 코드 체계 파악 완료** (`data/kamis_codes.xlsx`)
- [x] 주요 품목 20종 후보 정리 (Phase 3 시드와 일치)
- [ ] KAMIS API 키 받음 → `.env`에 등록 (cert_key는 받음, cert_id는 가입 이메일로 시도)
- [ ] httpx로 KAMIS API 직접 호출 → 실제 응답 확인
- [ ] 품목별 정확한 `itemcode` / `kindcode` 매핑 (코드통합 시트 참조)
- [ ] `app/services/kamis_client.py` 본 구현 (현재 골격만 있음)

### Phase 3: 도메인 모델 ✅ 완료

- [x] Alembic 초기화
- [x] `Item` 모델 (id, code, name, category, unit)
- [x] `PriceHistory` 모델 (id, item_id, price, recorded_date, source)
- [x] 첫 마이그레이션 적용
- [x] 시드 데이터 스크립트 (품목 마스터 20종)

> ⚠️ Phase 5 구현 시 `Item` 모델에 `kamis_item_code`, `kamis_kind_code` 필드 추가 필요할 수 있음. 응답 매핑 보고 결정.

### Phase 4: 백엔드 API ✅ 완료

- [x] `GET /api/prices/today` 엔드포인트
- [x] Pydantic 응답 스키마 (`schemas/price.py`)
- [x] 변동률 계산 로직 (7일/30일)
- [x] Swagger UI 확인 (`/docs`)

### Phase 5: 데이터 수집 🟡 뼈대 완료 / API 키 검증 대기

- [x] APScheduler 설정 (매일 06:00 Asia/Seoul)
- [x] `kamis_client.py` 골격 (키 없으면 빈 리스트 반환)
- [x] `price_collector.py` — TODO 블록 채우면 즉시 작동
- [ ] **`scripts/test_kamis.py` 작성 → 실제 호출해서 응답 확인** ← 다음 액션
- [ ] cert_id 검증 (가입 이메일 → 안 되면 마이페이지 확인)
- [ ] `KamisClient.fetch_daily_prices()` 본 구현
  - 파라미터: `category_code`, `country_code=1101`, `regday`, `product_cls_code=01`
  - 응답에서 `dpr1` 파싱 (콤마 제거, "-" 처리)
  - 우리 `Item` 모델과 매핑
- [ ] `collect_prices()` 구현 — 6개 부류 순회 호출 → DB 저장
- [ ] 초기 데이터 백필 (지난 7~30일)

### Phase 6: 프론트 ✅ 완료

- [x] `app/templates/base.html`, `index.html`
- [x] Tailwind CDN 적용
- [x] 품목 카드 + 변동률 화살표 (▲빨강 / ▼파랑)
- [x] 카테고리별 섹션 (곡물/채소/과일/축산/수산)
- [x] 데이터 없을 때 안내 화면
- [x] 모바일 반응형 (grid sm:grid-cols-2)
- [x] Footer (출처 표시)
- [ ] Chart.js 7일 변동 그래프 (데이터 쌓이면 추가)

### Phase 7: 배포 ⬜ 대기

- [ ] `Dockerfile` 작성
- [ ] Railway 가입 / GitHub 연동
- [ ] 환경변수 등록 (KAMIS 키, DB URL)
- [ ] 배포 후 동작 확인
- [ ] 깃허브 README에 라이브 URL 추가
- [ ] **레포 Public 전환**

---

## 📋 다음 액션 (Top 3)

1. **`scripts/test_kamis.py` 작성 → 실제 호출 → cert_id 검증** ← 즉시 가능
2. 응답 구조 보고 `KamisClient` 본 구현 + 6개 부류 순회 + DB 적재
3. Phase 7: Dockerfile 작성 → Railway 배포 → Public 전환

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
| 2026-04-28 | KAMIS API는 `dailyPriceByCategoryList` 사용 | 응답에 dpr1~dpr7로 시계열 한 번에 옴, 변동률 계산 단순 |
| 2026-04-28 | 별도 7일/30일 호출 없음 | dpr3=1주전, dpr5=1개월전 그대로 활용 → API 호출 횟수 1/N |
| 2026-04-28 | 가격 데이터는 소매(`p_product_cls_code=01`) 우선 | 일반 사용자 체감 물가가 목표. 도매는 향후 분석용 |
| 2026-04-28 | 1차 지역은 서울(`1101`) | 데이터 가장 풍부, 도매·소매 모두 지원 |

---

## ⚠️ 차단 / 대기 중인 항목

| 항목 | 상태 | 메모 |
|------|------|------|
| KAMIS `cert_id` 검증 | 🟡 진행 가능 | 본인 가입 이메일을 cert_id로 시도 → `code 900` 뜨면 마이페이지 확인 |

---

## 🤝 AI 협업 안내 (다른 AI에게 컨텍스트 줄 때)

이 프로젝트를 다른 AI(Claude Code, Cursor, ChatGPT 등)와 같이 작업할 때:

1. **`PROJECT.md`** 먼저 공유 — 프로젝트 전체 그림
2. **`PROGRESS.md`** (이 파일) 공유 — 현재 어디까지 했는지 + KAMIS API 명세
3. **`data/kamis_codes.xlsx`** — 코드 매핑 작업 시 필요
4. 추가로 현재 작업 중인 코드 파일 공유

### 컨텍스트 프롬프트 템플릿

```
나는 "얼마니"라는 식료품 가격 추적 서비스를 만들고 있어.
첨부한 PROJECT.md는 전체 기획서이고, PROGRESS.md는 현재 진행도 + KAMIS API 명세야.
지금 [Phase X]의 [작업명]을 하고 있는데 [구체적인 도움 요청].
기술 스택: Python 3.12, FastAPI, PostgreSQL, SQLAlchemy 2.0, uv 패키지 관리.
```

### Claude Code용 첫 프롬프트 (KAMIS 클라이언트 구현)

```
PROJECT.md, PROGRESS.md 읽고 컨텍스트 잡아줘.

지금 Phase 5 구현 단계야. PROGRESS.md의 "KAMIS API 명세" 섹션 참고해서:
1. scripts/test_kamis.py 작성 (실제 호출 + 응답 출력)
2. 내가 실행해서 응답 결과 보여주면, 그걸 보고 KamisClient 본 구현
3. 6개 부류 순회하는 collect_prices() 구현
4. PROGRESS.md 진행상황 업데이트

cert_id는 일단 내 가입 이메일 시도. code:900 뜨면 알려줘.
```

---

## 📝 변경 로그

### 2026-04-28
- **KAMIS API 명세 정리 섹션 추가** (요청/응답/에러/cert_id 이슈)
- **KAMIS 코드 체계 섹션 추가** (8개 시트 구조, 주요 품목 매핑)
- Phase 2를 "진행 중"으로 변경 (명세 분석 완료, 실제 호출 대기)
- Phase 3 완료: Item/PriceHistory 모델, Alembic 마이그레이션, 품목 시드 20종
- Phase 4 완료: GET /api/prices/today, Pydantic 스키마, 7일/30일 변동률 계산
- Phase 5 뼈대 완료: APScheduler(06:00 KST), kamis_client.py 골격
- Phase 6 완료: Jinja2 템플릿, Tailwind CDN, 카테고리별 가격 카드 UI

### 2026-04-27
- 프로젝트 시작
- 기획서 v1.0 (Java) → v1.1 (Python) 전환
- Phase 0 완료 (기본 프로젝트 셋업)
- Phase 1 완료 (PostgreSQL Docker, config.py, database.py)
