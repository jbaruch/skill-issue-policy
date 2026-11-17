---
alwaysApply: true
---

# Tests before a code PR

Before opening a PR that changes application behavior, add or verify meaningful
tests covering that behavior and run them. Record the result. An old passing
run or the mere existence of a test file is insufficient.

If verification cannot run, report the concrete limitation and leave the PR gate
unsatisfied. Respect the user's scope: a planning exercise does not authorize
external changes. Documentation follows the repository's contribution policy.

This is always-loaded guidance, not a runtime access control. Hooks and required
server-side checks enforce the specific constraints they actually inspect.
