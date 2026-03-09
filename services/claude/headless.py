"""
Run agents via Claude Code CLI (headless) using your subscription — no API key.
Uses: claude -p "..." --append-system-prompt "..." --output-format json
"""
import json
import os
import shutil
import subprocess


def _project_root() -> str:
    return os.getenv("AGLANCER_PROJECT_ROOT", "/app")


def is_available() -> bool:
    """True if Claude Code CLI is in PATH and we should use it (no API key needed)."""
    if os.getenv("USE_CLAUDE_CODE_CLI", "").lower() in ("1", "true", "yes"):
        return bool(shutil.which("claude"))
    # Prefer CLI when present so subscription is used
    return bool(shutil.which("claude"))


def complete(system_prompt: str, user_prompt: str) -> str:
    """
    Run Claude Code in headless mode; return the text result.
    Uses your Claude Code subscription (no ANTHROPIC_API_KEY).
    Raises on non-zero exit or missing result.
    """
    claude_path = shutil.which("claude")
    if not claude_path:
        raise RuntimeError("Claude Code CLI not in PATH; install it or set ANTHROPIC_API_KEY")

    root = _project_root()
    env = os.environ.copy()
    # Ensure CLI is on PATH in subprocess (Docker often has minimal PATH)
    claude_bin_dir = os.path.dirname(claude_path)
    path = env.get("PATH", "")
    if claude_bin_dir and claude_bin_dir not in path:
        env["PATH"] = claude_bin_dir + os.pathsep + path
    env["CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS"] = os.getenv("CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS", "1")

    result = subprocess.run(
        [
            claude_path,
            "-p", user_prompt,
            "--append-system-prompt", system_prompt,
            "--output-format", "json",
        ],
        capture_output=True,
        text=True,
        cwd=root,
        env=env,
        timeout=int(os.getenv("CLAUDE_HEADLESS_TIMEOUT", "300")),  # 5 min default
    )

    if result.returncode != 0:
        raise RuntimeError(f"claude exit {result.returncode}: {result.stderr or result.stdout}")

    try:
        out = json.loads(result.stdout)
    except json.JSONDecodeError:
        raise RuntimeError(f"claude output was not JSON: {result.stdout[:500]}")
    text = out.get("result") or out.get("output") or ""
    return text.strip()
