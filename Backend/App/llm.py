import anthropic

from app.config import settings

_client: anthropic.Anthropic | None = None


def complete(system: str, user: str, max_tokens: int = 1024) -> str:
    global _client
    if _client is None:
        if not settings.anthropic_api_key:
            raise RuntimeError("ANTHROPIC_API_KEY is not set. Copy .env.example to .env.")
        _client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    resp = _client.messages.create(
        model=settings.llm_model,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    return "".join(b.text for b in resp.content if b.type == "text")
