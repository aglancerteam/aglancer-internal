# Claude Code Teams Architecture in AGlancer

This document describes how AGlancer implements the [Claude Code Agent Teams](https://code.claude.com/docs/en/agent-teams) model: a **team lead** that coordinates work, **teammates** with independent context, a **shared task list**, and a **mailbox** for inter-agent messaging.

## Mapping: Claude Code Teams → AGlancer

| Claude Code Teams | AGlancer |
|-------------------|----------|
| **Team lead** | **Atlas** (`chief_of_staff`) – coordinates execution, assigns tasks, synthesizes results |
| **Teammates** | **Nova** (PM), **Forge** (Lead Dev), **Scribe** (Docs), and optional Sentinel, Luma, etc. |
| **Task list** | `tasks` + `jobs` with states: `pending` → `in_progress` → `completed`; dependencies supported |
| **Mailbox** | Per-agent inbox (Supabase `mailbox` table); `SendMessage` to one agent or broadcast |
| **Team config** | `config/teams.py` – lead id, member list (name, agent_id, role) |

## Design principles (from Claude Code Teams)

- **Separated concerns**: Data plane (work product: specs, code, docs) is separate from control plane (task assignment, approvals, mailbox).
- **Leader + workers**: Atlas is the policy engine; teammates execute with bounded autonomy to avoid conflicting edits and global inconsistencies.
- **State coordination, not context sharing**: Teammates do not share LLM context. They share the task list and mailbox so each session stays focused and token usage stays bounded.

## Components

### 1. Team lead (Atlas)

- Creates and assigns tasks (e.g. from Linear webhooks or daily summary).
- Spawns teammate work by enqueueing jobs (our equivalent of “spawning” a teammate session).
- Receives idle notifications and mailbox messages from teammates.
- Synthesizes findings (e.g. daily summary, blocker report).
- Can require plan approval: teammate sends plan to lead; lead approves/rejects before implementation.

### 2. Teammates (Nova, Forge, Scribe, …)

- Each has a dedicated role and prompt (e.g. `.claude/agents/nova.md`).
- Claim tasks from the shared task list (pending, unblocked) or receive assignments from the lead.
- Work in their own “context” (separate job/run with only task + mailbox context).
- Send messages to the lead or other teammates via the mailbox.
- Mark tasks completed when done; dependent tasks unblock automatically.

### 3. Task list

- **Location**: Supabase `tasks` and `jobs`; optional file-based mirror under `~/.claude/tasks/{team_name}/` for local tooling.
- **States**: `pending` → `in_progress` → `completed` (and `failed` for jobs).
- **Dependencies**: A task can depend on other tasks; it becomes claimable only when dependencies are completed.
- **Claiming**: Teammates (or lead) claim a task by setting assignee and moving to `in_progress`; use optimistic locking or DB constraints to prevent double-claim.

### 4. Mailbox

- **Location**: Supabase `mailbox` table. Create it with `docs/schema_mailbox.sql` if not using migrations.
- **Semantics**: `SendMessage(from_agent_id, to_agent_id, content)`. `to_agent_id is None` = broadcast to all teammates (use sparingly).
- **Delivery**: When a teammate (or lead) runs, they receive `get_inbox(agent_id)` as part of their context. The lead receives all messages addressed to it and optionally broadcast.

### 5. Team config

- **Lead**: `chief_of_staff` (Atlas).
- **Members**: List of `{ agent_id, name, role }` for all agents that can act as teammates.
- Stored in `config/teams.py` and optionally in DB for runtime (e.g. `~/.claude/teams/{team_name}/config.json`-style export).

## Flow

1. **Linear webhook** → Orchestrator routes issue state to an agent → creates/updates task and enqueues job for that agent (teammate).
2. **Worker** runs the job: loads agent prompt, task context, and mailbox inbox; runs agent logic (today: templates; later: LLM with tools ClaimTask, CompleteTask, SendMessage); inserts agent output; marks job completed; optionally sends message to lead.
3. **Atlas (lead)** runs on schedule or on demand: reads task list, blocked tasks, pending approvals, failed jobs; can create/assign tasks and enqueue jobs; synthesizes daily summary; reads mailbox for teammate updates.
4. **Plan approval** (optional): Teammate sends a “plan” message to lead; lead runs and approves/rejects via mailbox or approval table; teammate only then proceeds to implementation.

## Best practices (from Claude Code Teams)

- **Task sizing**: Self-contained units (e.g. one spec, one implementation slice, one doc update). Avoid too large (long runs without check-in) or too small (coordination overhead).
- **Team size**: 3–5 teammates for most workflows; 5–6 tasks per teammate to keep everyone productive.
- **Avoid file conflicts**: Assign work so different teammates own different files/modules.
- **Give teammates context**: Put task-specific instructions in the job payload and in mailbox messages; teammates load project context (e.g. CLAUDE.md) from their working directory when running in Claude Code; in AGlancer, include relevant context in the prompt payload.

## Limitations and differences from Claude Code IDE

- **No live Claude Code sessions**: AGlancer runs agents as one-off jobs (API-style). “Teammates” are not long-lived IDE sessions; they are invocations with task + mailbox context.
- **One team per deployment**: The “team” is fixed by config (Atlas + configured teammates). No nested teams; only the lead assigns tasks and coordinates.
- **Token usage**: Each job is a separate “session”; token cost scales with number of concurrent jobs and context passed (task list + mailbox).

## Running with Claude Code on the VPS

When the **Claude Code CLI** is installed on the VPS and in PATH, the worker uses **headless mode** (`claude -p "..."`) for each job—no API key needed; your Claude Code (e.g. Max) subscription is used. Each invocation gets the agent role from `.claude/agents/*.md` and the task + team context (inbox, task list). Set `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` so the CLI runs teams-aware. For a **full Agent Teams** setup (one long-running lead session that spawns teammates and uses the shared task list under `~/.claude/tasks/`), run Claude Code interactively (or in tmux) on the VPS; you can add a bridge that writes queue jobs into that task list later.

## Quick start

1. **Create mailbox table**: Run `docs/schema_mailbox.sql` in Supabase if the `mailbox` table does not exist.
2. **Team config**: Lead and teammates are defined in `config/teams.py`; extend `TEAMMATE_IDS` when adding agents.
3. **Sending messages**: From any service or future agent tooling, call `services.memory.mailbox.send_message(from_agent_id, content, to_agent_id=...)` (omit `to_agent_id` to broadcast).
4. **Task list**: Use `services.memory.tasks.get_task_list_for_team()` and `get_claimable_tasks(agent_id)` for lead/teammate context.

## Next steps

- Add real LLM calls in `services/agents/runner.py` using each agent’s prompt file and tools: `ClaimTask`, `CompleteTask`, `SendMessage`, `GetInbox`.
- Optionally add hooks (e.g. `TaskCompleted`, `TeammateIdle`) to enforce quality gates or trigger follow-up jobs.
- Optionally mirror task list to a file-based layout under `~/.claude/tasks/` for compatibility with local Claude Code tooling.
