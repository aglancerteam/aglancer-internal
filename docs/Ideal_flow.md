In the ideal AGlancer environment, a requirement should move through a **controlled pipeline**, not just “one agent does something.”

Think of it as:

**request → triage → spec → approval → implementation → review → documentation → summary**

Here’s the full flow.

# 1. Requirement enters the system

A requirement can enter from:

* you manually creating a Linear issue
* a Slack request that gets turned into a Linear issue
* a customer/internal note later
* Atlas creating follow-up work from blockers or summaries

## Example

You create a Linear issue:

**Title:** Add revision workflow for generated outputs

Status:

```text
Ready for Spec
```

That status is the trigger.

---

# 2. Orchestrator receives the event

The webhook receives the Linear update and does a few things immediately:

* stores the issue event in Supabase
* updates the `tasks` table
* checks the issue status
* routes the issue to the correct agent
* creates a job
* pushes the job to Redis
* posts a Slack message

## Example Slack message

```text
Task routed to Nova (product_manager)
Issue: Add revision workflow for generated outputs
State: Ready for Spec
Job ID: 14
```

At this point, the webhook is done.
It does not do the heavy work itself.

---

# 3. Worker picks up the job

The worker sees the Redis job and starts processing it.

For `Ready for Spec`, the assigned agent is:

**Nova**

Nova’s job is to turn the idea into a real requirement.

## Nova should produce

* **deliverable** (one clear statement of what must exist or be true to consider this ticket done)
* problem statement
* user story
* acceptance criteria
* edge cases
* assumptions
* notes for engineering

This gets stored in:

* `jobs`
* `agent_outputs`
* **Linear issue description** (spec including deliverable, so the ticket has it for the rest of the flow)

And Slack gets an update.

## Example Slack

```text
Nova completed work
Job ID: 14
Task: Add revision workflow for generated outputs
Output type: spec_draft
```

---

# 4. You review the requirement

Now the issue should move to:

```text
Awaiting Approval
```

This is where you step in.

You review:

* Nova’s spec output
* any notes/comments
* maybe ask for changes

If approved, you move the issue forward in Linear.

## Example

You change status from:

```text
Awaiting Approval
```

to:

```text
Ready to Build
```

That state change is the approval signal.

The system should:

* resolve the approval record
* note that approval is complete
* enqueue the next step

---

# 5. Forge takes over for implementation planning

Once status becomes:

```text
Ready to Build
```

the orchestrator routes to:

**Forge**

Forge’s job is not necessarily to instantly code everything in the ideal flow.
First, Forge should produce an engineering implementation draft.

## Forge should produce

* impacted modules
* implementation steps
* API/data changes
* validation concerns
* testing notes
* technical risks
* **deliverable confirmation** (how the spec deliverable was met)

That output gets stored, posted to Slack, and **posted as a comment on the Linear issue** when the work is moved to Review (so the ticket has a clear record of what was done).

## Example Slack

```text
Forge completed work
Job ID: 18
Task: Add revision workflow for generated outputs
Output type: engineering_draft
```

In a more advanced flow, Forge can then proceed to actual implementation tasks.

---

# 6. Optional sub-splitting into child tasks

In the ideal environment, Forge or Atlas can split larger work into sub-issues.

## Example

A requirement might become:

* backend API for revisions
* UI state for revision requests
* persistence changes
* audit trail
* notification updates

These can be created as separate Linear child issues or subtasks.

That makes the system scalable.

---

# 7. QA / review stage

Once build work is complete, the issue moves to:

```text
Review
```

This routes to:

**Sentinel** later, when you activate QA/security

Sentinel checks:

* expected flow
* missing validation
* regression risks
* edge cases
* failure scenarios
* **deliverable verified** (yes/no; confirm the spec deliverable was met)

Sentinel’s review (including deliverable verified) is **posted as a comment on the Linear issue**.

If issues are found:

* task goes back to build
* comments/notes are saved

If all good:

* task moves toward done or approval

---

# 8. Done triggers Scribe

When status becomes:

