def compute_role_match_score(
    strong_count: int,
    partial_count: int,
    missing_count: int,
    total_jd_skills: int,
) -> float:
    if total_jd_skills <= 0:
        return 0.0
    raw_score = ((strong_count * 1.0) + (partial_count * 0.55) - (missing_count * 0.15)) / total_jd_skills
    return round(max(0.0, min(raw_score, 1.0)) * 100, 2)


def role_match_label(score: float) -> str:
    if score >= 80:
        return "strong_fit"
    if score >= 60:
        return "good_fit"
    if score >= 40:
        return "partial_fit"
    return "low_fit"
