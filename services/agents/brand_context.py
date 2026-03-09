"""
Load project brand kit (e.g. JSX) for agents that must stick to brand guidelines.
"""
import os


def _project_root() -> str:
    return os.getenv("AGLANCER_PROJECT_ROOT", "/app")


def load_brand_kit(max_chars: int = 30000) -> str | None:
    """
    Load brand kit content from the configured path (default: docs/brand/brandkit.jsx).
    Returns the file content (truncated if over max_chars) or None if file is missing.
    Set AGLANCER_BRAND_KIT_PATH to a path relative to AGLANCER_PROJECT_ROOT to override.
    """
    root = _project_root()
    rel = os.getenv("AGLANCER_BRAND_KIT_PATH", "docs/brand/brandkit.jsx").lstrip("/")
    path = os.path.join(root, rel)
    if not os.path.isfile(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        if len(content) > max_chars:
            content = content[:max_chars] + "\n\n[... truncated for context limit ...]"
        return content.strip()
    except Exception:
        return None


# Agent IDs that should receive brand kit context when generating output.
BRAND_AWARE_AGENTS = frozenset({"brand_strategist", "ux_ui", "growth_marketing"})
