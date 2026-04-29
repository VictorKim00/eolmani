"""
날씨 → 가격 영향 룰 엔진.
7일 예보를 받아 각 날짜의 극단적 날씨를 감지하고 영향 품목을 반환한다.
"""

from dataclasses import dataclass


@dataclass
class WeatherImpact:
    condition: str    # 조건 이름 (한파, 폭염 등)
    emoji: str
    items: list[str]  # 영향 받는 품목명
    direction: str    # "up" | "down"
    reason: str


# 룰 테이블: 농업기술센터 자료 기반
_RULES = [
    {
        "condition": "한파",
        "emoji": "🥶",
        "check": lambda d: d["temp_min"] <= -5,
        "items": ["배추", "시금치", "대파", "무"],
        "direction": "up",
        "reason": "한파로 노지 채소 수확 차질 우려",
    },
    {
        "condition": "추위",
        "emoji": "🌨️",
        "check": lambda d: -5 < d["temp_min"] <= 2,
        "items": ["시금치", "대파"],
        "direction": "up",
        "reason": "저온으로 잎채소 공급 감소 가능성",
    },
    {
        "condition": "폭염",
        "emoji": "🔥",
        "check": lambda d: d["temp_max"] >= 33,
        "items": ["오이", "애호박", "시금치"],
        "direction": "up",
        "reason": "폭염으로 노지 채소 성장 저하",
    },
    {
        "condition": "강수",
        "emoji": "🌧️",
        "check": lambda d: d["precip_prob"] >= 70 and d["weather_code"] >= 61,
        "items": ["배추", "오이", "애호박"],
        "direction": "up",
        "reason": "강수로 노지 채소 출하 감소 가능성",
    },
    {
        "condition": "태풍·폭우",
        "emoji": "⛈️",
        "check": lambda d: d["precip_prob"] >= 85 and d["weather_code"] >= 80,
        "items": ["갈치", "고등어", "오징어"],
        "direction": "up",
        "reason": "강풍·파고로 어선 출항 제한 가능성",
    },
]


def get_impacts(forecast: list[dict]) -> dict[str, list[WeatherImpact]]:
    """
    forecast의 각 날짜에 대해 영향 룰을 매칭해 반환.
    반환: {date_str: [WeatherImpact, ...]}
    """
    result: dict[str, list[WeatherImpact]] = {}

    for day in forecast:
        impacts = []
        for rule in _RULES:
            if rule["check"](day):
                impacts.append(WeatherImpact(
                    condition=rule["condition"],
                    emoji=rule["emoji"],
                    items=rule["items"],
                    direction=rule["direction"],
                    reason=rule["reason"],
                ))
        if impacts:
            result[day["date"]] = impacts

    return result


def get_week_summary(forecast: list[dict]) -> list[str]:
    """
    7일 예보에서 주목할 날씨 이슈를 요약 문장으로 반환 (최대 2개).
    일일 브리핑 카드용.
    """
    impacts = get_impacts(forecast)
    seen: set[str] = set()
    summaries: list[str] = []

    for day in forecast:
        date_impacts = impacts.get(day["date"], [])
        for impact in date_impacts:
            key = f"{impact.condition}-{','.join(impact.items)}"
            if key not in seen:
                seen.add(key)
                items_str = "·".join(impact.items[:3])
                summaries.append(
                    f"{day['weekday']}요일 {impact.condition} {impact.emoji} → {items_str} 가격 상승 우려"
                )
            if len(summaries) >= 2:
                return summaries

    return summaries
