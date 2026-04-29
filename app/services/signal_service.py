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
