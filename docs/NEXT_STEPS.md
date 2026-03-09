# What to do next (after adding Supabase)

## 1. Create all tables in Supabase

If you haven’t already, run the full schema so every table the app expects exists:

1. Open [Supabase Dashboard](https://supabase.com/dashboard) → your project.
2. Go to **SQL Editor** → **New query**.
3. Paste the contents of `docs/schema_supabase_full.sql`.
4. Run it.

That creates: `tasks`, `task_events`, `jobs`, `approvals`, `agent_outputs`, `mailbox`.

## 2. Confirm environment

Your `.env` already has:

- `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` ✓  
- `LINEAR_*`, `SLACK_*`, `REDIS_*` as needed ✓  

For **local runs** (no Docker), set Redis to your host:

- `REDIS_HOST=localhost` (and ensure Redis is running, e.g. `redis-server` or Docker).

## 3. Run the app

**Option A – Docker (recommended)**

From the repo root:

```bash
cd aglancer-internal
docker compose -f infra/docker-compose.yml up --build
```

- Orchestrator: http://localhost:8000  
- Worker runs in the background and processes jobs from Redis.

**Option B – Local (orchestrator + worker + Redis)**

Terminal 1 – Redis:

```bash
redis-server
```

Terminal 2 – Orchestrator (from repo root so `config` and `services` are on the path):

```bash
cd aglancer-internal
REDIS_HOST=localhost python -m uvicorn apps.orchestrator.app.main:app --reload --host 0.0.0.0 --port 8000
```

Terminal 3 – Worker:

```bash
cd aglancer-internal
REDIS_HOST=localhost python apps/worker/app/main.py
```

## 4. Quick checks

- **Health**: `curl http://localhost:8000/health` → `{"status":"ok","service":"aglancer-orchestrator"}`.
- **Atlas daily summary**: `curl http://localhost:8000/atlas/daily-summary` (uses Supabase + team context; may post to Slack if configured).
- **Linear**: When you have a webhook pointing at `/webhooks/linear`, moving an issue to e.g. “Ready for Spec” will create a task and enqueue a job for Nova; the worker will run the agent and write to `agent_outputs`.

## 5. Optional next steps

- **Linear webhook**: In Linear → Settings → API → Webhooks, add a webhook URL: `https://<your-orchestrator-host>/webhooks/linear`, and set the secret to `LINEAR_WEBHOOK_SECRET`.
- **LLM agents**: Right now agents return templates. To use real Claude/LLM calls, wire `services.agents.runner` to your API and pass `team_context` (inbox, task list) into the prompt; add tools like `SendMessage`, `ClaimTask`, `CompleteTask` that call the mailbox and task APIs.
- **Plan approval**: For “plan before implement”, have a teammate send a plan via `mailbox.send_message(..., to_agent_id="chief_of_staff")` and have Atlas approve/reject before the worker marks the task done.
