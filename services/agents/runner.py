from config.agents import AGENTS


def run_agent(agent_id: str, task: dict) -> dict:
    agent = AGENTS.get(agent_id)

    if not agent:
        raise ValueError(f"Unknown agent_id: {agent_id}")

    title = task.get("title", "Untitled")
    state = task.get("state", "unknown")

    if agent_id == "product_manager":
        content = (
            f"# Product Spec Draft\n\n"
            f"## Feature\n{title}\n\n"
            f"## Current State\n{state}\n\n"
            f"## Problem\n"
            f"Define the business and user problem this feature should solve.\n\n"
            f"## User Story\n"
            f"As a user, I want this feature to work clearly and reliably.\n\n"
            f"## Acceptance Criteria\n"
            f"- Requirement draft created\n"
            f"- Key scope captured\n"
            f"- Ready for review\n\n"
            f"## Edge Cases\n"
            f"- Missing input handling\n"
            f"- Validation behavior\n"
            f"- Failure state handling\n"
        )

        return {
            "agent_id": agent_id,
            "agent_name": agent["name"],
            "output_type": "spec_draft",
            "content": content,
        }

    content = f"{agent['name']} has no execution logic yet for task: {title}"

    return {
        "agent_id": agent_id,
        "agent_name": agent["name"],
        "output_type": "note",
        "content": content,
    }
