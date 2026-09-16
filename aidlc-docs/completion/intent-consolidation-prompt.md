# Intent Consolidation Prompt

> **When to use:** After all bolts for the current intent are complete, before running `aidlc-kit archive`.
> Paste this prompt into your AI session to generate a summary of the completed intent.

---

## Prompt

You are consolidating a completed AI-DLC intent into a summary document for future reference.

### Instructions

1. Read the following artifacts in order:
   - `aidlc-docs/intents/intent-primary.md` — the intent definition
   - `aidlc-docs/mob-elaboration/mob_elaboration_plan.md` — elaboration plan (stories, units, bolts)
   - `aidlc-docs/decisions/decision-log.md` — all decisions made during this intent
   - `aidlc-docs/retrospectives/` — all retro files
   - `aidlc-docs/mob-construction/bolt-*/mob_construction_plan.md` — per-bolt construction plans
   - For brownfield: also read `aidlc-docs/code-elevation/` artifacts

2. Produce a single markdown document with these sections:

```markdown
# Intent Summary: <intent name>

> Completed: <date> | Mode: <greenfield|brownfield> | Platform: <platform>

## 1. Scope
What this intent set out to build. 2-3 sentences max.

## 2. What Was Built
- Units delivered (list with one-line descriptions)
- Key components, services, or modules created
- Integration points exposed (APIs, events, shared resources)

## 3. Architecture Decisions
Carry forward every decision from the decision log that has project-wide impact.
For each: one-line summary, rationale, and any expiry date if noted.
Skip intent-specific tactical decisions (e.g., "split story X into two bolts").

## 4. Patterns & Conventions
Coding patterns, naming conventions, folder structures, or design patterns
the team established during this intent that future intents should follow.

## 5. Technical Debt
Items acknowledged but deferred. Include severity and any context on why they were deferred.

## 6. Lessons Learned
Distilled from retrospectives. Focus on actionable insights, not session logistics.

## 7. Dependencies & Integration Surface
What future intents need to know to connect with what was built:
- Shared tables, queues, event buses
- API contracts or schemas
- Environment variables or configuration
- IAM roles or permissions created
```

3. Save the output as: `aidlc-docs/intent-summaries/<intent-name>.md`
   - Derive `<intent-name>` from the intent filename (e.g., `intent-task-api.md` → `task-api.md`)

4. After saving, confirm to the user: "Intent summary saved. You can now run `aidlc-kit archive` to archive this intent and start the next one."
