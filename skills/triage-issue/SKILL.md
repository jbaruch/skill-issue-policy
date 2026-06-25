---
name: triage-issue
description: Classify an incoming ticket — bug, feature, docs, or question — and route it to the right lane before any work starts. Use when triaging a new issue, sorting the backlog, or deciding how to handle a ticket.
---

# Triage Issue

This skill is an action router — read the ticket, pick the one classification that fits, and route. Do not run other steps; do not parallelize.

## Step 1 — Read the ticket

Read the title and body. Identify the core ask: is the reporter describing broken behavior, requesting new capability, asking about documentation, or asking a usage question?

## Step 2 — Classify

Pick exactly one:

- **bug** — existing behavior is wrong (error, crash, incorrect result).
- **feature** — new capability or enhancement to existing behavior.
- **docs** — a documentation gap or fix only, no source change.
- **question** — a support/usage question; no change to the project is needed.

When a ticket spans categories, classify by the change it requires: a feature request that also needs docs is a **feature** (the docs follow the code).

## Step 3 — Route

- **bug** / **feature** → invoke `Skill(skill: "fix-the-ticket")` with the ticket context.
- **docs** → invoke `Skill(skill: "update-docs")`.
- **question** → answer inline from the project's docs and close; do NOT open a PR.

If the classification is genuinely ambiguous after Step 2, state the two candidates and ask the reporter one clarifying question before routing.
