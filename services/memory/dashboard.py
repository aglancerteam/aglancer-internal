from services.memory.supabase_client import get_supabase


def get_recent_tasks(limit: int = 10):
    supabase = get_supabase()
    result = (
        supabase.table("tasks")
        .select("*")
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )
    return result.data


def get_blocked_tasks():
    supabase = get_supabase()
    result = (
        supabase.table("tasks")
        .select("*")
        .eq("state", "Blocked")
        .execute()
    )
    return result.data


def get_pending_approvals():
    supabase = get_supabase()
    result = (
        supabase.table("approvals")
        .select("*")
        .eq("status", "pending")
        .execute()
    )
    return result.data


def get_failed_jobs():
    supabase = get_supabase()
    result = (
        supabase.table("jobs")
        .select("*")
        .eq("status", "failed")
        .order("created_at", desc=True)
        .limit(10)
        .execute()
    )
    return result.data
