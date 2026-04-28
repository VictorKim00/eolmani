from collections import defaultdict
from contextlib import asynccontextmanager
from datetime import date

from fastapi import Depends, FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.prices import router as prices_router
from app.database import get_db
from app.scheduler.price_collector import start_scheduler, stop_scheduler
from app.services.price_service import get_today_prices

CATEGORY_EMOJI: dict[str, str] = {
    "곡물": "🌾",
    "채소": "🥬",
    "과일": "🍎",
    "축산": "🥩",
    "수산": "🐟",
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()
    yield
    stop_scheduler()


app = FastAPI(title="얼마니", version="0.1.0", lifespan=lifespan)
app.include_router(prices_router)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")


@app.get("/")
def index(request: Request, db: Session = Depends(get_db)):
    data = get_today_prices(db)

    # 카테고리별 그룹핑
    categories: dict[str, list] = defaultdict(list)
    for item in data.items:
        categories[item.category].append(item)

    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "today": date.today().strftime("%Y년 %m월 %d일"),
            "categories": dict(categories),
            "category_emoji": CATEGORY_EMOJI,
            "total_count": data.count,
        },
    )


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/health/db")
def health_db(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"status": "ok", "db": "connected"}
