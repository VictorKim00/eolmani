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
    group_code: str | None = None
    variant_label: str | None = None
    sort_order: int = 0
    vs_nation: float | None = None  # 전국 평균 대비 % (지역 선택 시)

    model_config = {"from_attributes": True}


class PricesTodayResponse(BaseModel):
    date: date
    region_code: str = ""
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
    change_7d: float | None
    change_30d: float | None
    change_avg: float | None
    points: list[PriceHistoryPoint]
