import os
from fastapi import FastAPI, Request
from services.slack.client import send_slack_message
from services.memory.tasks import upsert_task, get_task_by_linear_issue_id, insert_task_event
from services.memory.agent_outputs import insert_agent_output
from services.router import get_next_agent
from services.agents.runner import run_agent
from services.team_context import build_team_context
from services.approvals.service import (
    create_approval,
    get_pending_approvals,
    get_pending_approval_for_task,
    resolve_approvals_for_task,
)
from services.memory.jobs import (
    create_job,
    get_recent_jobs,
    has_pending_or_running_job,
    has_recent_job_for_task_agent,
)
from services.queue import enqueue_job
from services.memory.dashboard import (
    get_recent_tasks,
    get_blocked_tasks,
    get_pending_approvals,
    get_failed_jobs,
)
from services.linear.client import (
    get_teams,
    get_workflow_states,
    create_issue as linear_create_issue,
)

app = FastAPI(title="AGlancer Orchestrator")

SLACK_CHANNEL_ALERTS = os.getenv("SLACK_CHANNEL_ALERTS", "")
SLACK_CHANNEL_STANDUP = os.getenv("SLACK_CHANNEL_STANDUP", "")
SLACK_CHANNEL_APPROVALS = os.getenv("SLACK_CHANNEL_APPROVALS", "")


@app.get("/health")
async def health():
    return {"status": "ok", "service": "aglancer-orchestrator"}


@app.get("/slack/test")
async def slack_test():
    if not SLACK_CHANNEL_ALERTS:
        return {"ok": False, "error": "SLACK_CHANNEL_ALERTS is missing"}

    result = await send_slack_message(
        SLACK_CHANNEL_ALERTS,
        "AGlancer orchestrator is online."
    )
    return {"ok": True, "slack": result}


async def _process_linear_payload(payload: dict) -> dict:
    """Shared webhook processing: task, job, Slack. Used by /webhooks/linear and /test/create-issue."""
    action = payload.get("action", "unknown")
    data = payload.get("data", {})

    issue_id = data.get("id", "unknown")
    title = data.get("title", "Untitled")

    state = (
        data.get("state", {}).get("name")
        if isinstance(data.get("state"), dict)
        else data.get("state", "unknown")
    )

    agent = get_next_agent(state)
    agent_id = None
    agent_name = None
    if agent:
        agent_id = agent["agent_id"]
        agent_name = agent["agent_name"]

    upsert_task(issue_id, title, state, agent_id)
    task = get_task_by_linear_issue_id(issue_id)

    if task:
        insert_task_event(task["id"], action, payload)
        if state != "Awaiting Approval":
            resolve_approvals_for_task(task["id"])

    if task and agent_id in [
            "triage",
            "product_manager", "lead_developer", "docs_knowledge", "qa_security",
            "brand_strategist", "architect", "ux_ui", "growth_marketing",
        ]:
        # Avoid duplicate jobs: skip if already pending/running, or any job for this task+agent in last 2 min
        if has_pending_or_running_job(task["id"], agent_id) or has_recent_job_for_task_agent(
            task["id"], agent_id, within_seconds=120
        ):
            pass  # no new job, no Slack (avoids spam when Linear sends many webhooks)
        else:
            job = create_job(
                task_id=task["id"],
                agent_id=agent_id,
                agent_name=agent_name,
                job_type="agent_execution",
                payload={"title": title, "state": state, "issue_id": issue_id},
            )
            enqueue_job({
                "job_id": job["id"],
                "task_id": task["id"],
                "agent_id": agent_id,
                "agent_name": agent_name,
                "payload": {"title": title, "state": state, "issue_id": issue_id},
            })
            if SLACK_CHANNEL_STANDUP:
                await send_slack_message(
                    SLACK_CHANNEL_STANDUP,
                    f"Task routed to {agent_name} ({agent_id})\nIssue: {title}\nState: {state}\nJob ID: {job['id']}",
                )
    elif SLACK_CHANNEL_STANDUP:
        await send_slack_message(
            SLACK_CHANNEL_STANDUP,
            f"Linear event: {action}\nIssue: {title}\nState: {state}",
        )

    if state == "Awaiting Approval" and task and not get_pending_approval_for_task(task["id"]):
        create_approval(task_id=task["id"], title=title, requested_by_agent=agent_id)
        if SLACK_CHANNEL_APPROVALS:
            await send_slack_message(
                SLACK_CHANNEL_APPROVALS,
                f"Approval required\nIssue: {title}\nRequested by: {agent_name or 'System'}\nState: {state}",
            )

    return {
        "received": True,
        "action": action,
        "issue_id": issue_id,
        "title": title,
        "state": state,
        "agent_id": agent_id,
        "agent_name": agent_name,
        "queued_agent_id": agent_id,
        "queued_agent_name": agent_name,
    }


