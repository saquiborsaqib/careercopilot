import json
import random

from backend.ai import llm_service, prompts

_FALLBACK_QUESTION_BANK: dict[str, list[str]] = {
    "general": [
        "Tell me about yourself and why you're interested in this field.",
        "Describe a challenging problem you solved recently and how you approached it.",
        "What are your greatest strengths relevant to this role?",
        "Where do you see yourself professionally in three years?",
    ],
    "technical": [
        "Explain the difference between supervised and unsupervised learning.",
        "What is the time complexity of binary search, and why?",
        "How would you design a database schema for a simple e-commerce system?",
        "Explain how a REST API differs from a GraphQL API.",
    ],
    "hr": [
        "Why do you want to work for this type of organization?",
        "Describe a time you disagreed with a teammate. How did you resolve it?",
        "How do you prioritize tasks when you have multiple deadlines?",
        "What motivates you to do your best work?",
    ],
    "behavioral": [
        "Tell me about a time you failed at something and what you learned.",
        "Describe a situation where you had to learn a new skill quickly.",
        "Give an example of when you showed leadership without being asked to.",
        "Describe how you handle receiving critical feedback.",
    ],
}


def generate_question(career_title: str, session_type: str, asked_so_far: list[str]) -> str:
    system_prompt, user_prompt = prompts.interview_question_prompt(career_title, session_type, asked_so_far)
    result = llm_service.generate(system_prompt, user_prompt, max_tokens=120)
    if result:
        return result.strip().strip('"')
    bank = _FALLBACK_QUESTION_BANK.get(session_type, _FALLBACK_QUESTION_BANK["general"])
    remaining = [q for q in bank if q not in asked_so_far]
    if not remaining:
        remaining = bank
    return random.choice(remaining)


def evaluate_answer(question: str, answer: str, career_title: str) -> dict:
    system_prompt, user_prompt = prompts.interview_feedback_prompt(question, answer, career_title)
    result = llm_service.generate(system_prompt, user_prompt, max_tokens=350)
    if result:
        parsed = _parse_feedback_json(result)
        if parsed is not None:
            return parsed
    return _fallback_evaluation(answer)


def _parse_feedback_json(raw: str) -> dict | None:
    try:
        start = raw.index("{")
        end = raw.rindex("}") + 1
        data = json.loads(raw[start:end])
        score = max(0, min(100, int(data.get("score", 0))))
        strengths = list(data.get("strengths", []))[:5]
        improvements = list(data.get("improvements", []))[:5]
        return {"score": score, "strengths": strengths, "improvements": improvements}
    except (ValueError, KeyError, TypeError):
        return None


def _fallback_evaluation(answer: str) -> dict:
    """Deterministic heuristic scoring used when no LLM is configured."""
    word_count = len(answer.split())
    score = min(100, max(10, word_count * 3))
    strengths = []
    improvements = []
    if word_count >= 40:
        strengths.append("Answer is reasonably detailed.")
    else:
        improvements.append("Add more specific detail and examples to strengthen your answer.")
    if any(keyword in answer.lower() for keyword in ["example", "for instance", "e.g."]):
        strengths.append("Good use of a concrete example.")
    else:
        improvements.append("Include a concrete example to illustrate your point.")
    if not strengths:
        strengths.append("Attempted the question with a relevant response.")
    return {"score": score, "strengths": strengths, "improvements": improvements}


def format_feedback_text(evaluation: dict) -> str:
    lines = [f"Score: {evaluation['score']}/100"]
    if evaluation.get("strengths"):
        lines.append("Strengths:")
        lines += [f"  + {s}" for s in evaluation["strengths"]]
    if evaluation.get("improvements"):
        lines.append("Improve:")
        lines += [f"  -> {i}" for i in evaluation["improvements"]]
    return "\n".join(lines)
