# Consistency Check Prompt

> Run this between bolts or before milestones to validate cross-artifact coherence.
> Not a ritual — a diagnostic tool. Output: `aidlc-docs/completion/consistency_report_YYYY-MM-DD.md`

```
You are a senior architect performing a consistency audit on an AI-DLC project.
Read ALL project artifacts and cross-reference them for coherence. Do not
generate new designs or fix issues — only identify and report them.

## Artifacts to Read

1. aidlc-docs/intents/ — all intent files
4. aidlc-docs/decisions/decision-log.md — all decisions
5. aidlc-docs/mob-elaboration/user_stories.md — all stories
6. aidlc-docs/mob-elaboration/unit_definitions.md — unit breakdown
7. aidlc-docs/mob-elaboration/mob_elaboration_plan.md — phase progress + Bolt Plan table
8. aidlc-docs/mob-elaboration/nfrs.md — non-functional requirements
9. aidlc-docs/mob-elaboration/risk_register.md — risk register
10. aidlc-docs/mob-construction/ — all bolt folders (domain models, logical designs, ADRs)
11. aidlc-docs/mob-construction/bolt-*/mob_construction_plan.md — per-bolt stage progress
12. aidlc-docs/retrospectives/ — all retro files (for unresolved action items)
13. For Brownfield: aidlc-docs/code-elevation/ artifacts, compatibility_impact.md,

Read each file. If a file does not exist, note it as "not yet created" and skip.

## Checks to Perform

### 1. Stories → Implementation Traceability
For each story in user_stories.md:
- Is it assigned to a Unit in unit_definitions.md?
- Is that Unit's Bolt planned in the Bolt Plan table?
- Does a bolt folder exist with artifacts that address this story?
- Flag: orphan stories (planned, never built), phantom implementations
  (bolt artifacts that don't trace to any story).

### 2. Decision Log → Design Coherence
For each decision in decision-log.md:
- Does the chosen option match what was actually implemented in the
  bolt designs (domain models, logical designs, ADRs)?
- Are there contradictions between decisions? (e.g., decision #3 says
  "use SQS" but decision #7 says "use EventBridge" for the same flow)
- Flag: contradicted decisions, unimplemented decisions, decisions
  that were superseded without being marked as such.

### 3. Bolt Dependencies → Interface Consistency
For each bolt with declared dependencies in the Bolt Plan table:
- Does the dependent bolt's logical design expose the interfaces
  this bolt expects? (e.g., API endpoints, table schemas, event contracts)
- Are there version or schema mismatches between what was designed
  in the dependency and what the consuming bolt assumes?
- Flag: missing interfaces, schema drift, undeclared dependencies.

### 4. EGS → Implementation Alignment
Read the EGS and overrides. For each completed bolt's logical design:
- Does the design comply with EGS requirements? (encryption, auth,
  logging, data classification, etc.)
- Are there violations not covered by an approved override?
  being relied upon.

### 5. Unit Definitions → Bolt Coverage
For each unit in unit_definitions.md:
- Are all its stories assigned to bolts in the Bolt Plan?
- Are there bolts that reference stories from the wrong unit?
- Flag: uncovered stories, misassigned bolts.

### 6. NFRs → Design Validation
For each NFR in nfrs.md:
- Is there evidence in the bolt designs that the NFR is addressed?
  (e.g., latency target → async processing, availability target →
  multi-AZ, cost target → serverless choices)
- Flag: NFRs with no design evidence, designs that contradict NFRs.

### 7. Retrospective Action Items
For each retro file with open action items:
- Has the action been addressed in a subsequent bolt or decision?
- Flag: stale action items carried across 2+ sessions.

## Output Format

Write the report to aidlc-docs/completion/consistency_report_YYYY-MM-DD.md
using this structure:

# Consistency Report — YYYY-MM-DD

## Summary
| Category | 🔴 Conflicts | 🟡 Drift | 🟢 Consistent |
|----------|-------------|----------|---------------|
| Stories → Implementation | | | |
| Decisions → Design | | | |
| Bolt Dependencies | | | |
| EGS Compliance | | | |
| Unit → Bolt Coverage | | | |
| NFRs → Design | | | |
| Retro Action Items | | | |

## Findings

### 🔴 Conflicts (must resolve before next bolt)
(numbered list with artifact references)

### 🟡 Drift (should address soon)
(numbered list with artifact references)

### 🟢 Consistent (no issues found)
(list categories that passed)

## Recommended Actions
(prioritized list of what to fix, with specific artifact and section references)

---

After generating the report, present the summary table and any 🔴 Conflicts
to the user.

If there are NO 🔴 Conflicts: say "No critical issues. Safe to proceed with
the next bolt." Log any 🟡 Drift items as decisions to watch.

If there ARE 🔴 Conflicts, ask:
"There are [N] conflicts that should be resolved before the next bolt.
Insert a Consistency Bolt (CB-N) into the Bolt Plan? (yes / no, I'll fix
them manually / no, defer to next bolt)"

If yes — Consistency Bolt flow:
1. Add a row to the Bolt Plan table in mob_elaboration_plan.md:
   | CB-N | — | Resolve consistency report YYYY-MM-DD | [bolts that caused conflicts] | ~Xh | ⬜ Pending |
2. Walk through each 🔴 Conflict one by one:
   a) Present the conflict with artifact references.
   b) Propose a fix (update design, align interface, correct decision,
      fix code, add missing artifact).
   c) Get user approval or alternative direction.
   d) Apply the fix to the actual artifacts and/or code.
   e) Log the resolution as a decision in decision-log.md.
3. After all conflicts are resolved, re-run ONLY the checks that had
   🔴 findings to verify resolution. If new issues surface, repeat.
4. Mark the CB-N row as ✅ Done in the Bolt Plan table.
5. Update the consistency report with a "Resolution" section listing
   what was fixed and verified.

If "no, I'll fix them manually": log each conflict as a decision with
status "pending manual resolution" and continue.

If "no, defer": log each conflict as a decision with status "deferred"
and a note that the next bolt may be affected. Continue.
```
