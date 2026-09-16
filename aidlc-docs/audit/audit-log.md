# Audit Log

> **Project:** (auto-filled during session)  
> **Created:** (auto-filled during session)

---

## Log Format

Each entry follows this structure:

```
### YYYY-MM-DDTHH:MM — <Event Type>
**Phase/Stage:** <current phase or stage>  
**Description:** <what happened>  
**Artifacts Affected:** <list of files created, modified, or read>  
**User Response:** <approval, change request, or decision — verbatim if short>
```

### Event Types

| Type | When to Log |
|------|------------|
| `SESSION_START` | Beginning of a ritual session (pre-flight start) |
| `PRE_FLIGHT` | Pre-flight check results (what was read, what was found) |
| `PHASE_START` | Starting a new phase or stage |
| `PHASE_COMPLETE` | Phase or stage completed and approved by user |
| `DECISION` | User made a trade-off or architectural decision |
| `CHANGE_REQUEST` | User requested changes to a completed artifact |
| `EXTENSION_FINDING` | A blocking extension rule was triggered |
| `SESSION_END` | End of session (normal completion or pause) |

---

## Entries

(Entries are appended below by the AI during each ritual session.)
