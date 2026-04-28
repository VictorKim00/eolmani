from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.price import PricesTodayResponse
from app.services.price_service import get_today_prices

router = APIRouter(prefix="/api/prices", tags=["prices"])


@router.get("/today", response_model=PricesTodayResponse)
def today_prices(db: Session = Depends(get_db)):
    return get_today_prices(db)
