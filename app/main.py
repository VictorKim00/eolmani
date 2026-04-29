from collections import defaultdict
from contextlib import asynccontextmanager
from datetime import date, timedelta

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.prices import router as prices_router
from app.config import settings
from app.database import get_db
from app.scheduler.price_collector import start_scheduler, stop_scheduler
from app.services.price_service import get_item_history, get_today_prices
from app.services.price_stats_service import enrich_season_picks, get_month_vs_annual
from app.services.season_service import get_this_month_season
from app.services.signal_service import SIGNAL_EMOJI, SIGNAL_LABEL, compute_signal, get_action
from app.services.weather_client import WEEKDAY_KO, fetch_forecast
from app.services.weather_impact_service import get_impacts, get_week_summary

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
async def index(request: Request, db: Session = Depends(get_db)):
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

    # 이번 주 일~토 구조 — 과거 날짜도 실제 날씨 데이터 포함
    today_date = date.today()
    days_since_sunday = (today_date.weekday() + 1) % 7  # 일=0, 월=1, ..., 토=6
    week_start = today_date - timedelta(days=days_since_sunday)

    # past_days 포함해 전체 반환 → forecast_future는 오늘 이후 7일까지 포함
    forecast_full = await fetch_forecast(days=7, past_days=days_since_sunday)
    forecast_future = [d for d in forecast_full if d["date"] >= today_date.strftime("%Y-%m-%d")]
    impacts = get_impacts(forecast_future)
    week_summary = get_week_summary(forecast_future)

    forecast_lookup = {d["date"]: d for d in forecast_full}
    week_days = []
    for i in range(7):
        d = week_start + timedelta(days=i)
        d_str = d.strftime("%Y-%m-%d")
        if d_str in forecast_lookup:
            entry = {**forecast_lookup[d_str], "is_today": d == today_date, "is_past": d < today_date}
        else:
            entry = {
                "date": d_str,
                "weekday": WEEKDAY_KO[d.weekday()],
                "is_past": True,
                "is_today": False,
                "temp_max": None,
                "temp_min": None,
                "precip_prob": 0,
                "emoji": None,
            }
        week_days.append(entry)

    # 시즌 캘린더 — item_code 없는 미추적 품목 제외, 나머지에 신호등·가격·월별 통계 주입
    season = get_this_month_season()
    season["picks"] = [p for p in season["picks"] if p.get("item_code")]
    season["picks"] = enrich_season_picks(db, season["picks"], today_date.month)
    item_map = {i.code: i for i in data.items}
    for pick in season["picks"]:
        code = pick.get("item_code")
        if code and code in item_map:
            item = item_map[code]
            pick["signal"] = signals[code]
            pick["price"] = item.price
            pick["unit"] = item.unit
        else:
            pick["signal"] = None

    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "today": today_date.strftime("%Y년 %m월 %d일"),
            "categories": dict(categories),
            "category_emoji": CATEGORY_EMOJI,
            "total_count": data.count,
            "deals": deals,
            "signals": signals,
            "signal_emoji": SIGNAL_EMOJI,
            "signal_label": SIGNAL_LABEL,
            "season": season,
            "week_days": week_days,
            "impacts": impacts,
            "week_summary": week_summary,
        },
    )


@app.get("/items/{item_code}")
async def item_detail(item_code: str, request: Request, db: Session = Depends(get_db)):
    history = get_item_history(db, item_code)
    if history is None:
        raise HTTPException(status_code=404, detail="품목을 찾을 수 없습니다")

    signal = compute_signal(history.change_avg, history.change_30d, history.change_7d)

    today_date = date.today()
    chart_labels = [str(p.date) for p in history.points]
    chart_prices = [p.price for p in history.points]
    month_stats = get_month_vs_annual(db, item_code, today_date.month)
    action = get_action(signal, history.change_7d, history.change_30d, month_stats)

    return templates.TemplateResponse(
        request,
        "item_detail.html",
        {
            "today": today_date.strftime("%Y년 %m월 %d일"),
            "history": history,
            "signal": signal,
            "signal_emoji": SIGNAL_EMOJI,
            "signal_label": SIGNAL_LABEL,
            "chart_labels": chart_labels,
            "chart_prices": chart_prices,
            "month_stats": month_stats,
            "current_month": today_date.month,
            "action": action,
        },
    )


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/admin/collect")
async def admin_collect(request: Request):
    """수동 가격 수집 트리거 (배포 직후 데이터 갱신용)."""
    if settings.admin_secret:
        if request.headers.get("X-Admin-Key", "") != settings.admin_secret:
            raise HTTPException(status_code=401, detail="Unauthorized")
    from app.scheduler.price_collector import collect_prices
    await collect_prices()
    return {"status": "ok", "message": "수집 완료"}


@app.get("/health/db")
def health_db(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"status": "ok", "db": "connected"}
