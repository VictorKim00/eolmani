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


def normalize_region(value: str | None) -> str:
    """쿼리스트링 → 유효한 region_code. 미지원 값은 전국 평균으로 폴백."""
    if value is None:
        return DEFAULT_REGION
    return value if value in REGION_CODES else DEFAULT_REGION
