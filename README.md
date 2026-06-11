# skill-issue-policy

[![tessl](https://img.shields.io/endpoint?url=https%3A%2F%2Fapi.tessl.io%2Fv1%2Fbadges%2Fjbaruch%2Fskill-issue-policy)](https://tessl.io/registry/jbaruch/skill-issue-policy)

The codified ticket-handling policy from the talk **"Skill Issue: How to Write
Skills That Actually Work"** — the same behaviour the bad `fix-the-ticket` skill
was reaching for, but decomposed into a skill, a script, and a rule and packaged
as one distributable context artifact.

## What's inside

| Kind | Name | Does |
|------|------|------|
| Skill | `fix-the-ticket` | The code-ticket lane: implement → PR → summon+await review → resolve → merge. Scoped so it doesn't fire on docs tickets. |
| Script | `scripts/await_review.py` | Deterministic summon-Copilot-review + bounded poll (no token-burning model loop). |
| Rule | `tests-before-pr` | Always-applied: no PR for a code change without tests. |

## Install

```bash
tessl install jbaruch/skill-issue-policy
```
