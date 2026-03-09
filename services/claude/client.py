"""
Claude API client for team agents. Uses Anthropic Messages API with system + user prompt.
"""
import os
from anthropic import Anthropic


DEFAULT_MODEL = os.getenv("CLAUDE_AGENT_MODEL", "claude-sonnet-4-20250514")
MAX_TOKENS = int(os.getenv("CLAUDE_AGENT_MAX_TOKENS", "4096"))


def get_client():
    key = os.getenv("ANTHROPIC_API_KEY")
    if not key:
        return None
    return Anthropic(api_key=key)


def complete(system_prompt: str, user_prompt: str, model: str | None = None) -> str:
    """
    Send system + user prompt to Claude, return assistant text.
    Returns empty string if ANTHROPIC_API_KEY is not set or the API call fails.
    """
    client = get_client()
    if not client:
        return ""

    model = model or DEFAULT_MODEL
    try:
        message = client.messages.create(
            model=model,
            max_tokens=MAX_TOKENS,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )
        if message.content and len(message.content) > 0:
            block = message.content[0]
            if hasattr(block, "text"):
                return block.text
            if isinstance(block, dict) and "text" in block:
                return block["text"]
        return ""
    except Exception:
        raise
