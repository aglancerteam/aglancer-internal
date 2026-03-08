import os
from fastapi import FastAPI, Request
from services.slack.client import send_slack_message
from services.memory.tasks import upsert_task, get_task_by_linear_issue_id, insert_task_event
from services.memory.agent_outputs import insert_agent_output
from services.router import get_next_agent
from services.agents.runner import run_agent
from services.approvals.service import create_approval
from services.approvals.service import get_pending_approvals

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


@app.post("/webhooks/linear")
async def linear_webhook(request: Request):
    payload = await request.json()

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
    agent_output = None

    if agent:
        agent_id = agent["agent_id"]
        agent_name = agent["agent_name"]

    upsert_task(issue_id, title, state, agent_id)
    task = get_task_by_linear_issue_id(issue_id)

    if task:
        insert_task_event(task["id"], action, payload)

    if task and agent_id == "product_manager":
        agent_output = run_agent(
            agent_id,
            {
                "title": title,
                "state": state,
            }
        )

        insert_agent_output(
            task_id=task["id"],
            agent_id=agent_output["agent_id"],
            agent_name=agent_output["agent_name"],
            output_type=agent_output["output_type"],
            content=agent_output["content"],
        )

        if SLACK_CHANNEL_STANDUP:
            await send_slack_message(
                SLACK_CHANNEL_STANDUP,
                f"{agent_output['agent_name']} completed a draft\n"
                f"Issue: {title}\n"
                f"Output type: {agent_output['output_type']}"
            )

    if SLACK_CHANNEL_STANDUP:
        await send_slack_message(
            SLACK_CHANNEL_STANDUP,
            f"Linear event received: {action}\n"
            f"Issue: {title}\n"
            f"State: {state}"
        )

    if agent and SLACK_CHANNEL_STANDUP:
        await send_slack_message(
            SLACK_CHANNEL_STANDUP,
            f"Task routed to {agent_name} ({agent_id})\n"
            f"Issue: {title}\n"
            f"State: {state}"
        )

    if state == "Awaiting Approval":
        if task:
            create_approval(
                task_id=task["id"],
                title=title,
                requested_by_agent=agent_id,
            )

        if SLACK_CHANNEL_APPROVALS:
            await send_slack_message(
                SLACK_CHANNEL_APPROVALS,
                f"Approval required\n"
                f"Issue: {title}\n"
                f"Requested by: {agent_name or 'System'}\n"
                f"State: {state}"
            )

    return {
        "received": True,
        "action": action,
        "issue_id": issue_id,
        "title": title,
        "state": state,
        "agent_id": agent_id,
        "agent_name": agent_name,
        "agent_output_type": agent_output["output_type"] if agent_output else None,
    }
@app.get("/approvals/pending")
async def approvals_pending():
    approvals = get_pending_approvals()
    return {"pending_approvals": approvals}