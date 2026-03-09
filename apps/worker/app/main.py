import asyncio
import os
import re
import time

from services.queue import dequeue_job
from services.agents.runner import run_agent
from services.team_context import build_team_context
from services.memory.jobs import mark_job_running, mark_job_completed, mark_job_failed
from services.memory.agent_outputs import insert_agent_output
from services.slack.client import send_slack_message
from services.docs.updater import update_project_summary, update_active_workstreams
from services.linear.client import (
    create_comment as linear_create_comment,
    update_issue_description as linear_update_issue_description,
    set_issue_state_by_name as linear_set_issue_state_by_name,
)

SLACK_CHANNEL_STANDUP = os.getenv("SLACK_CHANNEL_STANDUP", "")
SLACK_CHANNEL_ALERTS = os.getenv("SLACK_CHANNEL_ALERTS", "")

print("AGlancer worker started")


def post_slack(channel: str, text: str):
    if not channel:
        return
    asyncio.run(send_slack_message(channel, text))


while True:
    job = dequeue_job(timeout=5)

    if not job:
        time.sleep(1)
        continue

    job_id = job["job_id"]
    task_id = job["task_id"]
    agent_id = job["agent_id"]
    agent_name = job["agent_name"]
    payload = job["payload"]

    try:
        print(f"Processing job {job_id} for {agent_name} ({agent_id})")

        mark_job_running(job_id)

        post_slack(
            SLACK_CHANNEL_STANDUP,
            f"{agent_name} started work\n"
            f"Job ID: {job_id}\n"
            f"Task: {payload.get('title', 'Untitled')}"
        )

        team_context = build_team_context(agent_id)
        agent_output = run_agent(agent_id, payload, team_context=team_context)

        if agent_output.get("source") == "template":
            print(
                f"WARNING: {agent_id} used template (Claude CLI/API not used). "
                "Check CLAUDE_CODE_OAUTH_TOKEN and PATH for claude, or ANTHROPIC_API_KEY."
            )

        insert_agent_output(
            task_id=task_id,
            agent_id=agent_output["agent_id"],
            agent_name=agent_output["agent_name"],
            output_type=agent_output["output_type"],
            content=agent_output["content"],
        )
        
        if agent_id == "docs_knowledge":
            update_project_summary(
                title=payload.get("title", "Untitled"),
                agent_name=agent_output["agent_name"],
            )
            update_active_workstreams(
                title=payload.get("title", "Untitled"),
                agent_name=agent_output["agent_name"],
            )

        # Attach deliverable to the ticket: Nova/Meridian/Vertex/Luma/Pulse → description; Forge/Sentinel → comments
        # Linear API needs a real issue UUID (not e.g. "test-issue-001"); otherwise the call fails silently
        issue_id = payload.get("issue_id")
        if issue_id:
            try:
                if agent_id == "triage":
                    content = agent_output.get("content", "")
                    match = re.search(r"State:\s*(.+?)(?:\n|$)", content, re.IGNORECASE)
                    allowed = {
                        "ready for spec", "ready for brand", "ready for design",
                        "ready for architecture", "ready for gtm", "ready to build", "backlog",
                    }
                    if match:
                        state_name = match.group(1).strip()
                        if state_name.lower() in allowed:
                            ok, err = linear_set_issue_state_by_name(issue_id, state_name)
                            if ok:
                                print(f"Linear: triage set issue to state '{state_name}' (issue_id={issue_id})")
                            else:
                                print(f"Linear: triage failed to set state '{state_name}': {err}")
                        else:
                            print(f"Linear: triage chose unknown state '{state_name}', not updating")
                    else:
                        print(f"Linear: triage output had no 'State: ...' line, not updating")
                else:
                    description_agents = ("product_manager", "brand_strategist", "architect", "ux_ui", "growth_marketing")
                    if agent_id in description_agents:
                        content = agent_output.get("content", "")
                        if agent_output.get("source") == "template":
                            content = (
                                "*[Output from template — Claude did not run. Check worker env: CLAUDE_CODE_OAUTH_TOKEN or ANTHROPIC_API_KEY.]*\n\n"
                                + content
                            )
                        ok = linear_update_issue_description(issue_id, content)
                        if not ok:
                            print(f"Linear: failed to update issue description (issue_id={issue_id})")
                    elif agent_id == "lead_developer":
                        result = linear_create_comment(
                            issue_id,
                            f"**[Forge] Deliverable confirmation**\n\n{agent_output.get('content', '')}",
                        )
                        if not result:
                            print(f"Linear: failed to create comment (issue_id={issue_id})")
                    elif agent_id == "qa_security":
                        result = linear_create_comment(
                            issue_id,
                            f"**[Sentinel] QA review**\n\n{agent_output.get('content', '')}",
                        )
                        if not result:
                            print(f"Linear: failed to create comment (issue_id={issue_id})")
            except Exception as e:
                print(f"Linear API error: {e}")  # don't fail the job

        mark_job_completed(job_id, agent_output)

        content = agent_output.get("content", "")
        content_preview = content[:2000] + ("…" if len(content) > 2000 else "") if content else "(no content)"

        source_note = " (template)" if agent_output.get("source") == "template" else ""
        post_slack(
            SLACK_CHANNEL_STANDUP,
            f"{agent_output['agent_name']} completed work{source_note}\n"
            f"Job ID: {job_id}\n"
            f"Task: {payload.get('title', 'Untitled')}\n"
            f"Output type: {agent_output['output_type']}\n\n"
            f"Content:\n{content_preview}"
        )

        print(f"Completed job {job_id}")

    except Exception as e:
        mark_job_failed(job_id, str(e))

        post_slack(
            SLACK_CHANNEL_ALERTS,
            f"Job failed\n"
            f"Job ID: {job_id}\n"
            f"Agent: {agent_name} ({agent_id})\n"
            f"Task: {payload.get('title', 'Untitled')}\n"
            f"Error: {str(e)}"
        )

        print(f"Failed job {job_id}: {e}")