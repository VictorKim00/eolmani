from collections import defaultdict
from contextlib import asynccontextmanager
from datetime import date, timedelta

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.api.prices import router as prices_router
from app.config import settings
from app.database import get_db
from app.models.item import Item as ItemModel
from app.scheduler.price_collector import collect_prices, start_scheduler, stop_scheduler
from app.services.price_service import get_item_history, get_today_prices
from app.services.price_stats_service import enrich_season_picks, get_month_vs_annual
from app.services.item_origins import get_item_origin
from app.services.regions import REGION_COORDS, REGION_LABEL, REGION_WEATHER_LABEL, REGIONS, normalize_region
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

# 묶음 단위 → (나누는 수, 표시 단위) — 1개·1구·1kg당 환산
UNIT_DIVISOR: dict[str, tuple[int, str]] = {
    "10개": (10, "1개당"),
    "30구": (30, "1구당"),
    "20kg": (20, "1kg당"),
    "500g": (5, "100g당"),
}

# 그룹 카드에서 보여줄 표시 이름
GROUP_DISPLAY_NAMES: dict[str, str] = {
    "beef_korean": "소고기(한우)",
    "pork": "돼지고기",
    "rice": "쌀",
    "cucumber": "오이",
    "pumpkin": "호박",
    "lettuce": "상추",
}


def _build_category_cards(items_in_cat: list) -> list:
    """
    카테고리 내 품목을 group_code 기준으로 묶어 카드 목록을 반환.
    그룹 품목은 첫 등장 위치에 ONE 그룹 카드로 삽입.
    반환 요소 형태:
      {"is_group": False, "item": PriceItem}
      {"is_group": True, "group_code": str, "group_name": str,
       "default": PriceItem, "variants": [PriceItem, ...]}
    """
    group_map: dict[str, list] = {}
    for item in items_in_cat:
        if item.group_code:
            group_map.setdefault(item.group_code, []).append(item)

    for code in group_map:
        group_map[code].sort(key=lambda x: x.sort_order)

    cards: list = []
    seen_groups: set = set()

    for item in items_in_cat:
        if item.group_code:
            if item.group_code not in seen_groups:
                variants = group_map[item.group_code]
                cards.append({
                    "is_group": True,
                    "group_code": item.group_code,
                    "group_name": GROUP_DISPLAY_NAMES.get(item.group_code, item.name),
                    "default": variants[0],
                    "variants": variants,
                })
                seen_groups.add(item.group_code)
        else:
            cards.append({"is_group": False, "item": item})

    return cards


def _last_collected_date() -> date | None:
    """DB에서 가장 최근 수집일 반환."""
    from app.database import SessionLocal as _DB
    from app.models.price_history import PriceHistory as _PH
    db = _DB()
    try:
        return db.execute(
            select(_PH.recorded_date)
            .where(_PH.source == "kamis")
            .order_by(_PH.recorded_date.desc())
            .limit(1)
        ).scalar_one_or_none()
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()

    # 배포·재시작으로 06:00 / 15:00 job을 놓쳤을 때 즉시 수집
    import asyncio
    if _last_collected_date() != date.today():
        asyncio.create_task(collect_prices())

    yield
    stop_scheduler()


app = FastAPI(title="얼마니", version="0.1.0", lifespan=lifespan)
app.include_router(prices_router)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")


