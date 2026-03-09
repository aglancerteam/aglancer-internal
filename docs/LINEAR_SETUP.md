# Linear setup for AGlancer agents

Use this when configuring your Linear team so that all agents (Switch, Nova, Meridian, Vertex, Luma, Pulse, Forge, Sentinel, Scribe) are triggered by the right issue states.

---

## Where to configure

**Settings → [Your team] → Workflow** (or **Issue statuses** / **Workflow states**).

Create or edit **states** and assign each to a **state type** (category).

---

## State types (categories) in Linear

Linear groups states into types. Use these as the **category** for each state:

| State type   | Use for |
|-------------|---------|
| **Backlog** | Not yet picked up (e.g. Backlog, Icebox). |
| **Unstarted** | Ready to start (e.g. Todo). |
| **Started** | Work in progress — any state where an agent or human is doing work. |
| **Completed** | Done. |
| **Canceled** | Canceled, Won't do, Duplicate. |

All “Ready for …” and “In Progress” and “Review” states belong in **Started**.

---

## States to create (and their category)

Create these **workflow states** and set the **state type** as below.

### Existing (for reference)

| State                | State type | Agent / use |
|----------------------|------------|-------------|
| Backlog              | Backlog    | —           |
| Todo                 | Unstarted  | —           |
| Ready for Spec       | **Started**| Nova        |
| Awaiting Approval    | **Started**| (approval)  |
| Ready to Build       | **Started**| Forge       |
| In Progress          | **Started**| (building)  |
| Review               | **Started**| Sentinel    |
| Done                 | Completed  | Scribe      |
| Canceled             | Canceled   | —           |

### Triage (auto-routing)

When an issue is in **Triage**, the **Switch** agent runs, reads the ticket, and updates the issue to the appropriate status (e.g. Ready for Spec, Ready for Brand). That triggers the webhook again and the right content agent runs.

| State   | State type   | Agent  |
|---------|--------------|--------|
| **Triage** | **Unstarted** or **Started** | Switch |

### New states for the 4 content agents

Add these four states and set **State type = Started** for each:

| State                   | State type | Agent    |
|-------------------------|------------|----------|
| **Ready for Brand**     | **Started**| Meridian |
| **Ready for Design**    | **Started**| Luma     |
| **Ready for Architecture** | **Started**| Vertex   |
| **Ready for GTM**       | **Started**| Pulse    |

---

## Summary: what to do in Linear

1. Open your team’s **Workflow** (issue statuses) in Linear.
2. **Triage (optional):** Add state **Triage** (State type: **Unstarted** or **Started**). Moving an issue to Triage runs Switch, which sets the issue to the right status (e.g. Ready for Spec, Ready for Brand).
3. For each of the four states below, **add a new state** (if it doesn’t exist) and set its **category/type** to **Started**:
   - **Ready for Brand**
   - **Ready for Design**
   - **Ready for Architecture**
   - **Ready for GTM**
4. Save. **Triage** → Switch updates status; **Ready for …** → the corresponding agent runs (Nova, Meridian, Luma, Vertex, Pulse, or Forge).

No new categories are required — only new **states** inside existing categories.
