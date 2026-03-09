"""
Claude Code Teams architecture: team lead + teammates.
Single team per deployment; lead coordinates, teammates execute.
"""
from config.agents import AGENTS

# Team lead (policy engine, assigns tasks, synthesizes results)
TEAM_LEAD_ID = "chief_of_staff"

# Teammates: agent_ids that can claim tasks and receive mailbox messages.
# Excludes the lead; only these are spawned as "worker" jobs from the orchestrator.
TEAMMATE_IDS = [
    "product_manager",   # Nova
    "lead_developer",   # Forge
    "docs_knowledge",   # Scribe
    "qa_security",      # Sentinel (Review stage)
    "brand_strategist", # Meridian
    "architect",        # Vertex
    "ux_ui",            # Luma
    "growth_marketing", # Pulse
    "triage",          # Switch (routes to correct status)
]


def get_team_lead():
    """Return the team lead agent config."""
    return AGENTS.get(TEAM_LEAD_ID)


def get_teammates():
    """Return list of teammate agent configs (name, agent_id, role)."""
    return [
        {"agent_id": aid, "name": AGENTS[aid]["name"], "role": AGENTS[aid]["role"]}
        for aid in TEAMMATE_IDS
        if aid in AGENTS
    ]


def get_team_config():
    """Full team config for lead and members (Claude Code Teams–style)."""
    lead = get_team_lead()
    if not lead:
        return None
    return {
        "lead": {
            "agent_id": TEAM_LEAD_ID,
            "name": lead["name"],
            "role": lead["role"],
        },
        "members": [
            {"agent_id": TEAM_LEAD_ID, "name": lead["name"], "role": lead["role"]},
            *get_teammates(),
        ],
    }


def is_teammate(agent_id: str) -> bool:
    """True if agent_id is a teammate (can claim tasks, receive messages)."""
    return agent_id in TEAMMATE_IDS


def is_lead(agent_id: str) -> bool:
    """True if agent_id is the team lead."""
    return agent_id == TEAM_LEAD_ID
