"""
Mailbox: per-agent inbox for Claude Code Teams–style messaging.
SendMessage(from_agent_id, to_agent_id, content); to_agent_id=None = broadcast.
"""
from datetime import datetime, timezone
from services.memory.supabase_client import get_supabase
from config.teams import TEAMMATE_IDS, TEAM_LEAD_ID


def send_message(
    from_agent_id: str,
    content: str,
    to_agent_id: str | None = None,
    task_id: int | None = None,
) -> list:
    """
    Send a message to one agent (to_agent_id) or broadcast (to_agent_id=None).
    Broadcast goes to all teammates + lead. Returns list of inserted rows.
    """
    supabase = get_supabase()
    inserts = []

    if to_agent_id is None:
        # Broadcast: one row per recipient (lead + all teammates)
        recipients = [TEAM_LEAD_ID] + [a for a in TEAMMATE_IDS if a != from_agent_id]
        for rid in recipients:
            row = supabase.table("mailbox").insert({
                "from_agent_id": from_agent_id,
                "to_agent_id": rid,
                "task_id": task_id,
                "content": content,
                "created_at": datetime.now(timezone.utc).isoformat(),
            }).execute()
            if row.data:
                inserts.extend(row.data)
    else:
        row = supabase.table("mailbox").insert({
            "from_agent_id": from_agent_id,
            "to_agent_id": to_agent_id,
            "task_id": task_id,
            "content": content,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }).execute()
        if row.data:
            inserts.extend(row.data)

    return inserts


def get_inbox(agent_id: str, limit: int = 50, unread_only: bool = False):
    """Return messages for this agent, newest first."""
    supabase = get_supabase()
    q = (
        supabase.table("mailbox")
        .select("*")
        .eq("to_agent_id", agent_id)
        .order("created_at", desc=True)
        .limit(limit)
    )
    if unread_only:
        q = q.is_("read_at", "null")
    result = q.execute()
    return result.data or []


def mark_read(message_id: int):
    """Mark a mailbox message as read."""
    supabase = get_supabase()
    supabase.table("mailbox").update({
        "read_at": datetime.now(timezone.utc).isoformat(),
    }).eq("id", message_id).execute()
