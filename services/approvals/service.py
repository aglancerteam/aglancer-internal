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
