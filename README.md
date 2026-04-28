# 얼마니 (Eolmani)

**오늘 장보기 전에, 얼마니?**

농축수산물 20종의 오늘 가격과 변동률을 한눈에 확인하는 서비스입니다.

🌐 **[eolmani-production.up.railway.app](https://eolmani-production.up.railway.app)**

---

## 주요 기능

- 농축수산물 20종 소매 가격 (서울 기준)
- 전일·7일·30일 변동률 표시
- 매일 06:00 자동 수집 (KAMIS 공공 데이터)
- 모바일 반응형

## 수록 품목

| 분류 | 품목 |
|------|------|
| 곡물 | 쌀, 콩 |
| 채소 | 배추, 무, 양파, 대파, 마늘, 시금치, 오이, 애호박 |
| 과일 | 사과, 배, 감귤 |
| 축산 | 소고기(한우 등심), 돼지고기(삼겹살), 닭고기, 계란 |
| 수산 | 갈치, 고등어, 오징어 |

## 기술 스택

- **Backend**: Python 3.12, FastAPI, SQLAlchemy 2.0, APScheduler
- **DB**: PostgreSQL
- **Frontend**: Jinja2, Tailwind CSS
- **Infra**: Docker, Railway
- **Data**: [KAMIS 농산물유통정보](https://www.kamis.or.kr)

## 로컬 실행

```bash
# 의존성 설치
uv sync

# DB 실행 (Docker)
docker-compose up -d

# 마이그레이션
uv run alembic upgrade head

# 시드 데이터
uv run python scripts/seed_items.py

# 서버 실행
uv run uvicorn app.main:app --reload
```

---

데이터 출처: 농넷 KAMIS (비상업 목적 사용)
