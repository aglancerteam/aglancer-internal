# AGlancer deployment (VPS)

## Current setup

- **VPS** hosting **aglancer.tech**
- **Portainer**: http://api.aglancer.tech/ (container port 9000)
- **Stack** (`infra`): `aglancer_orchestrator`, `aglancer_worker`, `aglancer_redis` (all running)
- **Orchestrator API**: https://api.aglancer.tech (reverse proxy routes to orchestrator; same setup as before)

| Service        | Container              | Port  | Notes                         |
|----------------|------------------------|-------|-------------------------------|
| Portainer      | portainer              | 9000  | api.aglancer.tech             |
| Orchestrator   | aglancer_orchestrator  | 8000  | api.aglancer.tech (by path)   |
| Worker         | aglancer_worker        | —     | Consumes Redis queue           |
| Redis          | aglancer_redis         | 6379  | Internal                       |

## URLs

- **Linear webhook**: https://api.aglancer.tech/webhooks/linear
- **Health**: https://api.aglancer.tech/health
- **Atlas daily summary**: https://api.aglancer.tech/atlas/daily-summary
- **Pending approvals**: https://api.aglancer.tech/approvals/pending
- **Recent jobs**: https://api.aglancer.tech/jobs/recent

## Cron jobs

These endpoints are called on a schedule (e.g. from the VPS crontab or an external scheduler) to keep Slack and ops in sync.

| Purpose              | URL | Suggested schedule | Notes |
|----------------------|-----|--------------------|--------|
| Atlas daily summary | `GET https://api.aglancer.tech/atlas/daily-summary` | Daily (e.g. 9:00) | Posts summary to `SLACK_CHANNEL_STANDUP` |
| Pending jobs/approvals | `GET https://api.aglancer.tech/approvals/pending` and/or `GET https://api.aglancer.tech/jobs/recent` | As needed (e.g. every 15–60 min) | Use to remind about pending approvals or recent job status |

**Example crontab (VPS):**

```cron
# Atlas daily summary (e.g. 9:00 AM daily)
0 9 * * * curl -sS https://api.aglancer.tech/atlas/daily-summary > /dev/null

# Pending approvals / jobs check (e.g. every 30 min)
*/30 * * * * curl -sS https://api.aglancer.tech/approvals/pending > /dev/null
```

Adjust URLs if you use auth or different endpoints. If your scheduler runs inside the network, you can use `http://aglancer_orchestrator:8000/...` instead of the public URL.

## Rebuild and restart (after code changes)

From the repo on the VPS:

```bash
cd ~/aglancer-internal/infra
docker compose up -d --build orchestrator
```

That rebuilds the orchestrator image and restarts only the orchestrator container (Redis stays up; worker unchanged). To rebuild and restart **worker** as well:

```bash
docker compose up -d --build orchestrator worker
```

## Testing the flow with a simple issue

### Option A: Create issue via API and run the pipeline (recommended)

One curl creates the Linear issue and kicks off Nova. The issue is real, so Nova’s spec is written to its description.

**1. Set your Linear team id (once)**

Get your team UUID (e.g. from Linear → Settings → API, or run):

```bash
curl -s -X POST https://api.linear.app/graphql \
  -H "Authorization: YOUR_LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query":"query { teams(first: 5) { nodes { id name } } }"}' | jq .
```

Add to `.env` on the VPS:

```env
LINEAR_TEAM_ID=your-team-uuid-here
```

**2. Create issue and run pipeline**

```bash
curl -X POST https://api.aglancer.tech/test/create-issue \
  -H "Content-Type: application/json" \
  -d '{"title": "Add a simple test button to the dashboard"}'
```

The API will create the issue in Linear (in “Ready for Spec”), then process it: task + job for Nova, Slack updates, and Nova’s spec (including deliverable) written to the **issue description** in Linear.

Optional: pass a different team or title:

