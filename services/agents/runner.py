import os
from config.agents import AGENTS
from config.teams import get_team_config
from services.agents.prompts import load_agent_prompt
from services.agents.brand_context import load_brand_kit, BRAND_AWARE_AGENTS
from services.claude.headless import complete as claude_headless_complete, is_available as claude_cli_available
from services.claude.client import complete as claude_api_complete


# Output types per agent (for storage and Slack)
AGENT_OUTPUT_TYPES = {
    "chief_of_staff": "ops_summary",
    "product_manager": "spec_draft",
    "lead_developer": "engineering_draft",
    "docs_knowledge": "docs_update",
    "qa_security": "qa_review",
    "brand_strategist": "brand_brief",
    "architect": "architecture_draft",
    "ux_ui": "design_draft",
    "growth_marketing": "gtm_draft",
    "triage": "triage_decision",
}


def _build_user_message(agent_id: str, task: dict, team_context: dict) -> str:
    """Build the user message for Claude: task details + team context (+ brand kit when relevant)."""
    title = task.get("title", "Untitled")
    state = task.get("state", "unknown")
    lines = [
        f"## Current task\nTitle: {title}\nState: {state}",
    ]
    if agent_id in BRAND_AWARE_AGENTS:
        brand_kit = load_brand_kit()
        if brand_kit:
            lines.append("\n## Brand kit (you must stick to this)")
            lines.append("Use the following brand kit as the source of truth. Do not contradict it.")
            lines.append("```")
            lines.append(brand_kit)
            lines.append("```")
    if agent_id == "chief_of_staff":
        lines.append(
            f"Recent tasks: {task.get('recent_tasks_count', 0)}, "
            f"Blocked: {task.get('blocked_count', 0)}, "
            f"Pending approvals: {task.get('pending_approvals_count', 0)}, "
            f"Failed jobs: {task.get('failed_jobs_count', 0)}."
        )
    inbox = team_context.get("inbox", [])
    if inbox:
        lines.append("\n## Messages for you (mailbox)")
        for m in inbox[:10]:
            lines.append(f"- From {m.get('from_agent_id', '?')}: {m.get('content', '')[:200]}")
    task_list = team_context.get("task_list_summary", [])
    if task_list:
        lines.append("\n## Task list (summary)")
        for t in task_list[:15]:
            lines.append(f"- [{t.get('task_status', '?')}] {t.get('title', '')} (state: {t.get('state', '')})")
    lines.append("\nRespond in the output format defined in your role. Be concise and actionable.")
    return "\n".join(lines)


