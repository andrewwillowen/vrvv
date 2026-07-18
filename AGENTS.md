# AGENTS.md

This file defines operating rules for **AI coding agents only** in this repository.

## 1) Execution contexts

This project uses two valid operating contexts:

1. **Local interactive context (default for this repo):** agent provides advice and focused code edits; human maintainer reviews, commits, and manages PRs.
2. **Issue-assigned autonomous context (explicitly initiated by maintainer):** agent may independently implement assigned issue work, subject to the guardrails below.

## 2) Core operating mode

- This project is **alpha**.
- Agents may make reasonable low-risk assumptions to keep progress moving.
- Agents must explicitly state assumptions they make.
- Agents must ask for clarification before making risky assumptions.

## 3) Approval-required actions

Agents must get explicit maintainer approval **before** doing any of the following:

- Implementing breaking changes.
- Modifying dependency manifests or lockfiles.
- Running database/schema migrations.
- Running destructive operations (data-destructive or environment-destructive commands).
- Pushing commits to a remote branch.

Additionally:

- In **local interactive context**, agents must not commit, push, or open/update PRs.
- In **issue-assigned autonomous context**, local commits are allowed; push/PR actions require maintainer approval.

## 4) Breaking-change policy (alpha)

Breaking changes are allowed in principle, but only with explicit approval first.  
When approved, the resulting codebase must remain internally consistent, and the same change set must include:

- Updated tests for the new behavior.
- Updated user-facing/developer-facing documentation.

## 5) Implementation standards

- Make focused, minimal-diff changes that fully solve the requested task.
- Preserve codebase consistency (types, naming, architecture, and style).
- Avoid unrelated refactors unless required for correctness.
- Reuse existing utilities/patterns before introducing new abstractions.
- Never commit secrets or credentials.

## 6) Mandatory validation

Before handoff in local context, and before any push/PR action in autonomous context, agents must run this full validation suite:

```bash
hatch test && hatch fmt --check && hatch run types:check
```

If validation fails, do not proceed to push/PR actions until failures are addressed or maintainer guidance is received.

## 7) Documentation policy

When behavior changes affect users or developer workflows, documentation updates are required in the same change set.

## 8) Git and collaboration hygiene

- Use clear commit messages that explain intent and impact.
- Do not rewrite shared history unless explicitly asked.
- Keep handoff notes or PR descriptions explicit about assumptions, risk level, and any required follow-up.
