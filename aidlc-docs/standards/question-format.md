# Question Format Standards

> Read by the AI at the start of every ritual. Defines how to ask clarifying
> questions so answers are structured, traceable, and free of contradictions.

## Format

Use numbered multiple-choice with an `[Answer]:` tag.

```
## Question 1
[Clear, specific question]

A) [Option]
B) [Option]
C) Other (please describe after [Answer]: tag)

[Answer]:
```

### Rules
- Minimum 2 meaningful options.
- Maximum 5 meaningful options.
- Include "Other" as the last option unless the question is binary or the options are exhaustive (e.g., yes/no, or selecting from a known list of existing artifacts).
- Options must be mutually exclusive and realistic. Do not invent options to fill slots.
- One topic per question.

## Delivery Mode

**In chat (default):** Present questions directly in chat when there are 10 or fewer.
Present at most 3 questions per message. Wait for answers before sending the next batch.
The user replies with the letter or a short description.

**In file (complex cases):** When there are more than 10 questions, or when a
phase involves compliance/regulatory scope, create a question file:
`aidlc-docs/{ritual}-{phase}-questions.md`. Inform the user, wait for them to
fill in the `[Answer]:` tags, then read the file back.

## Adaptive Depth

Adjust question volume based on the session's depth profile:

- **LIGHTWEIGHT:** Prefer fewer, broader questions. Combine related topics. Target ≤3 questions per phase.
- **STANDARD:** Normal behavior per the rules above.
- **THOROUGH:** May ask more granular questions. Split complex topics into separate questions rather than combining. No upper limit change.

## Contradiction and Ambiguity Detection

After collecting answers (chat or file), check for:
- **Contradictions:** logically inconsistent answers (e.g., "bug fix" scope but
  "entire codebase affected"; "low risk" but "breaking changes").
- **Ambiguities:** vague answers, hedging language ("maybe", "probably",
  "not sure"), or answers that fit multiple interpretations.

If contradictions or ambiguities are found:
1. **Standard tier:** Resolve in chat. Ask targeted multiple-choice questions referencing the original question numbers and explaining the conflict.
2. **Enterprise tier:** Create `aidlc-docs/{ritual}-clarification-questions.md` for audit trail. Reference the original question numbers and explain the conflict. Ask targeted multiple-choice questions to resolve.
3. Do NOT proceed until all contradictions are resolved.

## Validation

- If an `[Answer]:` tag is empty, ask the user to complete it before proceeding.
- If an answer does not match any option letter, ask the user to clarify.
- After clarifications, re-validate for consistency before moving on.
