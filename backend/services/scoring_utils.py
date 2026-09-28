from backend.database.models.enums import ProficiencyLevel, SkillImportance

PROFICIENCY_RANK: dict[ProficiencyLevel, int] = {
    ProficiencyLevel.BEGINNER: 1,
    ProficiencyLevel.INTERMEDIATE: 2,
    ProficiencyLevel.ADVANCED: 3,
    ProficiencyLevel.EXPERT: 4,
}

IMPORTANCE_WEIGHT: dict[SkillImportance, float] = {
    SkillImportance.ESSENTIAL: 4.0,
    SkillImportance.IMPORTANT: 3.0,
    SkillImportance.USEFUL: 2.0,
    SkillImportance.OPTIONAL: 1.0,
}


def proficiency_rank(level: ProficiencyLevel) -> int:
    return PROFICIENCY_RANK[level]


def meets_minimum(student_level: ProficiencyLevel, minimum_level: ProficiencyLevel) -> bool:
    return proficiency_rank(student_level) >= proficiency_rank(minimum_level)
