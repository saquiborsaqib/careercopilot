"""Provider-neutral, OpenAI-compatible LLM client.

Configured entirely through environment variables (LLM_PROVIDER, LLM_API_KEY,
LLM_BASE_URL, LLM_MODEL) so any OpenAI-compatible endpoint works (OpenAI,
Azure OpenAI, local vLLM/Ollama gateways, etc.). When no API key is
configured, or the call fails for any reason, `generate` returns None and
callers fall back to deterministic, template-based text -- the app must
never hard-fail because an LLM is unavailable.
"""

from __future__ import annotations

import logging

import httpx

from backend.core.config import settings

logger = logging.getLogger(__name__)


def is_available() -> bool:
    return settings.llm_enabled


def generate(
    system_prompt: str,
    user_prompt: str,
    max_tokens: int = 600,
    temperature: float = 0.6,
) -> str | None:
    """Call the configured chat-completions endpoint. Returns None on any failure."""
    if not settings.llm_enabled:
        return None

    url = f"{settings.llm_base_url.rstrip('/')}/chat/completions"
    payload = {
        "model": settings.llm_model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    headers = {
        "Authorization": f"Bearer {settings.llm_api_key}",
        "Content-Type": "application/json",
    }

    try:
        response = httpx.post(url, json=payload, headers=headers, timeout=settings.llm_timeout_seconds)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()
    except Exception:
        logger.warning("LLM call failed; falling back to template output", exc_info=True)
        return None
