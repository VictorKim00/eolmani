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
    change_7d: float | None    # 7일 변동률 (%)
    change_30d: float | None   # 30일 변동률 (%)
    change_avg: float | None   # 평년 대비 변동률 (%)

    model_config = {"from_attributes": True}


class PricesTodayResponse(BaseModel):
    date: date
    count: int
    items: list[PriceItem]


class PriceHistoryPoint(BaseModel):
    date: date
    price: float


class PriceHistoryResponse(BaseModel):
    item_code: str
    item_name: str
    unit: str
    category: str
    current_price: float
    avg_year_price: float | None
    points: list[PriceHistoryPoint]
