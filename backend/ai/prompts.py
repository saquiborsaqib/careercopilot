"""Prompt templates for the LLM-backed explanation, resume and interview features.

These build the (system_prompt, user_prompt) pairs passed to backend.ai.llm_service.
The LLM is only ever asked to explain, phrase or generate free text around facts
that deterministic Python code has already computed -- it never decides eligibility
or scores on its own.
"""

CAREER_EXPLANATION_SYSTEM = (
    "You are a career guidance assistant for engineering and science students in India. "
    "Explain career recommendations in warm, encouraging, concrete language. "
    "Never invent facts about the student that were not given to you. "
    "Keep responses under 120 words."
)


def career_explanation_prompt(
    student_summary: str,
    career_title: str,
    overall_score: float,
    matched_skills: list[str],
    gap_skills: list[str],
) -> tuple[str, str]:
    user_prompt = (
        f"Student profile: {student_summary}\n"
        f"Recommended career: {career_title}\n"
        f"Computed match score: {overall_score}/100\n"
        f"Skills already matching this career: {', '.join(matched_skills) or 'none yet'}\n"
        f"Skills the student is missing: {', '.join(gap_skills) or 'none'}\n\n"
        "Write a short, encouraging explanation of why this career fits, referencing the "
        "already-matching skills, and briefly note what to focus on next."
    )
    return CAREER_EXPLANATION_SYSTEM, user_prompt


RESUME_IMPROVEMENT_SYSTEM = (
    "You are an expert technical resume coach. You improve resume bullet points to be "
    "specific, quantified and achievement-oriented, without inventing new facts, tools, "
    "numbers or outcomes the student did not provide. If a claim can't be verified from the "
    "input, keep it general rather than fabricating specifics."
)


def resume_improvement_prompt(resume_text: str, target_career: str | None) -> tuple[str, str]:
    career_line = f"Target career: {target_career}\n" if target_career else ""
    user_prompt = (
        f"{career_line}"
        f"Resume text:\n{resume_text[:6000]}\n\n"
        "1. List up to 5 concrete weaknesses (weak verbs, no metrics, missing keywords, etc.).\n"
        "2. Rewrite up to 3 of the weakest bullet points into stronger versions, staying "
        "faithful to what was actually described -- do not invent tools, numbers or scope.\n"
        "Format as concise markdown with 'Weaknesses' and 'Improved bullet points' sections."
    )
    return RESUME_IMPROVEMENT_SYSTEM, user_prompt


INTERVIEW_QUESTION_SYSTEM = (
    "You are a technical interviewer generating one interview question at a time for a "
    "student preparing for a specific career and interview type. Ask a single, clear, "
    "self-contained question with no preamble or numbering."
)


def interview_question_prompt(career_title: str, session_type: str, asked_so_far: list[str]) -> tuple[str, str]:
    history = "\n".join(f"- {q}" for q in asked_so_far) or "None yet"
    user_prompt = (
        f"Career: {career_title}\n"
        f"Interview type: {session_type}\n"
        f"Questions already asked in this session:\n{history}\n\n"
        "Generate the next interview question. Do not repeat a topic already covered."
    )
    return INTERVIEW_QUESTION_SYSTEM, user_prompt


INTERVIEW_FEEDBACK_SYSTEM = (
    "You are a technical interview coach. Score the candidate's answer from 0-100 and give "
    "specific, actionable feedback. Be honest but constructive. "
    'Respond strictly as JSON: {"score": <0-100 integer>, "strengths": ["..."], "improvements": ["..."]}'
)


def interview_feedback_prompt(question: str, answer: str, career_title: str) -> tuple[str, str]:
    user_prompt = (
        f"Career context: {career_title}\n"
        f"Question: {question}\n"
        f"Candidate answer: {answer}\n\n"
        "Evaluate the answer for relevance, completeness, communication and technical "
        "understanding. Respond with the JSON object only."
    )
    return INTERVIEW_FEEDBACK_SYSTEM, user_prompt


ROADMAP_NARRATIVE_SYSTEM = (
    "You are a career coach turning a structured learning roadmap into a short, motivating "
    "narrative summary. Do not change the plan, only explain it. Keep it under 100 words."
)


def roadmap_narrative_prompt(career_title: str, item_titles: list[str]) -> tuple[str, str]:
    items = "\n".join(f"{i + 1}. {t}" for i, t in enumerate(item_titles))
    user_prompt = (
        f"Career: {career_title}\nRoadmap steps in order:\n{items}\n\n"
        "Write a short, encouraging narrative summary of this roadmap."
    )
    return ROADMAP_NARRATIVE_SYSTEM, user_prompt
