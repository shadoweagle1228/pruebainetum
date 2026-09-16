# Writing Inputs — Quick Start

> **Purpose:** Get started fast. What to provide, how much to write, minimum viable input.

## What You Need

Before starting Mob Elaboration, provide two things:

1. **An intent** (`intents/intent-primary.md`) — what to build and why
2. **Technical context** — what tools, patterns, and constraints apply (covered by EGS + platform selection + extensions)

## Intent: What to Write

| Section | What to Write | How Long |
|---------|--------------|----------|
| **Summary** | What does this feature do and why does it matter? | 3–5 sentences |
| **Users / Actors** | Who interacts with this feature? | A table or short list |
| **Key Scenarios** | User does X, system does Y | 3–5 scenarios, one line each |
| **Constraints** | Regulatory, technical, timeline, budget | Bullet list |
| **Out of Scope** | What this intent explicitly does NOT cover | Bullet list (prevents scope creep) |
| **Success Criteria** | How do you know this intent is done? | Measurable targets |

Full guide: `standards/intent-writing-guide.md`

## Technical Context: What to Write

Your platform selection (`--platform aws`) and EGS definition already provide most of the technical context. If you need to add project-specific constraints beyond the EGS, describe them in the intent's Constraints section or customize the EGS.

| Context Source | What It Covers | Your Action |
|---------------|---------------|-------------|
| `--platform` flag | Cloud provider guardrails | Choose at `init` time |
| EGS definition | 10 guardrail categories (security, compliance, architecture, etc.) | Customize during first session or via `import-egs` |
| Extensions | Domain-specific rules (security, API design, testing, etc.) | Install via `extensions install <name>` |
| Intent constraints | Project-specific limits not covered above | Write in the Constraints section |

Full guide: `standards/technical-context-guide.md`

## Minimum Viable Input

If you want to start fast and refine later, provide at least:

```markdown
# Intent: [Name]

**Type:** feature

## Summary
[One paragraph: what and why]

## Key Scenarios
1. [Most important scenario]
2. [Second scenario]

## Out of Scope
- [At least one thing you're NOT building]
```

The AI will ask clarifying questions during Mob Elaboration Phase 1 (Intent Clarification) to fill in the gaps. A minimal intent works; a detailed intent produces better results with fewer questions.
