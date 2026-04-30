"""
Open-Meteo 날씨 클라이언트 (API 키 불필요).
좌표 기반 7일 예보를 조회하고 1시간 인메모리 캐시로 API 호출을 최소화한다.
"""

import logging
from datetime import datetime, timedelta

import httpx

logger = logging.getLogger(__name__)

_URL = "https://api.open-meteo.com/v1/forecast"

# WMO 날씨 코드 → (이모지, 한국어 라벨)
WEATHER_CODE_MAP: dict[int, tuple[str, str]] = {
    0:  ("☀️",  "맑음"),
    1:  ("🌤️", "대체로 맑음"),
    2:  ("⛅",  "구름 많음"),
    3:  ("☁️",  "흐림"),
    45: ("🌫️", "안개"),
    48: ("🌫️", "짙은 안개"),
    51: ("🌦️", "이슬비"),
    53: ("🌦️", "이슬비"),
    55: ("🌧️", "강한 이슬비"),
    61: ("🌧️", "비"),
    63: ("🌧️", "비"),
    65: ("🌧️", "강한 비"),
    71: ("❄️",  "눈"),
    73: ("❄️",  "눈"),
    75: ("❄️",  "강한 눈"),
    80: ("🌦️", "소나기"),
    81: ("🌧️", "소나기"),
    82: ("⛈️",  "강한 소나기"),
    95: ("⛈️",  "뇌우"),
    96: ("⛈️",  "뇌우+우박"),
    99: ("⛈️",  "뇌우+우박"),
}

WEEKDAY_KO = ["월", "화", "수", "목", "금", "토", "일"]

# (lat, lon, past_days) → (data, expiry)
_cache: dict[tuple, tuple[list[dict], datetime]] = {}


async def fetch_forecast(
    lat: float,
    lon: float,
    days: int = 7,
    past_days: int = 0,
) -> list[dict]:
    """
    지정 좌표의 날씨 반환 (past_days 이전 + days 이후). 각 항목:
      date, weekday, temp_max, temp_min, precip_prob, weather_code, emoji, label
    실패 시 이전 캐시 반환 (없으면 빈 리스트).
    """
    cache_key = (round(lat, 2), round(lon, 2), past_days)
    now = datetime.now()

    if cache_key in _cache:
        cached_data, cached_until = _cache[cache_key]
        if now < cached_until:
            return cached_data

    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            resp = await client.get(
                _URL,
                params={
                    "latitude": lat,
                    "longitude": lon,
                    "daily": ",".join([
                        "temperature_2m_max",
                        "temperature_2m_min",
                        "precipitation_probability_max",
                        "weathercode",
                    ]),
                    "timezone": "Asia/Seoul",
                    "forecast_days": days,
                    "past_days": past_days,
                },
            )
            resp.raise_for_status()
            daily = resp.json()["daily"]

        result = []
        for i, date_str in enumerate(daily["time"]):
            code = daily["weathercode"][i] or 0
            emoji, label = WEATHER_CODE_MAP.get(code, ("🌡️", "알 수 없음"))
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            result.append({
                "date": date_str,
                "weekday": WEEKDAY_KO[dt.weekday()],
                "temp_max": daily["temperature_2m_max"][i],
                "temp_min": daily["temperature_2m_min"][i],
                "precip_prob": daily["precipitation_probability_max"][i] or 0,
                "weather_code": code,
                "emoji": emoji,
                "label": label,
            })

        _cache[cache_key] = (result, now + timedelta(hours=1))
        logger.info(f"[Open-Meteo] ({lat},{lon}) past={past_days}+{days}일 수신 완료")
        return result

    except Exception as e:
        logger.warning(f"[Open-Meteo] 날씨 조회 실패: {e}")
        if cache_key in _cache:
            return _cache[cache_key][0]
        return []