@app.post("/webhooks/linear")
async def linear_webhook(request: Request):
    payload = await request.json()
    return await _process_linear_payload(payload)


@app.post("/test/create-issue")
async def test_create_issue(request: Request):
    """
    Create a Linear issue via API and run the pipeline (Nova for Ready for Spec).
    Body: { "title": "Your issue title" }. Optional: "team_id" (default: LINEAR_TEAM_ID or first team).
    Requires LINEAR_API_KEY and LINEAR_TEAM_ID (or we use the first team).
    """
    body = await request.json() if request.headers.get("content-type", "").startswith("application/json") else {}
    title = (body.get("title") or "").strip() or "Add a simple test button to the dashboard"

    team_id = body.get("team_id") or os.getenv("LINEAR_TEAM_ID")
    if not team_id:
        teams, err = get_teams()
        if err:
            return {"ok": False, "error": f"Linear teams: {err}"}
        if not teams:
            return {"ok": False, "error": "No Linear teams found. Set LINEAR_TEAM_ID or check LINEAR_API_KEY."}
        team_id = teams[0]["id"]

    states, err = get_workflow_states(team_id)
    if err:
        return {"ok": False, "error": f"Linear workflow states: {err}"}
    state_id = None
    for s in states:
        if (s.get("name") or "").strip().lower() == "ready for spec":
            state_id = s["id"]
            break
    if not state_id and states:
        state_id = states[0]["id"]

    issue, err = linear_create_issue(team_id, title, state_id)
    if err:
        return {"ok": False, "error": f"Linear create issue: {err}"}

    payload = {
        "action": "create",
        "data": {
            "id": issue["id"],
            "title": issue.get("title", title),
            "state": "Ready for Spec",
        },
    }
    result = await _process_linear_payload(payload)
    result["ok"] = True
    result["linear_issue"] = {"id": issue["id"], "identifier": issue.get("identifier"), "title": issue.get("title")}
    return result
@app.get("/approvals/pending")
async def approvals_pending():
    approvals = get_pending_approvals()
    return {"pending_approvals": approvals}
@app.get("/jobs/recent")
async def jobs_recent():
    jobs = get_recent_jobs()
    return {"jobs": jobs}
@app.get("/atlas/daily-summary")
async def atlas_daily_summary():
    recent_tasks = get_recent_tasks()
    blocked_tasks = get_blocked_tasks()
    pending_approvals = get_pending_approvals()
    failed_jobs = get_failed_jobs()

    team_context = build_team_context("chief_of_staff")
    agent_output = run_agent(
        "chief_of_staff",
        {
            "recent_tasks_count": len(recent_tasks),
            "blocked_count": len(blocked_tasks),
            "pending_approvals_count": len(pending_approvals),
            "failed_jobs_count": len(failed_jobs),
        },
        team_context=team_context,
    )

    if SLACK_CHANNEL_STANDUP:
        await send_slack_message(
            SLACK_CHANNEL_STANDUP,
            f"{agent_output['agent_name']} daily summary\n\n{agent_output['content']}"
        )

    return {
        "ok": True,
        "agent_id": agent_output["agent_id"],
        "agent_name": agent_output["agent_name"],
        "output_type": agent_output["output_type"],
        "content": agent_output["content"],
    }
@app.get("/atlas/blockers")
async def atlas_blockers():
    blocked_tasks = get_blocked_tasks()

    if not blocked_tasks:
        return {"ok": True, "message": "No blocked tasks."}

    lines = ["Blocked tasks:"]
    for task in blocked_tasks[:10]:
        lines.append(f"- {task.get('title', 'Untitled')}")

    message = "\n".join(lines)

    if SLACK_CHANNEL_ALERTS:
        await send_slack_message(
            SLACK_CHANNEL_ALERTS,
            f"Atlas blocker report\n\n{message}"
        )

    return {"ok": True, "blocked_count": len(blocked_tasks), "message": message}