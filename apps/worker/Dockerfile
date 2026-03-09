FROM python:3.11-slim

WORKDIR /app

# Install curl + bash for Claude Code install script, then install Claude Code CLI (Option B: CLI in container)
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates bash \
  && curl -fsSL https://claude.ai/install.sh | bash -s stable \
  && rm -rf /var/lib/apt/lists/*

# Claude Code installs to ~/.local/bin; when running as root that is /root/.local/bin
ENV PATH="/root/.local/bin:${PATH}"

COPY apps/worker/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY apps/worker/app /app/app
COPY services /app/services
COPY config /app/config
COPY .claude /app/.claude
COPY docs /app/docs

ENV PYTHONPATH=/app
ENV AGLANCER_PROJECT_ROOT=/app

# Auth: set CLAUDE_CODE_OAUTH_TOKEN in .env (generate with `claude setup-token` on a machine with a browser)
# Optional: skip onboarding in headless
ENV CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1

CMD ["python", "-u", "app/main.py"]
