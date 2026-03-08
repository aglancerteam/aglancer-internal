from services.memory.supabase_client import get_supabase


def insert_agent_output(task_id: int, agent_id: str, agent_name: str, output_type: str, content: str):
    supabase = get_supabase()
    result = supabase.table("agent_outputs").insert({
        "task_id": task_id,
        "agent_id": agent_id,
        "agent_name": agent_name,
        "output_type": output_type,
        "content": content,
    }).execute()
    return result.data
