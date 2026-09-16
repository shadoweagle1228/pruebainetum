
> **Version:** 1.1 | **Last Updated:** 2026-02-16  
> **Usage:** Define "done" for each Bolt in Enterprise engagements with Guardrails enforcement. Validate against this checklist before closing a Bolt.  
> **Covers:** Greenfield and Brownfield Enterprise Mob Construction.  

---

## Bolt Info

| Field | Value |
|-------|-------|
| **Unit** | [Unit name] |
| **Bolt** | [Bolt number/name] |
| **Scenario** | [Greenfield / Brownfield] |
| **Stories in Scope** | [List story IDs: US-001, US-002, ...] |
| **Remediation Stories in Scope** | [List: REM-001, REM-002, ... or N/A] |
| **Team** | [Team members] |
| **Planned Duration** | [X hours] |
| **Date** | [YYYY-MM-DD] |

---

## Stage Completion Gates

### Stage 1: Domain Modeling
- [ ] Domain model generated and saved in mob-construction/[current-bolt]/
- [ ] All entities, value objects, and aggregates identified
- [ ] Business rules validated by at least one developer
- [ ] Integration contracts defined (if cross-Unit dependencies exist)
- [ ] Static models generated
- [ ] Entities annotated with data classification levels (EGS Section 1.6)
- [ ] Entities handling PII or Restricted data flagged
- [ ] Domain boundaries respect architectural guardrails (no shared databases, dependency direction)

#### Brownfield additions
- [ ] New domain concepts mapped to existing components from the static model
- [ ] Interactions between new and existing aggregates identified
- [ ] Each entity clearly marked as NEW or MODIFIED
- [ ] Existing domain concepts that need modification vs. extension flagged

### Stage 2 (Brownfield only): Integration Design
> Skip this section for Greenfield Bolts.

- [ ] Integration points with existing interfaces defined
- [ ] Adapter/anti-corruption layers designed where new code meets existing code
- [ ] Backward-compatible interfaces defined (existing consumers must not break)
- [ ] Data integration plan documented (migration, transformation, or dual-write)
- [ ] Rollback strategy defined (how to revert without data loss)
- [ ] Each integration decision documented as an ADR
- [ ] Integration points use encrypted channels (EGS Section 1.2)
- [ ] Service-to-service auth uses IAM roles (EGS Section 1.3)
- [ ] Guardrail remediation stories (if any) designed into the integration layer

### Stage 3: Logical Design
> Greenfield: Stage 2. Brownfield: Stage 3.

- [ ] Design patterns selected and justified
- [ ] AWS services selected and mapped to components
- [ ] NFRs from Mob Elaboration addressed in the design
- [ ] ADR written for each significant decision
- [ ] Dynamic models generated
- [ ] API contract produced (if Bolt exposes/consumes APIs): endpoint paths, request/response schemas, status codes, error shapes
- [ ] Team approved the architecture
- [ ] All selected AWS services are in the approved list and regionally available
- [ ] IAM design follows least privilege (EGS Section 1.3)
- [ ] Encryption applied to all data stores (EGS Sections 1.1, 1.2)
- [ ] Network design follows EGS Section 1.5 (private subnets, VPC endpoints, security groups)
- [ ] Observability design meets EGS Section 5.1 (metrics, logs, traces)
- [ ] Deployment strategy aligns with EGS Section 5.4

#### Brownfield additions
- [ ] Existing infrastructure and services reused where possible
- [ ] Any new service justified over extending an existing one
- [ ] Design respects the deployment strategy from Bolt Planning (canary, feature flag, blue-green)

### Stage 4: Code Generation
> Greenfield: Stage 3. Brownfield: Stage 4.

- [ ] Executable code generated and committed
- [ ] Infrastructure as Code generated (CloudFormation / CDK / Terraform)
- [ ] Code follows clean, simple, explainable principles
- [ ] Code reviewed by at least one developer (not just AI-generated and accepted)
- [ ] No secrets or credentials in code (EGS Section 1.4)
- [ ] IAM permissions follow least privilege
- [ ] Structured JSON logging with mandatory fields (EGS Section 4.3)
- [ ] Error handling with correlation IDs, no silent catches (EGS Section 4.2)
- [ ] Explicit dependency versions, no "latest" (EGS Section 4.4)
- [ ] IaC includes all mandatory resource tags (EGS Section 5.5)
- [ ] IaC passes security scanning (cfn-nag, Checkov patterns)
- [ ] Health check endpoints included (EGS Section 5.2)
- [ ] No PII in log output
- [ ] Guardrail remediation stories implemented (if any in this Bolt)

#### Brownfield additions
- [ ] New code clearly separated from modifications to existing code
- [ ] Modifications to existing files are minimal and surgical
- [ ] Feature flags implemented for new functionality
- [ ] Adapter/anti-corruption layer code generated per Integration Design
- [ ] Existing codebase conventions followed (naming, structure, patterns)
- [ ] Remediation before/after state matches remediation criteria (if applicable)

### Stage 5: Test & Validation
> Greenfield: Stage 4. Brownfield: Stage 5.

