# Error Handling and Recovery Procedures

> Load this file at the start of every AI-DLC session. It defines how to handle
> errors, recover from interruptions, and escalate blockers.

## Error Severity Levels

| Level | Meaning | Action |
|-------|---------|--------|
| **Critical** | Session cannot continue | Stop. Inform the user. Do not proceed until resolved. |
| **High** | Current phase/stage cannot complete as planned | Pause. Present options: resolve now, workaround, or skip with documented trade-off. |
| **Medium** | Phase can continue with workarounds | Note the issue, apply workaround, continue. Document in audit log. |
| **Low** | Minor issue, does not block progress | Log it, continue normally. |

## Phase-Specific Error Catalog

### Mob Elaboration Errors

| Error | Severity | Cause | Resolution |
|-------|----------|-------|------------|
| Intent file is blank or has placeholder text | Critical | User hasn't defined the intent | Stop. Ask user to fill `intents/intent-primary.md` before starting. |
| User provides contradictory requirements | High | Unclear scope, changing needs | Create follow-up questions to resolve contradictions. Do not proceed until resolved. |
| User gives vague or incomplete answers | Medium | Unclear what to answer | Rephrase the question with concrete examples. Flag as ambiguous in audit log. |
| Cannot decompose intent into stories | High | Intent too broad or too vague | Ask user to narrow scope or split into multiple intents. |

### Mob Construction Errors

| Error | Severity | Cause | Resolution |
|-------|----------|-------|------------|
| No elaboration plan exists | Critical | Construction started without elaboration | Stop. Run Mob Elaboration first. |
| Bolt dependencies not satisfied | High | Dependent bolt not yet complete | Reorder bolt execution or generate stubs for dependencies. |
| Generated code has syntax errors | Medium | Template or language issue | Fix immediately, validate before presenting. |
| Test generation fails | Medium | Complex logic, missing framework | Generate basic test structure, mark for manual completion. Continue. |

### Code Elevation Errors (Brownfield)

| Error | Severity | Cause | Resolution |
|-------|----------|-------|------------|
| Cannot read existing codebase | Critical | Permission issues, missing files | Ask user to verify paths and permissions. |
| Codebase too large to analyze in one pass | Medium | Large monolith | Analyze module by module. Document boundaries and assumptions. |
| Cannot determine tech stack | High | Mixed or unusual technologies | Ask user to specify primary stack and entry points. |
| Existing tests are failing | Medium | Pre-existing issues | Document as technical debt. Do not fix unless in scope. |

## Recovery Procedures

### Interrupted Session (Resume)

1. Read the plan file for the current phase/stage.
2. Identify the last completed step (last checked checkbox).
3. Verify prior steps produced their expected artifacts.
4. Resume from the next uncompleted step.
5. Log the resumption in `audit/audit-log.md`.

### Missing Artifacts from Prior Phase

1. Identify which artifacts are missing and which phase creates them.
2. If the phase was completed: regenerate the missing artifacts.
3. If the phase was not completed: return to that phase first.
4. Document the gap and recovery in `audit/audit-log.md`.

### User Wants to Restart a Phase/Stage

1. Confirm the user understands existing work will be archived.
2. Rename current artifacts with `.backup` suffix.
3. Re-execute the phase/stage from the beginning.
4. Log the restart reason in `audit/audit-log.md`.

### User Wants to Skip a Phase/Stage

1. Confirm the user understands downstream impacts.
2. Document the skip reason and accepted risks in `decisions/decision-log.md`.
3. Mark the phase/stage as "SKIPPED" in the plan.
4. Proceed to the next phase/stage.

## Escalation Rules

### Ask the User Immediately When:
- Input is contradictory or ambiguous
- A required artifact is missing and cannot be regenerated
- A decision requires business judgment (cost, timeline, scope)

### Attempt Resolution First, Then Ask When:
- Generated artifact has minor issues (formatting, naming)
- Optional information is missing
- A workaround exists but changes the approach

### Suggest Starting Over When:
- Multiple phases have cascading errors
- User requirements have changed significantly
- Architectural decisions need to be reversed

## Error Audit Logging

When an error occurs, log it in `audit/audit-log.md` using this format:

```markdown
### [Error] Phase/Stage Name — Brief Description
**Timestamp**: YYYY-MM-DD HH:MM
**Severity**: Critical | High | Medium | Low
**Description**: What went wrong
**Cause**: Why it happened
**Resolution**: How it was resolved
**Impact**: Effect on the session
```

When recovering from an interruption:

```markdown
### [Recovery] Phase/Stage Name — Session Resumed
**Timestamp**: YYYY-MM-DD HH:MM
**Issue**: What needed recovery
**Steps Taken**: What was done to recover
**Artifacts Affected**: List of files checked or regenerated
```
