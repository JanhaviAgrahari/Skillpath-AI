from math import ceil

from app.schemas.common import PlanIntensity


INTENSITY_MULTIPLIERS = {
    PlanIntensity.GENTLE: 0.8,
    PlanIntensity.STANDARD: 1.0,
    PlanIntensity.INTENSIVE: 1.25,
}


def adjusted_hours_per_week(hours_per_week: int, intensity: PlanIntensity) -> int:
    adjusted = hours_per_week * INTENSITY_MULTIPLIERS[intensity]
    return max(1, int(round(adjusted)))


def section_hours(base_hours: int, intensity: PlanIntensity) -> int:
    adjusted = base_hours * INTENSITY_MULTIPLIERS[intensity]
    return max(1, int(ceil(adjusted)))


def difficulty_weight_from_score(score: float | None) -> int:
    if score is None:
        return 3
    if score >= 7.5:
        return 1
    if score >= 5.5:
        return 2
    if score >= 3.0:
        return 3
    return 4
