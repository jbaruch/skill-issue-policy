---
name: fix-the-ticket
description: Handle application CODE tickets: bugs and features that need implementation, tests, and a reviewed pull request. Use for changes to application behavior. For documentation-only tasks use update-docs instead. Context-artifact authoring is outside this skill.
---

# Fix the ticket

This skill owns application code changes. A documentation-only ticket belongs to
`update-docs`, including a README quickstart. Respect the user's requested scope:
planning a workflow never authorizes creating or merging a real PR.

## Implement and test

Use a feature branch. Reproduce the bug with a failing test, implement the change,
and run the relevant tests. The always-loaded `tests-before-pr` rule supplies
policy; loading prose does not itself enforce it. Write down the test result.

## Open a PR when authorized

Open the PR only when the task authorizes it and tests pass. Resolve the target
repository explicitly; do not infer it from this skill's installation location.

## Request and await review

Resolve `skill_dir` from the absolute path of the **loaded SKILL.md**, not the
consumer working directory. The helper and fixture are inside that directory,
so the lookup works from both this source tree and an ACR installation.

Run the companion with Python 3.11 or newer:

```text
python3 <skill_dir>/scripts/await_review.py <pr-number> --repo <owner/repository>
```

Its module docstring and `--help` own the CLI contract. Exit 0 means a new review
by the requested reviewer arrived for the captured PR head. Read its JSON,
including body, state, review id and head SHA. It never authorizes a merge.
On a nonzero exit, report the error and stop; do not replace it with a model
polling loop. A changed head needs a new invocation against that head.

For workshop practice only, use the bundled synthetic fixture:

```text
python3 <skill_dir>/scripts/await_review.py 7 --repo workshop/brickbox --fixture <skill_dir>/fixtures/review.json --interval 0.01
```

Fixture mode cannot contact GitHub and is not evidence of a real review.

## Resolve feedback and verify merge readiness

Read the review and inline threads; a COMMENTED review may still contain blocking
feedback. Address feedback, run tests, push only when authorized, then request a
new review for the new commit. Before any authorized merge, freshly verify the
current head, required reviews, unresolved threads, CI, and branch protection.
Do not equate review receipt, exit 0, or a green workflow with merge permission.
Stop when a required gate is unresolved. Workshop exercises never merge real PRs.