```text
Done
```

the system routes to:

**Scribe**

Scribe updates the project brain:

* `project_summary.md`
* `active_workstreams.md`
* decision notes if needed
* completion summaries

This is what keeps your AI team aligned long-term.

Without Scribe, work gets done but knowledge gets lost.

---

# 9. Atlas watches the whole system

Atlas is not the main doer in the feature flow. Atlas is the coordinator.

Atlas should:

* summarize what moved today
* identify blocked work
* highlight stale issues
* point out pending approvals
* recommend next priorities

Atlas helps you avoid becoming the bottleneck.

---

# The ideal requirement flow in one line

## Normal feature flow

```text
Linear Issue Created
→ Ready for Spec
→ Nova creates spec
→ Awaiting Approval
→ You approve by moving status
→ Ready to Build
→ Forge creates engineering draft / implementation
→ Review
→ Sentinel validates
→ Done
→ Scribe updates docs
→ Atlas summarizes progress
```

---

# Example end-to-end scenario

Let’s say the requirement is:

**“Allow users to request one revision after an AI output is generated.”**

## Step A — You create issue in Linear

Title:

```text
Add one-click revision workflow for generated outputs
```

Status:

```text
Ready for Spec
```

## Step B — Nova runs

Nova produces:

* **deliverable** (one clear statement of what will confirm the work is done — stored in the ticket description)
* user problem: outputs may need refinement
* user story
* acceptance criteria:

  * user sees “Request Revision”
  * revision request is linked to original task
  * revised output is stored
* edge cases:

  * multiple revisions
  * empty revision reason
  * failed revision generation

## Step C — You review

Move issue to:

```text
Awaiting Approval
```

Then after review:

```text
Ready to Build
```

## Step D — Forge runs

Forge produces:

* new revision endpoint
* DB schema change or relation
* update results page action
* worker support for revision jobs
* audit trail notes

## Step E — Review

Sentinel checks:

* can revision be abused?
* can user submit empty revision?
* what happens if original output is missing?

## Step F — Done

Scribe updates docs:

* feature summary
* workstream
* implementation note

## Step G — Atlas summary

Atlas posts:

```text
Completed: revision workflow requirements and implementation draft
Pending: QA validation
Blocked: none
```

---

# Why this flow is ideal

Because it gives you:

## Clear ownership

Each phase belongs to one agent.

## Human control

You approve at critical points.

## Traceability

Everything is tied to Linear + Supabase + Slack.

## Scalability

Work can split into multiple jobs later.

## Knowledge retention

Scribe captures what happened.

---

# Agent responsibilities in the ideal requirement flow

## Nova

Turns ideas into usable requirements

## Forge

Turns requirements into engineering plans and later implementation

## Sentinel

Validates quality and risk

## Scribe

Captures knowledge and updates docs

## Atlas

Coordinates and summarizes

## You

Approve, reject, reprioritize, and make product decisions

---

# What should happen automatically vs manually

## Automatic

* webhook intake
* task routing
* job creation
* Slack updates
* output storage
* docs updates
* daily summaries

## Manual or approval-based

* requirement approval
* major scope changes
* deployment decisions
* product direction
* anything risky or unclear

---

# The maturity model

## Current stage

You have:

* intake
* routing
* queue
* Nova/Forge/Scribe/Atlas basic loops

## Next ideal stage

Add:

* real Claude execution for all key agents
* better approval states
* child task generation
* QA loop
* scheduled Atlas operations

## Later

Add:

* Luma for UX
* Pulse for growth/launch
* Architect for building new internal agents
* automatic Linear issue creation from summaries/blockers

---

# Best practical version for you right now

For now, the ideal requirement flow should be:

```text
Ready for Spec → Nova
Awaiting Approval → You
Ready to Build → Forge
Done → Scribe
Daily Summary / Blocked → Atlas
```

That’s enough to feel like a real AI team without too much complexity.

The next best thing to build after understanding this flow is the **real Claude-powered execution for Forge**, so both Nova and Forge become genuinely useful.
