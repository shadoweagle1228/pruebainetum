# AI-DLC Decision Log Template

> **Version:** 2.0 | **Last Updated:** 2026-02-24  
> **Usage:** One file per session. Log every significant decision made during any AI-DLC ritual.  

---

## Session Info

| Field | Value |
|-------|-------|
| **Session Type** | [Mob Elaboration / Mob Construction / Code Elevation] |
| **Intent** | [Brief description] |
| **Date** | [YYYY-MM-DD] |
| **Participants** | [Names and roles] |
| **Facilitator** | [Name] |

---

## Decisions

### Decision 001
| Field | Detail |
|-------|--------|
| **Phase/Stage** | [e.g., Mob Elaboration — Unit Division] |
| **Decision** | [What was decided] |
| **Context** | [Why this decision was needed] |
| **Options Considered** | [What alternatives were on the table] |
| **Rationale** | [Why this option was chosen over others] |
| **Trade-offs Accepted** | [What we gave up or accepted as risk] |
| **Decided By** | [Who made the call — PO, Dev, Team consensus] |
| **Compatibility Impact** | [Brownfield only: which existing components/interfaces are affected?] |

---

### Decision 002
| Field | Detail |
|-------|--------|
| **Phase/Stage** | |
| **Decision** | |
| **Context** | |
| **Options Considered** | |
| **Rationale** | |
| **Trade-offs Accepted** | |
| **Decided By** | |
| **Compatibility Impact** | [Brownfield only] |

---

### Decision 003
| Field | Detail |
|-------|--------|
| **Phase/Stage** | |
| **Decision** | |
| **Context** | |
| **Options Considered** | |
| **Rationale** | |
| **Trade-offs Accepted** | |
| **Decided By** | |
| **Compatibility Impact** | [Brownfield only] |

---

*Copy the Decision block above for additional entries.*

---

## Notes

- Log decisions as they happen during the session — don't try to reconstruct after.
- Not every micro-decision needs logging. Focus on: Unit splits, architecture choices, NFR thresholds, risk acceptance, scope changes.
- For Brownfield sessions, the "Compatibility Impact" field traces decisions back to the compatibility impact map.
- For Construction-phase architecture decisions, use this log AND create formal ADRs in mob-construction/[bolt]/logical_design.md.
- This log provides the traceability the AI-DLC methodology requires — from Intent to decision to artifact.