def run_agent(
    agent_id: str,
    task: dict,
    team_context: dict | None = None,
) -> dict:
    """
    Run an agent with optional Claude Code Teams context (inbox, task list).
    If ANTHROPIC_API_KEY is set and the agent has a prompt file, uses Claude; otherwise uses templates.
    """
    agent = AGENTS.get(agent_id)

    if not agent:
        raise ValueError(f"Unknown agent_id: {agent_id}")

    if team_context is None:
        team_context = {}

    def _with_team_context(d: dict, source: str = "template") -> dict:
        d["source"] = d.get("source", source)
        if team_context:
            d["team_context"] = {
                "inbox": team_context.get("inbox", []),
                "task_list_summary": team_context.get("task_list_summary", []),
                "claimable_tasks": team_context.get("claimable_tasks", []),
                "team_config": get_team_config(),
            }
        return d

    title = task.get("title", "Untitled")
    state = task.get("state", "unknown")

    # 1) Prefer Claude Code CLI (your subscription, no API key) — use when claude is in PATH on VPS
    # 2) Fall back to Anthropic API if ANTHROPIC_API_KEY is set
    # 3) Else use templates
    prompt_file = agent.get("prompt_file")
    if prompt_file:
        system_prompt = load_agent_prompt(prompt_file)
        if system_prompt:
            user_prompt = _build_user_message(agent_id, task, team_context)
            content = None
            source = "template"
            if claude_cli_available():
                try:
                    content = claude_headless_complete(system_prompt, user_prompt)
                    if content:
                        source = "claude"
                except Exception as e:
                    print(f"Claude CLI failed for {agent_id}: {e}")
            if not content and os.getenv("ANTHROPIC_API_KEY"):
                try:
                    content = claude_api_complete(system_prompt, user_prompt)
                    if content:
                        source = "claude"
                except Exception as e:
                    print(f"Claude API failed for {agent_id}: {e}")
            if content:
                output_type = AGENT_OUTPUT_TYPES.get(agent_id, "note")
                out = _with_team_context({
                    "agent_id": agent_id,
                    "agent_name": agent["name"],
                    "output_type": output_type,
                    "content": content.strip(),
                })
                out["source"] = source
                return out

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

        return _with_team_context({
            "agent_id": agent_id,
            "agent_name": agent["name"],
            "output_type": "spec_draft",
            "content": content,
        })

    if agent_id == "brand_strategist":
        content = (
            f"# Brand Brief\n\n"
            f"## Focus\n{title}\n\n"
            f"## Current State\n{state}\n\n"
            f"## Brand direction\n"
            f"Define positioning and voice.\n\n"
            f"## Name / tagline options\n"
            f"- Option 1\n"
            f"- Option 2\n\n"
            f"## Voice & tone\n"
            f"Guidelines for messaging.\n\n"
            f"## Key messages\n"
            f"- Primary message\n"
            f"- Supporting points\n\n"
            f"## Deliverable\n"
            f"One clear statement of what must exist to consider this brand work done.\n"
        )
        return _with_team_context({
            "agent_id": agent_id,
            "agent_name": agent["name"],
            "output_type": "brand_brief",
            "content": content,
        })

    if agent_id == "architect":
        content = (
            f"# Architecture / ADR Draft\n\n"
            f"## Topic\n{title}\n\n"
            f"## Current State\n{state}\n\n"
            f"## Context\n"
            f"Background and constraints.\n\n"
            f"## Decision\n"
            f"Proposed technical decision and rationale.\n\n"
            f"## Alternatives considered\n"
            f"- Option A\n"
            f"- Option B\n\n"
            f"## Consequences\n"
            f"- Positive\n"
            f"- Negative / risks\n\n"
            f"## Deliverable\n"
            f"One clear statement of what must exist (e.g. ADR doc, diagram) to consider this done.\n"
        )
        return _with_team_context({
            "agent_id": agent_id,
            "agent_name": agent["name"],
            "output_type": "architecture_draft",
            "content": content,
        })

    if agent_id == "ux_ui":
        content = (
            f"# UX/UI Design Draft\n\n"
            f"## Focus\n{title}\n\n"
            f"## Current State\n{state}\n\n"
            f"## User flows\n"
            f"Key flows and steps.\n\n"
            f"## Wireframe / layout notes\n"
            f"Structure and components.\n\n"
            f"## UI copy and labels\n"
            f"Key strings and microcopy.\n\n"
            f"## Accessibility & design system\n"
            f"Notes for consistency and a11y.\n\n"
            f"## Deliverable\n"
            f"One clear statement of what must exist (e.g. flow doc, wireframe) to consider this done.\n"
        )
        return _with_team_context({
            "agent_id": agent_id,
            "agent_name": agent["name"],
            "output_type": "design_draft",
            "content": content,
        })

    if agent_id == "growth_marketing":
        content = (
            f"# GTM / Marketing Draft\n\n"
            f"## Focus\n{title}\n\n"
            f"## Current State\n{state}\n\n"
            f"## Positioning\n"
            f"One-liner and differentiation.\n\n"
            f"## Audience & channels\n"
            f"Who and where.\n\n"
            f"## Launch checklist\n"
            f"- Item 1\n"
            f"- Item 2\n\n"
            f"## Copy / messaging\n"
            f"Key headlines and CTAs.\n\n"
            f"## Deliverable\n"
            f"One clear statement of what must exist to consider this GTM work done.\n"
        )
        return _with_team_context({
            "agent_id": agent_id,
            "agent_name": agent["name"],
            "output_type": "gtm_draft",
            "content": content,
        })

    if agent_id == "triage":
        content = (
            f"# Triage\n\n"
            f"## Ticket\n{title}\n\n"
            f"## Current State\n{state}\n\n"
            f"## Routing decision\n"
            f"State: Ready for Spec\n\n"
            f"(Choose one: Ready for Spec, Ready for Brand, Ready for Design, Ready for Architecture, Ready for GTM, Ready to Build, or Backlog.)\n"
        )
        return _with_team_context({
            "agent_id": agent_id,
            "agent_name": agent["name"],
            "output_type": "triage_decision",
            "content": content,
        })

    if agent_id == "lead_developer":
        content = (
            f"# Engineering Implementation Draft\n\n"
            f"## Feature\n{title}\n\n"
            f"## Current State\n{state}\n\n"
            f"## Proposed Tasks\n"
            f"- Review current architecture\n"
            f"- Identify affected modules\n"
            f"- Implement required backend changes\n"
            f"- Add tests\n"
            f"- Prepare for QA review\n\n"
            f"## Technical Notes\n"
            f"- Confirm API contract\n"
            f"- Confirm persistence changes if any\n"
            f"- Validate routing and webhook behavior\n\n"
            f"## Risks\n"
            f"- State transition mismatches\n"
            f"- Missing validation\n"
            f"- Incomplete test coverage\n"
        )

        return _with_team_context({
            "agent_id": agent_id,
            "agent_name": agent["name"],
            "output_type": "engineering_draft",
            "content": content,
        })

    if agent_id == "docs_knowledge":
        content = (
            f"# Documentation Update Summary\n\n"
            f"## Completed Item\n{title}\n\n"
            f"## State\n{state}\n\n"
            f"## Summary\n"
            f"This item has been completed and should be reflected in project documentation.\n\n"
            f"## Documentation Actions\n"
            f"- Add/update project summary\n"
            f"- Add/update active workstreams\n"
            f"- Note completion in project memory\n"
        )

        return _with_team_context({
            "agent_id": agent_id,
            "agent_name": agent["name"],
            "output_type": "docs_update",
            "content": content,
        })

    if agent_id == "qa_security":
        content = (
            f"# QA / Security Review\n\n"
            f"## Item\n{title}\n\n"
            f"## State\n{state}\n\n"
            f"## Review checklist\n"
            f"- Expected flow and happy path\n"
            f"- Missing validation and edge cases\n"
            f"- Regression risks\n"
            f"- Failure scenarios and error handling\n"
            f"- Security or abuse concerns\n\n"
            f"## Verdict\n"
            f"Approve for Done / or send back to Build with notes.\n"
        )
        return _with_team_context({
            "agent_id": agent_id,
            "agent_name": agent["name"],
            "output_type": "qa_review",
            "content": content,
        })

    if agent_id == "chief_of_staff":
        blocked = task.get("blocked_count", 0)
        pending_approvals = task.get("pending_approvals_count", 0)
        failed_jobs = task.get("failed_jobs_count", 0)
        recent_count = task.get("recent_tasks_count", 0)

        content = (
            f"# Daily Operations Summary\n\n"
            f"## Overview\n"
            f"- Recent tasks reviewed: {recent_count}\n"
            f"- Blocked tasks: {blocked}\n"
            f"- Pending approvals: {pending_approvals}\n"
            f"- Failed jobs: {failed_jobs}\n\n"
            f"## Recommended Actions\n"
            f"- Review blocked tasks first\n"
            f"- Resolve pending approvals\n"
            f"- Check failed job logs if any exist\n"
        )

        return _with_team_context({
            "agent_id": agent_id,
            "agent_name": agent["name"],
            "output_type": "ops_summary",
            "content": content,
        })

    content = f"{agent['name']} has no execution logic yet for task: {title}"
    return _with_team_context({
        "agent_id": agent_id,
        "agent_name": agent["name"],
        "output_type": "note",
        "content": content,
    })