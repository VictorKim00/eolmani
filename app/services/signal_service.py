"""
신호등 판단 서비스.
가중치: 평년 50% + 1개월 30% + 1주일 20%
평년 데이터 없을 때는 1개월 75% + 1주일 25%로 정규화.
"""


def compute_signal(change_avg: float | None, change_30d: float | None, change_7d: float | None) -> str:
    """
    종합 점수 ≤ -5% → 'green' (살 때)
              -5%~+5% → 'yellow' (보통)
              ≥ +5% → 'red' (비쌈)
    """
    scores: list[float] = []
    weights: list[float] = []

    if change_avg is not None:
        scores.append(change_avg)
        weights.append(0.50)
    if change_30d is not None:
        scores.append(change_30d)
        weights.append(0.30)
    if change_7d is not None:
        scores.append(change_7d)
        weights.append(0.20)

    if not scores:
        return "yellow"

    total_weight = sum(weights)
    weighted = sum(s * w for s, w in zip(scores, weights)) / total_weight

    if weighted <= -5:
        return "green"
    if weighted >= 5:
        return "red"
    return "yellow"


SIGNAL_LABEL = {"green": "살 때", "yellow": "보통", "red": "비쌈"}
SIGNAL_EMOJI = {"green": "🟢", "yellow": "🟡", "red": "🔴"}


def get_action(
    signal: str,
    change_7d: float | None,
    change_30d: float | None,
    month_stats: dict | None,
) -> dict:
    """
    신호등 + 변동률 + 월별 통계를 종합해 구매 행동 추천 반환.
    반환: {type, title, reasons}
      type: "buy_now" | "buy_soon" | "neutral" | "wait"
    """
    reasons: list[str] = []

    if month_stats:
        pct = month_stats["pct_diff"]
        if pct <= -8:
            reasons.append(f"이번 달은 연평균 대비 {pct:+.0f}% — 역사적으로 저렴한 시기")
        elif pct <= -3:
            reasons.append(f"이번 달은 연평균 대비 {pct:+.0f}% — 평년보다 저렴한 편")
        elif pct >= 8:
            reasons.append(f"이번 달은 연평균 대비 {pct:+.0f}% — 역사적으로 비싼 시기")
        elif pct >= 3:
            reasons.append(f"이번 달은 연평균 대비 {pct:+.0f}% — 평년보다 비싼 편")

    if change_7d is not None:
        if change_7d <= -5:
            reasons.append(f"1주일 전보다 {change_7d:.1f}% 하락 중")
        elif change_7d >= 5:
            reasons.append(f"1주일 전보다 {change_7d:.1f}% 상승 중")

    if change_30d is not None:
        if change_30d <= -8:
            reasons.append(f"30일 전보다 {change_30d:.1f}% 하락")
        elif change_30d >= 8:
            reasons.append(f"30일 전보다 {change_30d:.1f}% 상승")

    if signal == "green":
        falling = change_7d is not None and change_7d < -3
        if falling:
            return {"type": "buy_now", "title": "지금 사두기 좋은 시기입니다", "reasons": reasons}
        return {"type": "buy_soon", "title": "현재 저렴한 편 — 구매 고려해 보세요", "reasons": reasons}

    if signal == "red":
        falling = change_7d is not None and change_7d < -3
        if falling:
            return {"type": "wait", "title": "비싸지만 하락 중 — 1~2주 더 지켜보세요", "reasons": reasons}
        return {"type": "wait", "title": "현재 비싼 시기 — 급하지 않으면 미루세요", "reasons": reasons}

    # yellow
    if not reasons:
        reasons.append("평년 수준의 가격대")
    return {"type": "neutral", "title": "평년 수준 — 시급하지 않으면 관망 가능", "reasons": reasons}
