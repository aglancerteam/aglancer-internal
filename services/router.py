AGENT_MAPPING = {
    "Ready for Spec": "product_manager",
    "Ready for Design": "ux_ui",
    "Ready to Build": "lead_developer",
    "Review": "qa_security",
    "Done": "docs_knowledge",
    "Blocked": "chief_of_staff",
    "Awaiting Approval": None,
}

AGENT_NAMES = {
    "chief_of_staff": "Atlas",
    "product_manager": "Nova",
    "lead_developer": "Forge",
    "qa_security": "Sentinel",
    "ux_ui": "Luma",
    "growth_marketing": "Pulse",
    "docs_knowledge": "Scribe",
    "agent_builder": "Architect",
}


def get_next_agent(state: str):
    agent_id = AGENT_MAPPING.get(state)

    if not agent_id:
        return None

    return {
        "agent_id": agent_id,
        "agent_name": AGENT_NAMES.get(agent_id, agent_id),
    }