```bash
curl -X POST https://api.aglancer.tech/test/create-issue \
  -H "Content-Type: application/json" \
  -d '{"title": "Your issue title", "team_id": "optional-team-uuid"}'
```

---

### Option B: Simulate the webhook (no issue creation)

Send a POST that looks like Linear’s webhook. Use a **real** issue UUID in `data.id` if you want Linear updated; otherwise Slack and Supabase still get the flow.

```bash
curl -X POST https://api.aglancer.tech/webhooks/linear \
  -H "Content-Type: application/json" \
  -d '{"action":"create","data":{"id":"test-issue-001","title":"Add a simple test button","state":"Ready for Spec"}}'
```

With a fake id (`test-issue-001`), nothing happens in Linear. With a real issue UUID, Nova’s spec is written to that issue’s description.

**2. Get a real issue UUID so Linear is updated**

**Easiest:** In Linear, create the issue, set status to **Ready for Spec**, and leave the webhook configured. Linear will send the webhook with the **real** issue id, and Nova’s spec will be written to that issue’s description automatically.

**Or** trigger manually with a real UUID:

- In **Linear**, create an issue and set status to **Ready for Spec**.
- Get its UUID: **Linear → Settings → API** (or run a GraphQL query such as `query { issues(first: 5) { nodes { id identifier title } } }` with your `LINEAR_API_KEY`). Use the `id` (UUID) of the issue.
- Send the webhook with that UUID:

  ```bash
  curl -X POST https://api.aglancer.tech/webhooks/linear \
    -H "Content-Type: application/json" \
    -d '{"action":"create","data":{"id":"PASTE-UUID-HERE","title":"Add a simple test button to the dashboard","state":"Ready for Spec"}}'
  ```

  Then Nova’s spec (including deliverable) is written to that issue’s **description** in Linear.

**3. Check the result**

- **Slack**: “Task routed to Nova (product_manager)” and “Nova completed work” with content.
- **Supabase**: New row in `tasks`, new row in `jobs` (status completed), new row in `agent_outputs`.
- **Linear** (only when you used a real issue UUID): Issue description updated with the spec.
- If Linear still doesn’t update: check worker logs for `Linear issueUpdate errors:` or `Linear: failed to update issue description` (e.g. `docker logs aglancer_worker`).

**4. Optional: test more states**

Same endpoint, different `state` and (for a real ticket) the same `data.id`:

- `"state": "Ready to Build"` → routes to Forge; worker posts deliverable confirmation as a comment.
- `"state": "Review"` → routes to Sentinel; worker posts QA review as a comment.
- `"state": "Done"` → routes to Scribe; updates docs.

### Option B: Use Linear for real

1. In **Linear**, create an issue (e.g. “Add a simple test button to the dashboard”).
2. Set its status to **Ready for Spec**.
3. If the webhook is configured (URL + secret), Linear will POST to `https://api.aglancer.tech/webhooks/linear` and the same flow runs.
4. Optionally copy the issue’s UUID and run the `curl` above with that `id` to re-trigger or test without changing the issue again.

---

## Linear webhook (reference)

1. **Linear** → **Settings** → **API** → **Webhooks**
2. **URL**: `https://api.aglancer.tech/webhooks/linear`
3. **Secret**: same as `LINEAR_WEBHOOK_SECRET` in `.env`
4. Subscribe to the issue events you need (e.g. create, update).

## Environment on the VPS

Containers use `env_file: ../.env`. Ensure the VPS `.env` (or the one mounted into the stack) has:

