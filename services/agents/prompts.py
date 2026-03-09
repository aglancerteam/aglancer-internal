"""
Load agent system prompts from .claude/agents/*.md (Claude Code Teams style).
"""
import os


def _project_root() -> str:
    return os.getenv("AGLANCER_PROJECT_ROOT", "/app")


def load_agent_prompt(prompt_file: str) -> str:
    """
    Load prompt content from repo file (e.g. .claude/agents/atlas.md).
    Returns empty string if file is missing (caller can fall back to template).
    """
    root = _project_root()
    path = os.path.join(root, prompt_file.lstrip("/"))
    if not os.path.isfile(path):
        return ""
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()
