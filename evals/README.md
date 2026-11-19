# Compare plans with and without the policy

The workshop uses the saved comparison. To rerun it with Claude Code, use
the reference checkout with Python 3.11 or later. Sign
in to Claude Code first and replace `MODEL_ID` with a model your account can
use. The bad group reads the original skill from
`../skill-issue-brickbox-start`. Point `--starter PATH` at an untouched
checkout if you already edited the skill in exercise 1.

```sh
python3 evals/run.py --model MODEL_ID --trials 3 --dry-run
python3 evals/run.py --model MODEL_ID --trials 3
```

For a single classroom run, add `--trials 1 --cells fixed --scenarios code`
to both commands. Use the dry run to check the inputs before making a paid call.

The runner starts a fresh process in a temporary project for every trial. It
supplies one of three inputs: no context, the starter's broad skill, or the
repaired skills and rules together. The last input tests the policy as a bundle.
To measure the effect of a single rule, vary that rule in a separate run.

Native skill discovery is disabled and the grader stays outside the temporary
project. Managed enterprise policy may still affect the session. Record the
policy in effect and use a clean profile for rehearsal.

The docs check passes when `workflow_log.md` is absent. The code checks look
for `await_review.py` and `--repo` in that file. Read the plan to see what it
supplies as the repository value. Use the separate native routing exercise to check
for a `Skill` call, and the fixture and hook tests to see what actually executes.

Save the results, raw traces and plans. Report passes per cell alongside the
number of completed runs and errors. The saved docs baseline passed every trial,
so that check showed no improvement. Three runs per cell give you examples to
inspect and limited evidence about future runs.

Read `scenario-0/task.md` in the prompt leakage exercise. The task gives the
agent the helper and sequence the grader expects. Use it to find the leaked
answer, then use `run.py` for the comparison.
