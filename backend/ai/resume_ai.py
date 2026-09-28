from backend.ai import llm_service, prompts

WEAK_VERBS = ["made", "did", "worked on", "helped with", "responsible for", "was involved in"]


def improve_resume(resume_text: str, target_career: str | None = None) -> str:
    system_prompt, user_prompt = prompts.resume_improvement_prompt(resume_text, target_career)
    result = llm_service.generate(system_prompt, user_prompt, max_tokens=700)
    if result:
        return result
    return _fallback_review(resume_text)


def _fallback_review(resume_text: str) -> str:
    """Deterministic heuristic review used when no LLM is configured."""
    text_lower = resume_text.lower()
    weaknesses = []

    if not any(char.isdigit() for char in resume_text):
        weaknesses.append("No measurable achievements found (add numbers: %, counts, time saved).")
    for verb in WEAK_VERBS:
        if verb in text_lower:
            weaknesses.append(f"Weak phrasing detected: \"{verb}\" — replace with a strong action verb and outcome.")
            break
    if "project" not in text_lower:
        weaknesses.append("No projects section detected — add 1-2 project bullet points with impact.")
    if len(resume_text.split()) < 150:
        weaknesses.append("Resume content looks short — add more detail on responsibilities and outcomes.")
    if not weaknesses:
        weaknesses.append("No major issues detected by the heuristic reviewer.")

    lines = ["**Weaknesses**"]
    lines += [f"- {w}" for w in weaknesses]
    lines.append("")
    lines.append("**Improved bullet points**")
    lines.append(
        "- Rewrite vague statements using the pattern: "
        "\"[Action verb] + [what you built/did] + [measurable outcome]\"."
    )
    lines.append(
        "- Example: \"Made a machine learning project\" → "
        "\"Developed a machine learning model to predict X using Y, achieving Z accuracy.\""
    )
    return "\n".join(lines)