@app.get("/")
async def index(request: Request, region: str = "", db: Session = Depends(get_db)):
    region_code = normalize_region(region)
    data = get_today_prices(db, region_code=region_code)

    # 카테고리별 그룹핑 → 그룹 카드 목록으로 변환
    raw_categories: dict[str, list] = defaultdict(list)
    for item in data.items:
        raw_categories[item.category].append(item)

    category_cards: dict[str, list] = {
        cat: _build_category_cards(items)
        for cat, items in raw_categories.items()
    }

    # TOP 5 오늘의 특가: 7일 대비 하락폭이 큰 순 (그룹 default 포함)
    all_for_deals = [
        (c["default"] if c["is_group"] else c["item"])
        for cards in category_cards.values()
        for c in cards
    ]
    deals = sorted(
        [i for i in all_for_deals if i.change_7d is not None and i.change_7d < 0],
        key=lambda i: i.change_7d,
    )[:5]

    # 신호등 계산 (전체 개별 품목 기준)
    signals = {
        i.code: compute_signal(i.change_avg, i.change_30d, i.change_7d)
        for i in data.items
    }

    # 신호등 분포 (요약 배너용)
    green_count = sum(1 for s in signals.values() if s == "green")
    red_count = sum(1 for s in signals.values() if s == "red")
    yellow_count = len(signals) - green_count - red_count
    top_deal = deals[0] if deals else None

    # 이번 주 일~토 구조 — 과거 날짜도 실제 날씨 데이터 포함
    today_date = date.today()
    days_since_sunday = (today_date.weekday() + 1) % 7  # 일=0, 월=1, ..., 토=6
    week_start = today_date - timedelta(days=days_since_sunday)

    region_lat, region_lon = REGION_COORDS[region_code]
    forecast_full = await fetch_forecast(region_lat, region_lon, days=7, past_days=days_since_sunday)
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

    category_counts = {cat: len(cards) for cat, cards in category_cards.items()}

    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "today": today_date.strftime("%Y년 %m월 %d일"),
            "category_cards": category_cards,
            "category_counts": category_counts,
            "category_emoji": CATEGORY_EMOJI,
            "unit_divisor": UNIT_DIVISOR,
            "total_count": data.count,
            "deals": deals,
            "signals": signals,
            "signal_emoji": SIGNAL_EMOJI,
            "signal_label": SIGNAL_LABEL,
            "green_count": green_count,
            "yellow_count": yellow_count,
            "red_count": red_count,
            "top_deal": top_deal,
            "season": season,
            "week_days": week_days,
            "impacts": impacts,
            "week_summary": week_summary,
            "regions": REGIONS,
            "current_region_code": region_code,
            "current_region_label": REGION_LABEL[region_code],
            "weather_location_label": REGION_WEATHER_LABEL[region_code],
        },
    )


@app.get("/items/{item_code}")
async def item_detail(item_code: str, request: Request, region: str = "", db: Session = Depends(get_db)):
    region_code = normalize_region(region)
    history = get_item_history(db, item_code, region_code=region_code)
    if history is None:
        raise HTTPException(status_code=404, detail="품목을 찾을 수 없습니다")

    signal = compute_signal(history.change_avg, history.change_30d, history.change_7d)

    today_date = date.today()
    chart_labels = [str(p.date) for p in history.points]
    chart_prices = [p.price for p in history.points]
    month_stats = get_month_vs_annual(db, item_code, today_date.month)
    action = get_action(signal, history.change_7d, history.change_30d, month_stats)

    # 같은 그룹의 형제 품목 조회 (탭 전환용)
    current_item = db.execute(
        select(ItemModel).where(ItemModel.code == item_code)
    ).scalar_one_or_none()
    siblings: list[ItemModel] = []
    if current_item and current_item.group_code:
        siblings = db.execute(
            select(ItemModel)
            .where(ItemModel.group_code == current_item.group_code)
            .order_by(ItemModel.sort_order)
        ).scalars().all()

    # 산지 날씨 — 그룹 품목은 group_code의 첫 번째 항목 기준으로 산지 조회
    origin_code = (
        siblings[0].code if siblings else item_code
    )
    origin = get_item_origin(origin_code)
    origin_forecast: list[dict] = []
    origin_label = ""
    origin_impacts: dict = {}
    if origin:
        origin_label, o_lat, o_lon = origin
        origin_forecast = await fetch_forecast(o_lat, o_lon, days=5)
        origin_impacts = get_impacts(origin_forecast)

    return templates.TemplateResponse(
        request,
        "item_detail.html",
        {
            "today": today_date.strftime("%Y년 %m월 %d일"),
            "history": history,
            "signal": signal,
            "signal_emoji": SIGNAL_EMOJI,
            "signal_label": SIGNAL_LABEL,
            "unit_divisor": UNIT_DIVISOR,
            "chart_labels": chart_labels,
            "chart_prices": chart_prices,
            "month_stats": month_stats,
            "current_month": today_date.month,
            "action": action,
            "siblings": siblings,
            "current_item_code": item_code,
            "group_display_name": GROUP_DISPLAY_NAMES.get(
                current_item.group_code if current_item else "", ""
            ),
            "regions": REGIONS,
            "current_region_code": region_code,
            "current_region_label": REGION_LABEL[region_code],
            "origin_forecast": origin_forecast,
            "origin_label": origin_label,
            "origin_impacts": origin_impacts,
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
