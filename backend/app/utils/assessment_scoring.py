from app.schemas.common import ProficiencyLevel


def proficiency_from_score(score: float) -> ProficiencyLevel:
    if score >= 8.5:
        return ProficiencyLevel.EXPERT
    if score >= 7.0:
        return ProficiencyLevel.ADVANCED
    if score >= 5.0:
        return ProficiencyLevel.INTERMEDIATE
    if score >= 2.5:
        return ProficiencyLevel.BEGINNER
    return ProficiencyLevel.UNKNOWN
