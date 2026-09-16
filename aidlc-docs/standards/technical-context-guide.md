# Technical Context Guide

> **Purpose:** How to describe the technical environment so the AI makes informed decisions during elaboration and construction. Most technical context comes from your platform selection and EGS; this guide covers what to add beyond those defaults.

## How Technical Context Works in aidlc-kit

Unlike tools that require a separate "technical environment document," aidlc-kit assembles technical context from multiple sources:

| Source | What It Provides | When It's Set |
|--------|-----------------|---------------|
| `--platform` (aws/azure/gcp/onprem/agnostic) | Platform-specific guardrails in the EGS | At `init` time |
| EGS definition (`egs_definition.md`) | 10 categories of guardrails (see mapping below) | Customized during first session or via `import-egs` |
| Extensions (`extensions/`) | Domain-specific rules (security, API design, testing, etc.) | Installed via `extensions install` |
| Intent constraints | Project-specific limits | Written in the intent file |

You don't need to write a separate technical environment document. Instead, customize the EGS and write specific constraints in your intent.

## When to Add More Context

Add explicit technical context when:
- Your project has constraints **not covered** by the EGS categories (e.g., specific library versions, internal API contracts)
- You're working in a **brownfield** project with existing code conventions the AI must follow
- Your organization has **standards beyond the EGS** (e.g., internal framework requirements, naming conventions)

## EGS Category Mapping

Each EGS category maps to a type of technical context. If you need to specify something, customize the corresponding EGS category rather than writing a separate document.

| Technical Context | EGS Category | What to Specify |
|------------------|-------------|-----------------|
| Languages (required/permitted/prohibited) | §4 Coding Standards | Add language requirements, version constraints, prohibited languages |
| Frameworks and libraries | §4 Coding Standards | Add required frameworks, preferred libraries, prohibited dependencies |
| Cloud services (allow/disallow) | §3 Architectural Guardrails | Add service allow lists, disallow lists, approval process |
| Architecture patterns | §3 Architectural Guardrails | Add required patterns (event-driven, microservices, monolith) |
| Security requirements | §1 Security Baseline | Add auth method, encryption requirements, secrets management |
| Compliance requirements | §2 Compliance Constraints | Add regulatory frameworks (HIPAA, PCI, SOC2, GDPR) |
| Cost constraints | §6 Cost Guardrails | Add budget limits, right-sizing rules, reserved capacity |
| Testing standards | §4 Coding Standards | Add coverage targets, test types, CI/CD gates |
| Performance targets | §9 Performance Efficiency | Add latency targets, throughput requirements, resource limits |
| Reliability requirements | §8 Reliability | Add availability targets, failover requirements, backup policies |
| Sustainability constraints | §10 Sustainability | Add efficiency targets, resource optimization rules |
| AI/GenAI usage | §7 AI/GenAI Guardrails | Add model constraints, responsible AI requirements |
| Operational readiness | §5 Operational Readiness | Add monitoring, alerting, runbook requirements |

## Brownfield: Additional Context Needed

For brownfield projects, the AI needs to understand the existing codebase before it can plan changes. This context comes from **Code Elevation** (the first ritual in brownfield mode), which produces:

- **Static model**: component inventory, data model, API surface, dependency map
- **Dynamic model**: sequence diagrams showing how the system behaves
- **Technical debt inventory**: known issues triaged by severity

After Code Elevation, the AI has the technical context it needs. You don't need to write it manually.

However, you should add to your intent's Constraints section:

| Brownfield Constraint | Example |
|----------------------|---------|
| Migration rules | "Must not change the existing database schema" |
| Coexistence rules | "New code must work alongside the legacy handler during transition" |
| Feature flags | "All new features behind feature flags for gradual rollout" |
| Regression requirements | "Existing API contracts must not break (backward compatible)" |
| Prohibited changes | "Do not modify the authentication module" |

## What NOT to Specify

- **Don't repeat the EGS.** If the EGS already says "use IAM least privilege," don't repeat it in the intent.
- **Don't prescribe the architecture.** Say "must support 500 concurrent users" (constraint), not "use DynamoDB with a single-table design" (solution).
- **Don't list every library.** The AI will choose appropriate libraries during construction. Only specify libraries you require or prohibit.
- **Don't write a separate technical document.** Use the EGS + intent constraints. If you find yourself writing a multi-page technical spec, you're probably over-specifying.
