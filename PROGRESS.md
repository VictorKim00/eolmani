# 얼마니 — 진행도

> 이 파일은 **사람과 AI가 같이 보는 진행도 추적 문서**입니다.
> 다른 AI에게 컨텍스트 전달 시 `PROJECT.md`와 함께 읽도록 안내해주세요.

- **시작일**: 2026-04-27
- **현재 주차**: Week 1
- **마지막 업데이트**: 2026-04-27

---

## 🎯 현재 목표

**Week 1 — MVP 출시**: KAMIS 데이터 → DB 적재 → 웹 페이지에 가격/변동률 표시 → 배포

---

## 📊 전체 진행률

```
Week 1 (MVP)            ███░░░░░░░  30%   ← 진행 중
Week 2 (레시피)          ░░░░░░░░░░   0%
Week 3 (알림)           ░░░░░░░░░░   0%
Week 4 (영수증 OCR)     ░░░░░░░░░░   0%
Week 5 (개인 CPI)       ░░░░░░░░░░   0%
Week 6 (슈링크플레이션) ░░░░░░░░░░   0%
Week 7+ (AI 예측)       ░░░░░░░░░░   0%
```

---

## ✅ Week 1 상세 진행

### Phase 0: 준비 ✅ 완료

- [x] KAMIS Open API 신청 (cert_id, cert_key 발급 대기)
- [x] GitHub 레포 생성 (eolmani, private)
- [x] Python 3.12 + uv 환경 셋업
- [x] FastAPI 기본 프로젝트 (`main.py`)
- [x] `.gitignore` Python용 정비
- [x] 첫 커밋 + 푸시 (`feat: initialize FastAPI project with uv`)

### Phase 1: 환경 구성 🟡 진행 중

- [ ] PostgreSQL Docker 컨테이너 띄우기
- [ ] `docker-compose.yml` 작성
- [ ] `.env` + `.env.example` 파일 만들기
- [ ] `app/config.py` (pydantic-settings) 작성
- [ ] `app/database.py` (SQLAlchemy 엔진/세션) 작성
- [ ] DB 연결 확인 (간단한 헬스체크)

### Phase 2: 데이터 탐색 ⬜ 대기

- [ ] KAMIS API 키 받음 → `.env`에 등록
- [ ] httpx로 KAMIS API 직접 호출
- [ ] 응답 JSON 구조 파악 (어떤 필드 있는지)
- [ ] 주요 품목 코드 정리 (목표: 20종)
  - [ ] 사과, 배, 감귤
  - [ ] 배추, 무, 양파, 대파, 마늘
  - [ ] 시금치, 오이, 호박
  - [ ] 돼지고기, 소고기, 닭고기
  - [ ] 계란
  - [ ] 쌀, 콩
  - [ ] 갈치, 고등어, 오징어
- [ ] `app/services/kamis_client.py` 초안 작성

### Phase 3: 도메인 모델 ⬜ 대기

- [ ] Alembic 초기화
- [ ] `Item` 모델 (id, code, name, category, unit)
- [ ] `PriceHistory` 모델 (id, item_id, price, recorded_date, source)
- [ ] 첫 마이그레이션 적용
- [ ] 시드 데이터 스크립트 (품목 마스터)

### Phase 4: 백엔드 API ⬜ 대기

- [ ] `GET /api/prices/today` 엔드포인트
- [ ] Pydantic 응답 스키마 (`schemas/price.py`)
- [ ] 변동률 계산 로직 (7일/30일)
- [ ] Swagger UI 확인

### Phase 5: 데이터 수집 ⬜ 대기

- [ ] APScheduler 설정
- [ ] 매일 06시 KAMIS 호출 → DB 적재
- [ ] 에러 처리 + 로깅
- [ ] 초기 데이터 백필 (지난 7~30일)

### Phase 6: 프론트 ⬜ 대기

- [ ] `app/templates/base.html`, `index.html`
- [ ] Tailwind CDN 적용
- [ ] 품목 리스트 + 변동률 화살표(↑↓)
- [ ] 모바일 반응형
- [ ] Chart.js로 7일 변동 그래프
- [ ] Footer (출처 표시 + 후원 링크)

### Phase 7: 배포 ⬜ 대기

- [ ] `Dockerfile` 작성
- [ ] Railway 가입 / GitHub 연동
- [ ] 환경변수 등록 (KAMIS 키, DB URL)
- [ ] 배포 후 동작 확인
- [ ] 깃허브 README에 라이브 URL 추가
- [ ] **레포 Public 전환**

---

## 📋 다음 액션 (Top 3)

1. **PostgreSQL Docker 컨테이너 띄우기** ← 다음 단계
2. `.env` + 설정 클래스 작성
3. KAMIS API 키 받으면 즉시 응답 구조 파악

---

## 📚 결정 로그

이 프로젝트의 중요한 결정과 그 이유를 기록합니다. AI/협업자가 컨텍스트 빠르게 잡는 데 도움.

| 날짜 | 결정 | 이유 |
|------|------|------|
| 2026-04-27 | 프로젝트명 "얼마니" 확정 | 가격을 묻는 본질적 질문, 모든 기능을 하나로 묶는 컨셉 |
| 2026-04-27 | Java/Spring Boot → Python/FastAPI 전환 | 사용자 주력 언어가 Python, 데이터/AI 기능에 더 적합 |
| 2026-04-27 | 비상업 무료 서비스로 운영 | KAMIS 등 공공 데이터 라이선스 부담 회피, 신뢰 기반 |
| 2026-04-27 | GitHub 레포 처음엔 Private | 시크릿 실수 방어, MVP 완성 후 Public 전환 예정 |
| 2026-04-27 | 패키지 관리는 uv 채택 | 빠르고 표준화 추세, pip/poetry 대비 우수 |
| 2026-04-27 | Flask 대신 FastAPI 채택 | 자동 API 문서, Pydantic 타입 안전, async, 취업 가치 |
| 2026-04-27 | psycopg2 대신 psycopg3 (`psycopg[binary]`) | 신버전, 성능/기능 우수 |

---

## ⚠️ 차단 / 대기 중인 항목

| 항목 | 상태 | 메모 |
|------|------|------|
| KAMIS API 키 발급 | ⏳ 대기 중 | 신청 완료, 보통 1~2일 소요. 받기 전에는 응답 구조 미리 파악 어려움 |

---

## 🤝 AI 협업 안내 (다른 AI에게 컨텍스트 줄 때)

이 프로젝트를 다른 AI(Cursor, ChatGPT 등)와 같이 작업할 때:

1. **`PROJECT.md`** 먼저 공유 — 프로젝트 전체 그림
2. **`PROGRESS.md`** (이 파일) 공유 — 현재 어디까지 했는지
3. 추가로 현재 작업 중인 코드 파일 공유

### 컨텍스트 프롬프트 템플릿

```
나는 "얼마니"라는 식료품 가격 추적 서비스를 만들고 있어.
첨부한 PROJECT.md는 전체 기획서이고, PROGRESS.md는 현재 진행도야.
지금 [Phase X]의 [작업명]을 하고 있는데 [구체적인 도움 요청].
기술 스택: Python 3.12, FastAPI, PostgreSQL, SQLAlchemy 2.0, uv 패키지 관리.
```

---

## 📝 변경 로그

### 2026-04-27
- 프로젝트 시작
- 기획서 v1.0 (Java) → v1.1 (Python) 전환
- Phase 0 완료 (기본 프로젝트 셋업)
- Phase 1 시작 (PostgreSQL 연결 준비)
