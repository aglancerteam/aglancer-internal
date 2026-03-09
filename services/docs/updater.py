from pathlib import Path
from datetime import datetime

BASE_DOCS_PATH = Path("/app/docs")


def append_to_file(filename: str, content: str):
    file_path = BASE_DOCS_PATH / filename
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with open(file_path, "a", encoding="utf-8") as f:
        f.write(content)


def update_project_summary(title: str, agent_name: str):
    timestamp = datetime.utcnow().isoformat()
    append_to_file(
        "project_summary.md",
        f"\n## {title}\n"
        f"- Updated by: {agent_name}\n"
        f"- Timestamp: {timestamp}\n"
        f"- Status: Completed and documented\n"
    )


def update_active_workstreams(title: str, agent_name: str):
    timestamp = datetime.utcnow().isoformat()
    append_to_file(
        "active_workstreams.md",
        f"\n- {title} | documented by {agent_name} | {timestamp}\n"
    )
