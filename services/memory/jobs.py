from services.memory.supabase_client import get_supabase
from datetime import datetime, timezone


def create_job(task_id: int, agent_id: str, agent_name: str, job_type: str, payload: dict):
    supabase = get_supabase()
    result = supabase.table("jobs").insert({
        "task_id": task_id,
        "agent_id": agent_id,
        "agent_name": agent_name,
        "job_type": job_type,
        "status": "pending",
        "payload": payload,
    }).execute()
    return result.data[0]


def mark_job_running(job_id: int):
    supabase = get_supabase()
    result = supabase.table("jobs").update({
        "status": "running",
        "started_at": datetime.now(timezone.utc).isoformat(),
    }).eq("id", job_id).execute()
    return result.data


def mark_job_completed(job_id: int, result_payload: dict):
    supabase = get_supabase()
    result = supabase.table("jobs").update({
        "status": "completed",
        "result": result_payload,
        "completed_at": datetime.now(timezone.utc).isoformat(),
    }).eq("id", job_id).execute()
    return result.data


def mark_job_failed(job_id: int, error: str):
    supabase = get_supabase()
    result = supabase.table("jobs").update({
        "status": "failed",
        "error": error,
        "completed_at": datetime.now(timezone.utc).isoformat(),
    }).eq("id", job_id).execute()
    return result.data


def get_recent_jobs(limit: int = 20):
    supabase = get_supabase()
    result = (
        supabase.table("jobs")
        .select("*")
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )
    return result.data


def has_pending_or_running_job(task_id: int, agent_id: str) -> bool:
    """True if there is already a job for this task+agent with status pending or running."""
    supabase = get_supabase()
    result = (
        supabase.table("jobs")
        .select("id")
        .eq("task_id", task_id)
        .eq("agent_id", agent_id)
        .in_("status", ["pending", "running"])
        .limit(1)
        .execute()
    )
    return bool(result.data)


def has_recent_job_for_task_agent(
    task_id: int,
    agent_id: str,
    within_seconds: int = 120,
) -> bool:
    """
    True if a job for this task+agent was created in the last within_seconds (any status).
    Stops duplicate jobs when the worker finishes before the next webhook is processed.
    """
    supabase = get_supabase()
    cutoff = datetime.now(timezone.utc).timestamp() - within_seconds
    cutoff_iso = datetime.fromtimestamp(cutoff, tz=timezone.utc).isoformat()
    result = (
        supabase.table("jobs")
        .select("id")
        .eq("task_id", task_id)
        .eq("agent_id", agent_id)
        .gte("created_at", cutoff_iso)
        .limit(1)
        .execute()
    )
    return bool(result.data)