REGIONS: list[tuple[str, str]] = [
    ("",     "전국 평균"),
    ("1101", "서울"),
    ("2100", "부산"),
    ("2200", "대구"),
    ("2300", "인천"),
    ("2401", "광주"),
    ("2501", "대전"),
]

REGION_CODES: set[str] = {code for code, _ in REGIONS}
REGION_LABEL: dict[str, str] = dict(REGIONS)
DEFAULT_REGION: str = ""

# 지역별 대표 좌표 (Open-Meteo 날씨 조회용)
REGION_COORDS: dict[str, tuple[float, float]] = {
    "":     (37.5665, 126.9780),  # 전국 평균 → 서울 기준
    "1101": (37.5665, 126.9780),  # 서울
    "2100": (35.1796, 129.0756),  # 부산
    "2200": (35.8714, 128.6014),  # 대구
    "2300": (37.4563, 126.7052),  # 인천
    "2401": (35.1595, 126.8526),  # 광주
    "2501": (36.3504, 127.3845),  # 대전
}

# 전국 평균 선택 시 날씨 표시 라벨
REGION_WEATHER_LABEL: dict[str, str] = {
    "":     "서울",
    "1101": "서울",
    "2100": "부산",
    "2200": "대구",
    "2300": "인천",
    "2401": "광주",
    "2501": "대전",
}


def normalize_region(value: str | None) -> str:
    """쿼리스트링 → 유효한 region_code. 미지원 값은 전국 평균으로 폴백."""
    if value is None:
        return DEFAULT_REGION
    return value if value in REGION_CODES else DEFAULT_REGION
