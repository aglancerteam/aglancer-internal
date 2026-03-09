# New project playbook

Run a new project from scratch with **brand → design → build → test → run**, everything tracked in **Linear**, shipped via **GitHub**, and **documented from day 1**.

---

## Principles

- **One source of truth for work**: Linear (tickets, deliverables, sprints).
- **One source of truth for code**: GitHub (repo, branches, PRs, releases).
- **Documentation is part of the definition of done**: No ticket closed without docs/changelog updated where relevant.
- **Sprints and cycles**: Work is planned in time-boxed sprints; each has clear goals and a deployable outcome when possible.

---

## Phase 0: Project kickoff (Day 1)

Do this before any brand or tech work so the team has a single place to work and document.

### Linear

1. **Create a new Linear project** (or team) for this product.
2. **Workflow states** – set up (or reuse) a lifecycle that supports your phases, for example:
   - `Backlog` → `Ready for Spec` → `Awaiting Approval` → `Ready to Build` → `In Progress` → `Review` → `Done`
   - Optional: `Blocked`, `Won't Do`, `Deferred`
3. **Labels** (examples):
   - **Phase**: `brand`, `design`, `architecture`, `implementation`, `qa`, `docs`, `ops`
   - **Type**: `epic`, `feature`, `bug`, `chore`, `spike`
   - **Area**: `frontend`, `backend`, `infra`, `content`, etc.
4. **Cycles (sprints)**:
   - Enable Cycles; set length (e.g. 2 weeks).
   - Plan work in cycles; use cycle goals for “what we ship this sprint.”

### GitHub

1. **Create a new repository** for the project.
2. **Branch strategy** (suggested):
   - `main` – production-ready; only merged via PR after review.
   - `develop` (optional) – integration branch for the current release.
   - Feature branches: `feature/<linear-issue-id>-short-name` or `feat/description`.
