---
alwaysApply: true
description: Every skill change ships with an eval scenario in the same PR
---

# Evals Required

- Any PR that ADDS a skill, or CHANGES a skill's behavior, MUST include an eval
  scenario under `evals/` that exercises that behavior — in the same PR.
- A skill change without a matching `evals/` scenario is a **blocking** violation:
  request changes, do not merge.
- This applies to every skill that carries LLM-side judgment. "It's small" or
  "baseline already does it" is not an exemption here — the eval is the proof, and
  it ships with the change.
