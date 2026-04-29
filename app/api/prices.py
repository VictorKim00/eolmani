from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.price import PriceHistoryResponse, PricesTodayResponse
from app.services.price_service import get_item_history, get_today_prices

router = APIRouter(prefix="/api/prices", tags=["prices"])


@router.get("/today", response_model=PricesTodayResponse)
def today_prices(db: Session = Depends(get_db)):
    return get_today_prices(db)


@router.get("/{item_code}/history", response_model=PriceHistoryResponse)
def item_history(item_code: str, days: int = 30, db: Session = Depends(get_db)):
    result = get_item_history(db, item_code, days)
    if result is None:
        raise HTTPException(status_code=404, detail="품목을 찾을 수 없습니다")
    return result
