import re


def extract_skills_from_text(text: str, known_skill_names: list[str]) -> list[str]:
    """Deterministic keyword matching against the Skill catalog.

    Word-boundary, case-insensitive matching keeps this precise and avoids the
    false positives a naive substring search would produce (e.g. "R" matching
    inside "Framework"). Longer skill names are matched first so multi-word
    skills like "Machine Learning" aren't shadowed by a partial match like
    "Machine".
    """
    if not text.strip() or not known_skill_names:
        return []

    lowered_text = text.lower()
    found: list[str] = []
    for skill_name in sorted(known_skill_names, key=len, reverse=True):
        pattern = r"(?<![a-zA-Z0-9+#.])" + re.escape(skill_name.lower()) + r"(?![a-zA-Z0-9+#.])"
        if re.search(pattern, lowered_text):
            found.append(skill_name)
    return found


def extract_email(text: str) -> str | None:
    match = re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", text)
    return match.group(0) if match else None


def extract_years_of_experience(text: str) -> float | None:
    match = re.search(r"(\d+(?:\.\d+)?)\s*\+?\s*years?\s+(?:of\s+)?experience", text.lower())
    if match:
        return float(match.group(1))
    return None
