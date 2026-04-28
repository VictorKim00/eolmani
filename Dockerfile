FROM python:3.12-slim

WORKDIR /app

# uv 설치
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# 의존성 먼저 복사 (레이어 캐시 활용)
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# 앱 소스 복사
COPY app/ ./app/
COPY migrations/ ./migrations/
COPY alembic.ini ./

# 포트
EXPOSE 8000

# DB 마이그레이션 → 앱 실행
CMD uv run alembic upgrade head && \
    uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
