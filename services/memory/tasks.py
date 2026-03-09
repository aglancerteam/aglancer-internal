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


# --- Claude Code Teams: task list semantics (pending / in_progress / completed) ---


def get_task_list_for_team(limit: int = 50):
    """
    Task list view for the team: tasks with job status.
    Status derived from jobs: pending (job pending), in_progress (job running), completed (job completed).
    """
    supabase = get_supabase()
    tasks_result = (
        supabase.table("tasks")
        .select("id, linear_issue_id, title, state, owner_agent, created_at")
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )
    tasks = tasks_result.data or []
    if not tasks:
        return []

    task_ids = [t["id"] for t in tasks]
    jobs_result = (
        supabase.table("jobs")
        .select("task_id, agent_id, status, created_at, completed_at")
        .in_("task_id", task_ids)
        .order("created_at", desc=True)
        .execute()
    )
    jobs = jobs_result.data or []

    # Latest job per (task_id, agent_id) to get current status per task
    by_task = {}
    for j in jobs:
        tid = j["task_id"]
        if tid not in by_task:
            by_task[tid] = []
        by_task[tid].append(j)

    out = []
    for t in tasks:
        tid = t["id"]
        task_jobs = by_task.get(tid, [])
        # Overall task status: any running -> in_progress; else any completed -> completed; else pending
        status = "pending"
        for j in task_jobs:
            if j["status"] == "running":
                status = "in_progress"
                break
            if j["status"] == "completed":
                status = "completed"
                break
        out.append({
            **t,
            "task_status": status,
            "jobs": task_jobs[:5],
        })
    return out


def get_claimable_tasks(agent_id: str, limit: int = 20):
    """
    Tasks that have a pending job for this agent (already assigned by lead/orchestrator).
    Worker "claims" by dequeuing the job; this list is for context so the agent sees what's available.
    """
    supabase = get_supabase()
    result = (
        supabase.table("jobs")
        .select("id, task_id, agent_id, status, payload, created_at")
        .eq("agent_id", agent_id)
        .eq("status", "pending")
        .order("created_at", desc=False)
        .limit(limit)
        .execute()
    )
    return result.data or []
