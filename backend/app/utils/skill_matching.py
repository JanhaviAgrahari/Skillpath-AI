from difflib import SequenceMatcher

from app.schemas.analysis import SkillGapItem, SkillItem
from app.schemas.common import MatchStrength


def similarity_score(left: str, right: str) -> float:
    return round(SequenceMatcher(None, left.lower(), right.lower()).ratio(), 2)


def build_gap_item(
    skill: SkillItem,
    match_strength: MatchStrength,
    score: float,
    reason: str,
    mapped_to: str | None = None,
) -> SkillGapItem:
    return SkillGapItem(
        skill=skill,
        match_strength=match_strength,
        score=score,
        mapped_to=mapped_to,
        reason=reason,
    )
