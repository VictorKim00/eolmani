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
from app.services.price_service import get_item_history, get_today_prices
from app.services.signal_service import SIGNAL_EMOJI, SIGNAL_LABEL, compute_signal

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

    # TOP 5 오늘의 특가: 7일 대비 하락폭이 큰 순
    deals = sorted(
        [i for i in data.items if i.change_7d is not None and i.change_7d < 0],
        key=lambda i: i.change_7d,
    )[:5]

    # 신호등 계산
    signals = {
        i.code: compute_signal(i.change_avg, i.change_30d, i.change_7d)
        for i in data.items
    }

    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "today": date.today().strftime("%Y년 %m월 %d일"),
            "categories": dict(categories),
            "category_emoji": CATEGORY_EMOJI,
            "total_count": data.count,
            "deals": deals,
            "signals": signals,
            "signal_emoji": SIGNAL_EMOJI,
            "signal_label": SIGNAL_LABEL,
        },
    )


@app.get("/items/{item_code}")
def item_detail(item_code: str, request: Request, db: Session = Depends(get_db)):
    history = get_item_history(db, item_code)
    if history is None:
        return templates.TemplateResponse(request, "index.html", {"error": "품목 없음"}, status_code=404)

    signal = compute_signal(
        None,  # avg_year_price는 history.avg_year_price로 계산
        None,
        None,
    )
    if history.points:
        latest = history.points[-1].price
        p30 = history.points[0].price if len(history.points) >= 30 else None
        p7 = history.points[-8].price if len(history.points) >= 8 else None
        def _rate(past):
            if past is None or past == 0:
                return None
            return round((latest - past) / past * 100, 2)
        signal = compute_signal(
            _rate(history.avg_year_price),
            _rate(p30),
            _rate(p7),
        )

    return templates.TemplateResponse(
        request,
        "item_detail.html",
        {
            "today": date.today().strftime("%Y년 %m월 %d일"),
            "history": history,
            "signal": signal,
            "signal_emoji": SIGNAL_EMOJI,
            "signal_label": SIGNAL_LABEL,
        },
    )


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/health/db")
def health_db(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"status": "ok", "db": "connected"}
