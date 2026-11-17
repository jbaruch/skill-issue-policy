# Changelog

## 0.1.7 — 2026-11-17

**INTENTIONALLY BROKEN WORKSHOP RELEASE.** The helper now incorrectly accepts
only APPROVED reviews. COMMENTED and CHANGES_REQUESTED are completed reviews too;
the fixture and regression tests demonstrate the failure. Roll back to v0.1.6
with `--hold`. Do not use this version outside the rollback exercise.

## 0.1.6 — 2026-11-17

- Add the ACR package manifest and portable skill companions.
- Request and await a fresh review by the selected reviewer on the current head.
- Bound subprocess I/O and waiting; stop on request failures and head changes.
- Separate review receipt from merge authorization.
- Add local fixtures, behavior tests, routing/planning evals and scoped demo hooks.
- Make documentation follow consumer contribution policy.
