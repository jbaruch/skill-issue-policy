# What the context adds

`run.py` replaces the hosted evaluator for this workshop. Run from an ordinary
terminal, with Claude authentication already working. Python 3.11+; no Python
packages required. Select an explicit model ID available to your account.

```sh
python3 evals/run.py --model MODEL_ID --trials 3 --dry-run
python3 evals/run.py --model MODEL_ID --trials 3
```

The three cells are no context, the original broad starter skill, and the fixed
skills plus their rules. This measures the **bundle**; it does not isolate a
single sentence or the effect of rules independently. An additional experiment
would vary those independently. Every run is a new process and temporary project.
The rubrics and runner are never copied into the agent's project. Store result
rows, raw file-tool traces and generated plans. Managed enterprise policy can still
affect the session; record it and rehearse in a clean profile.

The documentation scenario checks whether a code-workflow plan is unnecessarily
created. Context is explicitly injected; native skill discovery is disabled to
exclude personal skills from the baseline. This is NOT an activation test.
Use the starter's separate before/after native invocation exercise for routing.
The code scenario measures the context-specific helper and repository selection
in the **written plan**. Generic bug-fixing ability does not earn policy points.
The boolean checks deliberately leave prose quality and merge-readiness reasoning
for manual review; no uncalibrated model judge invents a percentage. The runner
does not claim that a written command was executed. Run helper and hook behavior
tests separately. Review actual artifacts before interpreting a pass.

Compare each check across cells. Show counts and denominators, including run
errors. Zero lift is a legitimate result. Three trials are a teaching sample,
not a statistically precise benchmark. Run one scenario/trial live and prepare
the full sweep beforehand; never fabricate a saved result.

`scenario-0/` is retained as the **intentionally leaking** historical example:
the task tells the agent which helper and sequence the rubric expects. Its
scores are unsuitable for estimating context contribution.
