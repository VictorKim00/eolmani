from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.price import PriceHistoryResponse, PricesTodayResponse
from app.services.price_service import get_item_history, get_today_prices
from app.services.regions import normalize_region

router = APIRouter(prefix="/api/prices", tags=["prices"])


@router.get("/today", response_model=PricesTodayResponse)
def today_prices(region: str = "", db: Session = Depends(get_db)):
    return get_today_prices(db, region_code=normalize_region(region))


@router.get("/{item_code}/history", response_model=PriceHistoryResponse)
def item_history(item_code: str, days: int = 30, region: str = "", db: Session = Depends(get_db)):
    result = get_item_history(db, item_code, days, region_code=normalize_region(region))
    if result is None:
        raise HTTPException(status_code=404, detail="품목을 찾을 수 없습니다")
    return result
