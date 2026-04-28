from datetime import date

from pydantic import BaseModel


class PriceItem(BaseModel):
    item_id: int
    code: str
    name: str
    category: str
    unit: str
    price: float
    recorded_date: date
    change_7d: float | None   # 7일 변동률 (%), None이면 데이터 없음
    change_30d: float | None  # 30일 변동률 (%), None이면 데이터 없음

    model_config = {"from_attributes": True}


class PricesTodayResponse(BaseModel):
    date: date
    count: int
    items: list[PriceItem]
