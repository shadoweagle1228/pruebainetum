# Extensions

Extensions are cross-cutting rules that the AI enforces at every phase and stage
of an AI-DLC ritual. They work alongside (not instead of) the standard prompt
instructions.

## How It Works

1. Install an extension: `aidlc-kit extensions install <name>`
2. During pre-flight, the AI scans this directory for `.md` files.
3. Each extension's rules are enforced as **blocking constraints**: a stage
   cannot complete until all applicable rules pass or are marked N/A.
4. Non-compliant findings are logged in `aidlc-docs/audit/audit-log.md`.

The AI may also suggest extensions during Mob Elaboration based on your intent.

## Managing Extensions

```bash
aidlc-kit extensions list              # show available extensions
aidlc-kit extensions install security  # install into this project
aidlc-kit extensions remove security   # remove from this project
```

## Adding Your Own

Drop any `.md` file in this directory following the format:

```markdown
# Extension Name

## Overview
What this extension enforces and why.

## Rule EXT-01: Rule Name
**Rule**: What must be true.
**Verification**: How to check it.

## Enforcement Integration
Summary of how rules apply across stages.
```

## Removing Extensions

Run `aidlc-kit extensions remove <name>` or delete the file directly.
