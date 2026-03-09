# Agents for full project lifecycle (brand → design → build → test → run)

This doc lists **new agents** to add so the team can run a new project from scratch (brand, architecture, implementation, QA, docs) with every phase owned by an agent. Existing agents are summarized first.

---

## Current agents (already in place)

| Agent   | ID                | Trigger (Linear state) | Role / deliverable |
|---------|-------------------|-------------------------|---------------------|
| **Nova**    | `product_manager`   | Ready for Spec           | Product spec: problem, user story, acceptance criteria, deliverable. Writes to issue description. |
| **Forge**   | `lead_developer`    | Ready to Build           | Implementation; deliverable confirmation as comment. |
| **Sentinel**| `qa_security`       | Review                   | QA review; sign-off or feedback as comment. |
| **Scribe**  | `docs_knowledge`    | Done                     | Docs update, project summary, changelog. |
| **Atlas**   | `chief_of_staff`    | Blocked / cron           | Daily summary, pending approvals, ops. |

These cover **spec → build → review → docs → ops**. They do **not** cover **brand** or **technical/architecture design**.

---

## New agents to add (recommended)

### 1. Brand strategist (Phase 1: Brand building)

| Field   | Value |
|--------|--------|
| **Name**   | **Meridian** (or "Brand") |
| **agent_id** | `brand_strategist` |
| **Role**   | Brand strategy and guidelines |
| **Trigger** | New Linear state: **Ready for Brand** |
| **Deliverable** | Brand brief, name/tagline options, voice & tone, messaging, brand asset checklist. Written to issue description (and optionally `docs/brand/` via Scribe or manual). |
| **When to use** | Epic "Brand & positioning"; tickets like "Define brand voice", "Name and tagline", "Logo and visual identity brief". |

**Why a dedicated agent:** Brand is a distinct skill set (positioning, voice, messaging). Nova is tuned for product/feature specs, not brand strategy.

---

### 2. Architect (Phase 2: Technical and architectural design)

| Field   | Value |
|--------|--------|
| **Name**   | **Vertex** (or "Architect") |
| **agent_id** | `architect` |
| **Role**   | Technical design and architecture |
| **Trigger** | New Linear state: **Ready for Architecture** (or reuse **Ready for Design** and split UX vs architecture; see below) |
| **Deliverable** | ADRs (decision + rationale + consequences), tech stack rationale, high-level system design, API/auth approach. Written to issue description; can reference or draft `docs/architecture/` content. |
| **When to use** | Epic "Technical design"; tickets like "Tech stack selection", "System architecture", "API design", "ADR: database choice". |

**Why a dedicated agent:** Architecture is decision-focused and technical (trade-offs, constraints, ADRs). Nova does product specs; Forge does implementation. Neither owns "how we should build the system."

**Note:** Your router already has `Ready for Design` → `ux_ui` (Luma) and `AGENT_NAMES` has "Architect" for `agent_builder`. Recommendation: add **Vertex** as `architect` for *technical* design and use **Ready for Architecture** for it; keep **Luma** (`ux_ui`) for *UX/UI* design under **Ready for Design** if you add Luma later.

---

### 3. Luma – UX/UI (Phase 2: Design, optional)

| Field   | Value |
|--------|--------|
| **Name**   | **Luma** |
| **agent_id** | `ux_ui` |
| **Role**   | UX and UI design |
| **Trigger** | Linear state: **Ready for Design** (already in router) |
| **Deliverable** | User flows, wireframe descriptions, UI copy, design system notes, accessibility considerations. |
| **When to use** | Tickets like "Login flow UX", "Dashboard layout", "Design system basics". |

**Status:** Router already maps **Ready for Design** → `ux_ui`; Luma is not in `config/agents.py` yet. Add when you want design work to be agent-driven.

---

### 4. Pulse – Growth / marketing (post-launch, optional)

| Field   | Value |
|--------|--------|
| **Name**   | **Pulse** |
| **agent_id** | `growth_marketing` |
| **Role**   | Growth and go-to-market |
| **Trigger** | New state e.g. **Ready for GTM** or label `growth` + existing state. |
| **Deliverable** | Launch checklist, positioning one-pager, channel/audience notes, copy suggestions. |
| **When to use** | Post-build; tickets like "Launch plan", "Landing page copy", "Launch checklist". |

**Status:** Name exists in router’s `AGENT_NAMES` only. Add when you run launch/marketing work in Linear.

---

## Summary: what to add for the playbook

| Priority | Agent        | agent_id           | Linear state (new or existing) | Purpose |
|----------|--------------|--------------------|---------------------------------|---------|
| **Must-have** | **Meridian** | `brand_strategist` | **Ready for Brand**            | Phase 1: brand brief, voice, messaging. |
| **Must-have** | **Vertex**   | `architect`        | **Ready for Architecture**      | Phase 2: ADRs, tech stack, system design. |
| Optional | **Luma**     | `ux_ui`            | Ready for Design (existing)    | Phase 2: UX/UI flows, design system. |
| Optional | **Pulse**    | `growth_marketing` | **Ready for GTM** (or label)   | Post-launch: GTM, launch plan, copy. |

---

## What to do in Linear (states and categories)

**Add four workflow states** and set each to **State type: Started** (same category as "Ready for Spec", "Ready to Build", "Review"):

| State                   | Agent    |
|-------------------------|----------|
| Ready for Brand         | Meridian |
| Ready for Design        | Luma     |
| Ready for Architecture  | Vertex   |
| Ready for GTM           | Pulse    |

Full step-by-step and category reference: **[LINEAR_SETUP.md](LINEAR_SETUP.md)**.

---

## Implementation checklist (when you add agents)

For each new agent (e.g. Meridian, Vertex):

1. **Linear** – Add workflow state (e.g. "Ready for Brand", "Ready for Architecture") in the team’s workflow.
2. **config/agents.py** – Add entry: `agent_id`, `name`, `role`, `prompt_file` (e.g. `.claude/agents/meridian.md`).
3. **config/teams.py** – Add `agent_id` to `TEAMMATE_IDS` if the agent should get task list and mailbox.
4. **services/router.py** – Add state → agent_id in `AGENT_MAPPING` and name in `AGENT_NAMES`.
5. **services/agents/runner.py** – Add `AGENT_OUTPUT_TYPES` entry and template block for fallback when Claude isn’t used; use same pattern as Nova/Forge (deliverable in description or comment).
6. **.claude/agents/<name>.md** – Write the agent prompt (role, inputs, output format, deliverable wording).
7. **apps/worker/app/main.py** – If the agent writes to Linear (e.g. Meridian/Vertex → description like Nova), add branch for `agent_id` to call `linear_update_issue_description`; if comment-only (like Forge), add `linear_create_comment`.
8. **apps/orchestrator** – Ensure the agent_id is included where jobs are created (e.g. same list as product_manager, lead_developer, etc.) so webhook creates jobs for the new state.

---

## Minimal set for “brand + architecture + build” today

- Add **Meridian** (`brand_strategist`) + state **Ready for Brand**.
- Add **Vertex** (`architect`) + state **Ready for Architecture**.

That gives you agent coverage for Phases 1 and 2 of the playbook; Nova, Forge, Sentinel, Scribe, and Atlas continue to cover spec → build → review → docs → ops.
