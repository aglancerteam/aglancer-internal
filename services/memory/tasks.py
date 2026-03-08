from services.memory.supabase_client import get_supabase


def upsert_task(linear_issue_id: str, title: str, state: str, owner_agent: str | None = None):
    supabase = get_supabase()
    result = supabase.table("tasks").upsert({
        "linear_issue_id": linear_issue_id,
        "title": title,
        "state": state,
        "owner_agent": owner_agent,
    }, on_conflict="linear_issue_id").execute()
    return result.data


def get_task_by_linear_issue_id(linear_issue_id: str):
    supabase = get_supabase()
    result = supabase.table("tasks").select("*").eq("linear_issue_id", linear_issue_id).limit(1).execute()
    return result.data[0] if result.data else None


def insert_task_event(task_id: int, event_type: str, payload: dict):
    supabase = get_supabase()
    result = supabase.table("task_events").insert({
        "task_id": task_id,
        "event_type": event_type,
        "payload": payload,
    }).execute()
    return result.data