- `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`
- `LINEAR_WEBHOOK_SECRET` (matches Linear webhook secret)
- `SLACK_*` if you use Slack
- `REDIS_HOST=redis` (Docker service name; default in compose is correct)
- `LINEAR_API_KEY` – Used by the worker (description + comments) and by the orchestrator for **create issue** (`/test/create-issue`). Ensure the key can **create issues**, **create comments**, and **update issues**.
- `LINEAR_TEAM_ID` – (Optional but recommended for `/test/create-issue`.) Your Linear team UUID; if unset, the first team returned by the API is used.
- **Claude Code CLI in worker (Option B)** – No API key needed. The worker image installs the Claude Code CLI and uses your **Claude Code subscription** (e.g. Max) via a long-lived OAuth token. See [Option B: Worker with Claude Code CLI](#option-b-worker-with-claude-code-cli) below for setup.
- **`ANTHROPIC_API_KEY`** – Optional fallback when the CLI is not available (e.g. worker in Docker without `claude` installed). When set, agents use the API instead of templates.

Optional for Claude Code CLI:

- `USE_CLAUDE_CODE_CLI=1` – Force use of CLI when both CLI and API key exist (default: prefer CLI if in PATH).
- `AGLANCER_PROJECT_ROOT` – Project root for headless runs (default `/app` in Docker; set to repo path if worker runs on host).
- `AGLANCER_BRAND_KIT_PATH` – Optional. Path to brand kit file relative to project root (default `docs/brand/brandkit.jsx`). When set, Meridian, Luma, and Pulse receive this content and must stick to it.
- `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` – Set by the runner so headless runs are teams-aware.
- `CLAUDE_HEADLESS_TIMEOUT` – Timeout in seconds for each `claude -p` run (default 300).

Optional for API fallback:

- `CLAUDE_AGENT_MODEL`, `CLAUDE_AGENT_MAX_TOKENS`

## Option B: Worker with Claude Code CLI

The worker Docker image includes the Claude Code CLI. The worker uses headless mode (`claude -p "..."`) for each job and consumes your Claude Code (Max) subscription—no `ANTHROPIC_API_KEY` required.

### 1. Generate a long-lived OAuth token

On a machine where you can open a browser (your laptop, not the VPS):

1. Install [Claude Code](https://code.claude.com) if needed, then run:
   ```bash
   claude setup-token
   ```
2. Complete the browser flow. You get a token valid for about 1 year (Claude Pro/Max).
3. Copy the token (it looks like `sk-ant-oat01-...`).

### 2. Add the token to `.env` on the VPS

In `aglancer-internal/.env` on the VPS, add:

```env
CLAUDE_CODE_OAUTH_TOKEN=sk-ant-oat01-your-token-here
```

Do **not** commit this file. The stack already loads `.env` via `env_file: ../.env`, so the worker container will receive the variable.

### 3. Rebuild and restart the worker

From the repo on the VPS:

```bash
cd ~/aglancer-internal/infra
docker compose up -d --build worker
```

The build installs the Claude Code CLI inside the worker image (via `https://claude.ai/install.sh`). The first build may take a couple of minutes.

### 4. Verify

- Move a Linear issue to a state that triggers an agent (e.g. **Ready for Spec**). The worker should process the job and you should see Slack messages with **Claude-generated** content (not the old templates).
- To confirm the CLI is present in the container:  
  `docker exec aglancer_worker claude --version`

If the installer script ever prompts for input and the build hangs, you can switch to installing the CLI via npm (add Node to the image and `npm install -g @anthropic-ai/claude-code`) or run the worker on the host with Claude Code installed there.

**Nova only writes a template to Linear (no real spec):** The runner falls back to the template when Claude CLI or API is not used. Check worker logs for `WARNING: product_manager used template` and the message that follows (CLAUDE_CODE_OAUTH_TOKEN, PATH for `claude`, or ANTHROPIC_API_KEY). The Linear description will also start with *[Spec from template — Claude did not run...]* when that happens. Fix: ensure `CLAUDE_CODE_OAUTH_TOKEN` is set in the worker env and `claude --version` works in the container; or set `ANTHROPIC_API_KEY` as fallback.

## Quick reference

| What              | URL / value |
|-------------------|-------------|
| Portainer         | http://api.aglancer.tech/ |
| Health            | https://api.aglancer.tech/health |
| Linear webhook    | https://api.aglancer.tech/webhooks/linear |