- [ ] Functional tests generated and passing
- [ ] Security tests generated and passing
- [ ] Performance tests generated and passing (if applicable to this Bolt)
- [ ] All acceptance criteria from stories covered by tests
- [ ] Contract conformance validated (if API contract exists): backend responses, frontend calls, and test mocks all match the contract — **BLOCKER**
- [ ] Edge cases from Risk Register covered
- [ ] Test results documented
  - [ ] Encryption validation (no unencrypted stores or channels)
  - [ ] IAM validation (no wildcards, least privilege)
  - [ ] Tagging validation (all mandatory tags present)
  - [ ] Secrets validation (no secrets in code/config)
  - [ ] Logging validation (structured, mandatory fields, no PII)
  - [ ] TLS validation (all endpoints encrypted)

#### Brownfield additions
- [ ] Regression tests passing (existing functionality NOT broken) — **BLOCKER**
- [ ] Integration tests passing (new code interacts correctly with existing components)
- [ ] Backward compatibility tests passing (existing API consumers unaffected) — **BLOCKER**
- [ ] Performance baseline compared (no degradation to existing system)
- [ ] Remediation-specific tests passing (if remediation stories in this Bolt)

---

## Artifact Checklist

| Artifact | Location | Status |
|----------|----------|--------|
| Domain Model | aidlc-docs/mob-construction/[current-bolt]/ | [ ] Complete |
| Integration Design (Brownfield) | aidlc-docs/mob-construction/[current-bolt]/ | [ ] Complete / N/A |
| Logical Design | aidlc-docs/mob-construction/[current-bolt]/ | [ ] Complete |
| ADRs (with EGS references) | aidlc-docs/mob-construction/[current-bolt]/ | [ ] Complete |
| Source Code | [project_folder]/ | [ ] Complete |
| Adapter Layers (Brownfield) | [project_folder]/adapters/ | [ ] Complete / N/A |
| IaC | [project_folder]/infra/ | [ ] Complete |
| Tests | [project_folder]/tests/ | [ ] Complete |
| Regression Tests (Brownfield) | [project_folder]/tests/regression/ | [ ] Complete / N/A |
| Test Results | aidlc-docs/plans/ | [ ] Complete |

---

## Dual Definition of Done



---

## Quality Gates

| Gate | Criteria | Pass? |
|------|----------|-------|
| **Functional** | All acceptance criteria from stories have passing tests | [ ] |
| **Security** | No critical/high vulnerabilities in static analysis | [ ] |
| **Performance** | Meets NFR thresholds defined in Mob Elaboration | [ ] |
| **Architecture** | All design decisions documented as ADRs with EGS references | [ ] |
| **Traceability** | Every story maps to code, every code maps to tests | [ ] |


| Gate | Criteria | Pass? |
|------|----------|-------|
| **Encryption** | All data at rest and in transit encrypted per EGS — BLOCKER | [ ] |
| **IAM** | No wildcard permissions, least privilege enforced — BLOCKER | [ ] |
| **Secrets** | No secrets in code, config, or environment variables — BLOCKER | [ ] |
| **Tagging** | All resources have mandatory tags per EGS | [ ] |
| **Logging** | Structured JSON, mandatory fields, no PII in logs | [ ] |


### Brownfield Quality Gates
> Skip for Greenfield Bolts.

| Gate | Criteria | Pass? |
|------|----------|-------|
| **Regression** | All existing functionality tests passing — BLOCKER | [ ] |
| **Backward Compatibility** | Existing API consumers receive same responses — BLOCKER | [ ] |
| **Integration** | New code interacts correctly with existing components | [ ] |
| **Performance Baseline** | No degradation vs. pre-change baseline | [ ] |
| **Feature Flags** | New functionality toggleable without redeployment | [ ] |
| **Remediation** | All remediation stories validated with before/after tests (if applicable) | [ ] |

---

## Bolt Closure

| Field | Value |
|-------|-------|
| **All gates passed?** | [Yes / No — list blockers] |
| **All Mandatory guardrail gates passed?** | [Yes / No — list violations] |
| **Actual Duration** | [X hours] |
| **Stories Completed** | [List] |
| **Remediation Stories Completed** | [List or N/A] |
| **Stories Deferred** | [List — with reason] |
| **Next Bolt Needed?** | [Yes — scope / No — Unit complete] |
| **Ready for Operations?** | [Yes — if last Bolt / No] |
| **Deployment Strategy** | [Blue-green / Canary / Feature flag / Direct] |
| **Closed By** | [Name] |
| **Date** | [YYYY-MM-DD] |

---

## Notes

- A Bolt is NOT done until all quality gates pass. No exceptions.
- Enterprise Bolts have two categories of blockers: standard quality gates AND Mandatory guardrail gates. Both must pass.
- Brownfield Enterprise Bolts have three categories: standard + guardrails + regression/compatibility. All must pass.
- If a story can't be completed in this Bolt, defer it explicitly; don't leave it half-done.
- If the Bolt exceeds planned duration by >50%, stop and reassess scope for the next Bolt.
- This template is the contract between the team and the facilitator for what "done" means in an Enterprise engagement.
