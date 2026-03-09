from services.memory.supabase_client import get_supabase


def create_approval(task_id: int, title: str, requested_by_agent: str | None):
    supabase = get_supabase()
    result = supabase.table("approvals").insert({
        "task_id": task_id,
        "title": title,
        "requested_by_agent": requested_by_agent,
        "status": "pending",
    }).execute()
    return result.data


def get_pending_approvals():
    supabase = get_supabase()
    result = supabase.table("approvals").select("*").eq("status", "pending").execute()
    return result.data


def get_pending_approval_for_task(task_id: int):
    """Return the first pending approval for this task, or None."""
    supabase = get_supabase()
    result = (
        supabase.table("approvals")
        .select("*")
        .eq("task_id", task_id)
        .eq("status", "pending")
        .limit(1)
        .execute()
    )
    return result.data[0] if result.data else None


def resolve_approvals_for_task(task_id: int):
    """Mark all pending approvals for this task as resolved (approved). Call when issue moves to Ready to Build."""
    supabase = get_supabase()
    result = (
        supabase.table("approvals")
        .update({"status": "approved"})
        .eq("task_id", task_id)
        .eq("status", "pending")
        .execute()
    )
    return result.data