3. **Repo contents from day 1**:
   - `README.md` – project name, one-line purpose, how to run locally, link to Linear project.
   - `docs/` – all design and product docs (see [Documentation](#documentation-from-day-1) below).
   - `.github/` – PR template, issue templates, and (when ready) CI/CD workflows.

### Documentation structure (create on day 1)

```
docs/
  README.md           # Index of all docs
  CHANGELOG.md        # Versioned list of changes (one place for “what shipped”)
  brand/              # Brand guidelines, voice, assets (when ready)
  architecture/      # ADRs, system design, diagrams
  specs/              # Product/feature specs (or link to Linear)
  runbooks/           # Ops, deployment, troubleshooting
```

Commit the structure and a minimal `README` + `CHANGELOG` so every later change can be documented in place.

---

## Phase 1: Brand building

**Goal:** Name, identity, voice, and core messaging so the rest of the work is aligned.

### Linear

- **Epic**: e.g. “Brand & positioning”
- **Tickets**: One ticket per deliverable, e.g.:
  - Brand name and tagline
  - Logo and visual identity (concept → final)
  - Voice & tone guidelines
  - Messaging / value proposition (short + long)
  - Brand assets pack (logo, colors, fonts, usage rules)
- **States:** Use your workflow (e.g. Ready for Spec → … → Done). Keep deliverables in the ticket description or in a linked doc.

### Deliverables and docs

- Store final brand outputs in `docs/brand/` (and optionally in a shared drive).
- In `CHANGELOG.md`, add an entry like: “Brand: name, logo, voice guidelines (see docs/brand).”
- Link Linear issue in PR/commit so “what was done” is traceable.

### Brand kit (for AGlancer agents)

To have **Meridian**, **Luma**, and **Pulse** stick to your project’s brand when generating content, add a **brand kit file** (e.g. JSX, or any text format) and point AGlancer at it:

- **Default path:** `docs/brand/brandkit.jsx` (relative to the project root AGlancer uses, e.g. `AGLANCER_PROJECT_ROOT`).
- **Override:** set `AGLANCER_BRAND_KIT_PATH` to a path relative to the project root (e.g. `brand/brandkit.jsx`).

The worker loads this file and injects it into the context for Meridian (brand), Luma (UX/UI), and Pulse (GTM). Those agents are instructed to follow the brand kit for colors, typography, voice, and copy. Use a single source-of-truth file (e.g. your design system JSX) so all three stay aligned.

---

## Phase 2: Technical and architectural design

**Goal:** Agreed tech stack, architecture, and key decisions so implementation has clear boundaries.

### Linear

- **Epic**: e.g. “Technical design & architecture”
- **Tickets** (examples):
  - Tech stack selection (framework, language, DB, hosting)
  - System architecture (high-level diagram, main components)
  - Data model / core entities
  - API design (style, auth, main endpoints)
  - Security and compliance approach
  - ADRs (Architecture Decision Records) for each major decision
- **States:** Same workflow; “Done” = decision made and documented.

### GitHub + docs

- **`docs/architecture/`**:
  - `README.md` – index of all ADRs and diagrams.
  - `ADR-001-<topic>.md` – one file per decision (context, decision, consequences).
  - Diagrams (e.g. `system-overview.png`, Mermaid in Markdown).
- **Link:** Every ADR ticket in Linear → link to the ADR file in GitHub; in the ticket description, paste the “Decision” and “Consequences” summary.
- **CHANGELOG:** Entry like “Architecture: tech stack, system design, ADRs 001–005.”

---

## Phase 3: Implementation (coding)

**Goal:** Features built in sprints, with code in GitHub and deliverables tracked in Linear.

### Linear

- **Epics** per feature area; **issues** per task (feature, bug, chore).
- **States:** Backlog → Ready for Spec → (optional Approval) → Ready to Build → In Progress → Review → Done.
- **Sprints:** Assign issues to a cycle; set cycle goal (e.g. “Auth + first API deploy”).
- **Deliverables:** In the ticket description (or first comment): “Done when …” so QA and review know what to verify.

### GitHub

- **Branch per issue:** `feature/LIN-123-add-login` or `fix/LIN-456-validation`.
- **PRs:**
  - Title: `[LIN-123] Add login flow` (so Linear links automatically if you have integration).
  - Description: Short summary, link to Linear issue, checklist (tests, docs).
  - PR template (`.github/PULL_REQUEST_TEMPLATE.md`): sections for “Linear issue”, “What changed”, “Docs updated”, “How to test”.
- **Merge:** Only after review and passing checks. Prefer squash or linear history per your team norm.
- **Releases:** Tag `v0.1.0`, `v0.2.0` from `main`; release notes = section in `CHANGELOG.md` for that version.

### Definition of done (per ticket)

- Code merged to `main` (or `develop` and then to `main`).
- Tests added/updated as needed.
- Docs updated (see [Documentation](#documentation-from-day-1)) if the change affects behavior or setup.
- Linear issue moved to **Done** and (if applicable) linked to PR/commit.

---

## Phase 4: Testing and QA

**Goal:** Quality and regression control; test work is visible and scheduled like any other work.

### Linear

- **Labels:** `qa`, `testing`, `e2e`, `regression`.
- **Tickets:** Test plans, test cases, automation tasks, bug fixes from QA.
- **States:** Same workflow; “Review” can mean “QA sign-off” before “Done”.
- **Sprint:** Reserve part of each cycle for QA and bug fixes (e.g. “Last 2 days of sprint = QA + polish”).

### GitHub

- **CI:** Run tests on every PR (unit, lint, e2e if available).
- **Docs:** `docs/runbooks/testing.md` – how to run tests locally, what’s automated, how to add tests.

### Deliverables

- Test plan or test-case list (in Linear ticket or in `docs/specs/`).
- Bugs filed as Linear issues; fix PRs reference the bug issue.

---

## Phase 5: Continuous work and deployment

**Goal:** Ongoing backlog, predictable releases, and clear deployment path.

### Linear

- **Backlog:** Prioritized list; groom regularly; break big items into sprint-sized issues.
- **Cycles:** Plan next sprint from backlog; close cycle with a short retrospective (what shipped, what slipped).
- **Releases:** Optional “Release” or “Version” field; or use labels like `release/v0.2` to group what shipped.

### GitHub

- **Environments:** e.g. `staging`, `production` (GitHub Environments or your CI).
- **Deploy:** On merge to `main` (or on tag) – run tests, build, deploy to staging; promote to production via tag or manual step.
- **Branch protection:** `main` requires PR + review + green CI.

### Documentation

- **`docs/runbooks/deployment.md`** – how to deploy, rollback, and who can do it.
- **`CHANGELOG.md`** – every release gets an entry (version, date, list of changes from Linear/PRs).

---

## Documentation from day 1

| When            | What to document | Where |
|-----------------|------------------|--------|
| Kickoff         | Project purpose, doc index | `README.md`, `docs/README.md` |
| Brand            | Name, logo, voice, assets | `docs/brand/` |
| Architecture     | Decisions, diagrams, ADRs | `docs/architecture/` |
| Features         | Specs, acceptance criteria | Linear ticket + optional `docs/specs/<feature>.md` |
| Every release    | What changed, why | `CHANGELOG.md` |
| Ops              | Deploy, test, troubleshoot | `docs/runbooks/` |

**Rule:** If it changes user-facing behavior, API, or setup, add or update docs in the same PR that changes the code.

---

## Linear ↔ GitHub linkage

- **In Linear:** Put GitHub PR link in the issue (or use Linear’s GitHub integration so PRs link automatically).
- **In GitHub:** Put Linear issue ID in PR title/description and in commit messages (`LIN-123 message`).
- **In CHANGELOG:** Reference either “Linear LIN-123” or “PR #45” so you can trace back.

---

## Agents for the full lifecycle

To have agents own brand and architecture (not just spec → build → QA → docs), add the agents described in [agents_for_new_project.md](agents_for_new_project.md): **Meridian** (brand) and **Vertex** (architect) with Linear states **Ready for Brand** and **Ready for Architecture**. Optionally add **Luma** (UX/UI) and **Pulse** (growth/marketing).

---

## Optional: Using AGlancer on this project

If this new project is managed with AGlancer (Nova, Forge, Sentinel, Scribe, Atlas):

1. **Linear:** Create issues in the same workspace/team that AGlancer’s webhook receives, or add the new project to the webhook filter.
2. **Workflow states:** Use the same state names AGlancer expects (e.g. **Ready for Spec**, **Awaiting Approval**, **Ready to Build**, **Review**, **Done**) so the right agent is triggered.
3. **Deliverables:** Nova writes the spec into the issue description; Forge and Sentinel add deliverable/QA as comments; Scribe and Atlas update project summary and docs as in [Ideal_flow.md](Ideal_flow.md).

Then the playbook above stays the same; AGlancer automates spec writing, implementation confirmation, and QA review comments on the same Linear tickets.

---

## Quick checklist: new project from scratch

- [ ] Linear: New project/team, workflow states, labels, cycles.
- [ ] GitHub: New repo, branch strategy, `README`, `docs/` + `CHANGELOG.md`, PR template.
- [ ] Phase 1: Brand epic + tickets; deliverables in `docs/brand/`, CHANGELOG entry.
- [ ] Phase 2: Architecture epic + tickets; ADRs in `docs/architecture/`, CHANGELOG entry.
- [ ] Phase 3: Implementation in sprints; PRs linked to Linear; docs updated per change.
- [ ] Phase 4: QA tickets in Linear; CI and test runbook in place.
- [ ] Phase 5: Backlog grooming, cycle planning, deployment runbook, CHANGELOG per release.

Use this playbook as the default so the team has one place for work (Linear), one for code (GitHub), and documentation that grows from day 1.
