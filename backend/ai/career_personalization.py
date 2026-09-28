from backend.ai import llm_service, prompts


def explain_career_match(
    student_summary: str,
    career_title: str,
    overall_score: float,
    matched_skills: list[str],
    gap_skills: list[str],
) -> str:
    system_prompt, user_prompt = prompts.career_explanation_prompt(
        student_summary, career_title, overall_score, matched_skills, gap_skills
    )
    result = llm_service.generate(system_prompt, user_prompt, max_tokens=220)
    if result:
        return result
    return _fallback_explanation(career_title, overall_score, matched_skills, gap_skills)


def _fallback_explanation(
    career_title: str,
    overall_score: float,
    matched_skills: list[str],
    gap_skills: list[str],
) -> str:
    lines = [f"{career_title} is a {overall_score:.0f}% match based on your current profile."]
    if matched_skills:
        lines.append(f"You already have relevant skills: {', '.join(matched_skills[:5])}.")
    if gap_skills:
        lines.append(f"Focus next on: {', '.join(gap_skills[:5])} to strengthen this fit.")
    else:
        lines.append("You already cover the core required skills for this career.")
    return " ".join(lines)


def summarize_roadmap(career_title: str, item_titles: list[str]) -> str:
    system_prompt, user_prompt = prompts.roadmap_narrative_prompt(career_title, item_titles)
    result = llm_service.generate(system_prompt, user_prompt, max_tokens=180)
    if result:
        return result
    steps = ", ".join(item_titles[:4])
    return f"Your {career_title} roadmap starts with {steps}, building toward full readiness step by step."
