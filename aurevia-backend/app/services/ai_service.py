"""
Wraps all calls to the external AI provider.
Keeping this in one place means:
- one spot to swap providers later
- one spot to add retry/timeout/rate-limit handling
- one spot to enforce safety guardrails before a reply reaches the user
"""
import httpx

from app.core.config import settings

# Very small, non-exhaustive keyword list used ONLY to decide whether to
# prepend crisis resources to a reply. This is not a clinical detector —
# treat it as a first line of defense, not a substitute for real safety
# infrastructure (human review, proper classifiers, etc.) before launch.
CRISIS_KEYWORDS = [
    "suicide", "kill myself", "want to die", "end my life", "self harm", "self-harm",
]

CRISIS_RESOURCE_MESSAGE = (
    "I want to pause here — it sounds like you might be going through something really "
    "heavy right now. If you're in immediate danger, please contact your local emergency "
    "number. You can also reach a crisis line for support, such as 988 (Suicide & Crisis "
    "Lifeline, US) or a local equivalent. You don't have to go through this alone."
)

SYSTEM_PROMPT = (
    "You are a supportive, empathetic mental wellness companion inside the Aurevia app. "
    "You are not a licensed therapist and must not diagnose conditions or prescribe "
    "treatment. Respond with warmth and validation, encourage healthy coping, and "
    "encourage the user to speak with a mental health professional for anything serious. "
    "If the user expresses thoughts of self-harm or suicide, respond with care and "
    "encourage them to seek immediate help."
)


class AIServiceError(Exception):
    pass


def _contains_crisis_language(text: str) -> bool:
    lowered = text.lower()
    return any(keyword in lowered for keyword in CRISIS_KEYWORDS)


async def get_ai_reply(user_message: str, history: list[dict] | None = None) -> tuple[str, bool]:
    """
    Calls the AI provider and returns (reply_text, flagged_for_safety).

    `history` is a list of {"role": "user"|"assistant", "content": str} dicts
    representing prior turns in the conversation, oldest first.
    """
    flagged = _contains_crisis_language(user_message)

    messages = (history or []) + [{"role": "user", "content": user_message}]

    payload = {
        "model": settings.ai_model,
        "max_tokens": 1000,
        "system": SYSTEM_PROMPT,
        "messages": messages,
    }
    headers = {
        "x-api-key": settings.ai_api_key,
        "content-type": "application/json",
        "anthropic-version": "2023-06-01",
    }

    try:
        async with httpx.AsyncClient(timeout=settings.ai_request_timeout_seconds) as client:
            response = await client.post(settings.ai_api_url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
    except httpx.TimeoutException as exc:
        raise AIServiceError("The AI service took too long to respond. Please try again.") from exc
    except httpx.HTTPStatusError as exc:
        raise AIServiceError(f"AI service returned an error: {exc.response.status_code}") from exc
    except httpx.HTTPError as exc:
        raise AIServiceError("Could not reach the AI service.") from exc

    reply_text = "".join(
        block.get("text", "") for block in data.get("content", []) if block.get("type") == "text"
    ).strip()

    if not reply_text:
        raise AIServiceError("AI service returned an empty response.")

    if flagged:
        reply_text = f"{CRISIS_RESOURCE_MESSAGE}\n\n{reply_text}"

    return reply_text, flagged
