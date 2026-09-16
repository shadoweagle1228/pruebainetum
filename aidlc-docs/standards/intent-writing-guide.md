# Intent Writing Guide

> **Purpose:** How to write intents that produce high-quality elaboration plans. Good intents lead to precise stories, units, and bolts. Vague intents lead to rework.

## What Makes a Good Intent

A good intent is:
- **Specific enough** to be actionable: the AI can decompose it into stories without guessing
- **Broad enough** for the AI to explore the solution space: don't prescribe the implementation
- **Bounded**: clear about what's in scope and what's not

A good intent describes the **problem and goal**, not the solution. "Build a task management API with status transitions" is good. "Build a task management API using Lambda, API Gateway, and DynamoDB with a single-table design" is not, because it prescribes the architecture before the design process begins.

## Intent Structure

### Summary
One paragraph: what does this feature do and why does it matter? Include the business context, not just the technical description.

**Good:** "Build a task management API that lets teams create, assign, and track tasks through a defined lifecycle (draft → active → completed → archived). Replaces the current spreadsheet-based tracking that breaks down above 50 concurrent users."

**Bad:** "Build a task API." (Too vague. The AI will spend Phase 1 asking questions you could have answered upfront.)

### Users / Actors
Who interacts with this feature? Include their role and what they need.

| Actor | What They Need |
|-------|---------------|
| Team Member | Create tasks, update status, assign to others |
| Team Lead | View team workload, reassign tasks, set priorities |
| System | Send notifications on status changes, enforce lifecycle rules |

### Key Scenarios
The 3–5 most important user interactions. Each scenario is one sentence: actor does X, system does Y.

1. Team member creates a task with title, description, and assignee → system validates, assigns draft status, notifies assignee
2. Assignee moves task from draft to active → system validates transition, logs timestamp
3. Team lead views all tasks filtered by status and assignee → system returns sorted list with pagination

### Constraints
Known limits that the AI must respect. These are hard boundaries, not preferences.

- Must run on AWS (already covered by `--platform aws`, but mention account-specific constraints)
- Must support 500 concurrent users with p95 latency < 300ms
- Must not store PII beyond user email (GDPR constraint)
- Budget: < $200/month at steady state

### Out of Scope
What this intent explicitly does NOT cover. This is critical for preventing scope creep during elaboration.

- User authentication (handled by a separate identity service)
- File attachments on tasks (Phase 2)
- Mobile app (API-first, mobile comes later)
- Reporting and analytics dashboard (separate intent)

### Success Criteria
How do you know this intent is done? Measurable, verifiable conditions.

- All CRUD operations work with < 300ms p95 latency
- Status transitions enforce the defined lifecycle (no invalid transitions)
- Soft-delete preserves data for 90 days
- API documentation generated and accessible

## Common Mistakes

| Mistake | Why It's Bad | Fix |
|---------|-------------|-----|
| Prescribing the solution | "Use DynamoDB single-table" removes the AI's ability to evaluate alternatives during design | Describe the requirement: "Must support flexible queries by status, assignee, and date range" |
| Vague scope | "Build a task system" could mean anything from a TODO list to Jira | Add key scenarios and out-of-scope to bound it |
| Missing constraints | No performance, cost, or compliance requirements | The AI will assume none exist and design without guardrails |
| No out-of-scope | Everything is implicitly in scope | The AI will ask about features you don't want, wasting elaboration time |
| Too many intents at once | "Build task management, notifications, and a dashboard" | One intent per bounded capability. Use separate intents and the `intent create` command. |

## Worked Examples

### Greenfield Example: Task Management API

```markdown
# Intent: Task Management API

**Type:** feature

## Summary
Build a task management API that lets teams create, assign, and track tasks
through a defined lifecycle (draft → active → completed → archived). Replaces
the current spreadsheet-based tracking that breaks down above 50 concurrent
users. API-first design; frontend will be built as a separate intent.

## Users / Actors
- Team Member: create tasks, update status, assign to others
- Team Lead: view team workload, reassign, set priorities
- System: notifications on status changes, lifecycle enforcement

## Key Scenarios
1. Team member creates a task with title, description, assignee → draft status
2. Assignee moves task draft → active → completed
3. Team lead filters tasks by status + assignee with pagination
4. Admin soft-deletes a task → hidden from queries, retained 90 days
5. System rejects invalid status transition (e.g., draft → archived)

## Constraints
- 500 concurrent users, p95 < 300ms
- No PII beyond user email
- Budget < $200/month at steady state
- Must integrate with existing SSO (OAuth 2.0, tokens provided by identity service)

## Out of Scope
- User authentication (separate identity service)
- File attachments (Phase 2)
- Mobile app (API-first, mobile later)
- Reporting dashboard (separate intent)
- Real-time collaboration / WebSockets (Phase 2)

## Success Criteria
- CRUD operations with < 300ms p95
- Status lifecycle enforced (no invalid transitions)
- Soft-delete with 90-day retention
- API docs generated and accessible
- 80% test coverage on business logic
```

### Brownfield Example: Add Notifications to Legacy Task System

```markdown
# Intent: Task Notification System

**Type:** feature

## Summary
Add event-driven notifications to the existing TaskFlow application. When a
task changes status or is reassigned, notify the relevant users via email and
in-app. The existing codebase has no event system; all mutations happen in a
single Lambda handler with direct DynamoDB writes.

## Users / Actors
- Task assignee: receives notification on assignment and status changes
- Task creator: receives notification when their task is completed
- Team lead: receives daily digest of overdue tasks

## Key Scenarios
1. Task assigned to user → email + in-app notification within 5 minutes
2. Task status changes → notification to assignee and creator
3. Task overdue (active > 7 days) → daily digest to team lead
4. User mutes notifications for a specific task → no further notifications

## Constraints
- Must not modify the existing task mutation flow (add events, don't rewrite)
- Existing Lambda handler is 400 lines, no tests (see Code Elevation output)
- Email via SES (already configured in the account)
- Budget: < $50/month incremental cost

## Out of Scope
- Push notifications (mobile not supported yet)
- Notification preferences UI (use defaults, add preferences in Phase 2)
- Rewriting the existing task handler (separate maintenance intent)
- SMS notifications

## Success Criteria
- Notifications delivered within 5 minutes of trigger event
- Zero impact on existing task API latency (async, not synchronous)
- Mute functionality works per-task per-user
- Daily digest sent by 08:00 local time
```

## How This Feeds Into AI-DLC

| Intent Section | Used During |
|---------------|-------------|
| Summary | Phase 1 (Intent Clarification): AI validates understanding |
| Users / Actors | Phase 2 (Story Generation): one story per actor-scenario pair |
| Key Scenarios | Phase 2 (Story Generation): scenarios become acceptance criteria |
| Constraints | Phase 4 (Risk & NFR Analysis): constraints become NFRs |
| Out of Scope | Phase 1 + Phase 2: AI uses this to reject scope creep |
| Success Criteria | Bolt completion criteria: "done" means these are met |
