"""
Build Claude Code Teams context for an agent: inbox, task list, claimable tasks.
"""
from services.memory.mailbox import get_inbox
from services.memory.tasks import get_task_list_for_team, get_claimable_tasks


def build_team_context(agent_id: str, task_list_limit: int = 20, inbox_limit: int = 20) -> dict:
    """
    Build team_context dict for run_agent(..., team_context=...).
    Includes inbox, task list summary (pending/in_progress/completed), and claimable tasks for this agent.
    """
    inbox = get_inbox(agent_id, limit=inbox_limit)
    full_list = get_task_list_for_team(limit=task_list_limit)
    task_list_summary = [
        {
            "task_id": t["id"],
            "title": t.get("title", ""),
            "state": t.get("state"),
            "task_status": t.get("task_status", "pending"),
            "owner_agent": t.get("owner_agent"),
        }
        for t in full_list
    ]
    claimable_tasks = get_claimable_tasks(agent_id, limit=task_list_limit)

    return {
        "inbox": inbox,
        "task_list_summary": task_list_summary,
        "claimable_tasks": claimable_tasks,
    }
