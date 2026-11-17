# Skill Issue policy — intentionally broken v0.2.1

**Teaching regression. Use v0.2.0 outside the rollback exercise.**

Reference context library for **How To Write Skills That Actually Work**, QCon
San Francisco, November 19, 2026. This is a teaching repository.

The library separates code-ticket and documentation workflows, always-loaded
policy, deterministic review waiting, and scoped runtime hooks. It never treats
review receipt as merge permission.

## Install the known-good workshop release

ACR 0.4.3; macOS or Linux. On Windows use **WSL**: native Windows is not supported
([ACR issue #14](https://github.com/jbaruch/agentic-context-registry/issues/14)).
Python 3.11+ is needed for companions and hooks. Live GitHub review additionally
requires authenticated `gh`, reviewer availability and repository permissions.

```sh
acr install github:jbaruch/skill-issue-policy@v0.2.0 --agent claude-code --freshness none --non-interactive
acr realize
acr check
```

Start a fresh agent session. Rules are loaded from the ACR-managed block in
`CLAUDE.md`; skills land under `.claude/skills/acr__jbaruch__skill-issue-policy__*`.
Remove the starter's intentionally broad local `fix-the-ticket` from discovery
first, using its `tools/use_packaged_context.py` in a separate packaging clone.

For local rehearsal before publication, replace the GitHub source with the path
to this checkout: `acr install ../skill-issue-policy`, then `acr realize`.
Local path installs are not immutable releases and cannot demonstrate `--hold`.

## What ships

| Artifact | Responsibility |
| --- | --- |
| `fix-the-ticket` | Application code workflow; helper path anchored to the loaded skill |
| `update-docs` | Documentation work respecting the consumer's contribution policy |
| `tests-before-pr` | Always-loaded guidance; meaningful verification before a code PR |
| `evals-required` | A behavior change includes its regression scenario |
| Review companion | Fresh reviewer/head identity, bounded I/O and waiting, explicit output |
| `sandbox-publishing-only` | Denies non-sandbox calls to `mcp__workshop__publish` only |
| `record-skill` | Local completed Skill-tool events without prompts or argument text |

The gate demonstrates native hook enforcement on one structured tool. It does
not constrain arbitrary shell execution, other publishing routes, or an operator
who can edit configuration. The hook lab's MCP server writes synthetic local
records only. Actual organization-wide enforcement belongs at trusted runtime
and server boundaries.

Telemetry is deliberately partial: direct `/skillname` commands do not go through
the Skill tool. `UserPromptExpansion` can cover that separate path on supported
Claude versions. Counts are tool invocations, not successful tasks or an
activation rate; retain the denominator and track outcomes separately.

## Verify the deterministic parts

```sh
python3 -m unittest discover -s tests -v
acr validate .
python3 scripts/await_review.py 7 --repo workshop/brickbox --fixture skills/fix-the-ticket/fixtures/review.json --interval 0.01 --timeout 1
```

The fixture contains an old review, an unrelated reviewer, and a new COMMENTED
review for the captured head. Receipt succeeds without network; approval remains
false. The root script is a source-checkout compatibility wrapper. Installed
consumers use the companion in the loaded skill's directory.

Model experiments and their measurement limits are documented in [evals](evals/README.md).

## Rollback exercise

`v0.2.0` is the known-good baseline. `v0.2.1` is an **intentional workshop
regression**, not a recommended update. It incorrectly waits only for APPROVED
reviews and therefore times out on the bundled COMMENTED-review fixture.
The release must be clearly labelled as a teaching failure. Keep ordinary
consumers pinned to `v0.2.0` during the exercise.

In a disposable packaging clone, after both releases are published:

```sh
acr install github:jbaruch/skill-issue-policy --agent claude-code --freshness none --non-interactive
acr realize
python3 .claude/skills/acr__jbaruch__skill-issue-policy__fix-the-ticket/scripts/await_review.py 7 --repo workshop/brickbox --fixture .claude/skills/acr__jbaruch__skill-issue-policy__fix-the-ticket/fixtures/review.json --interval 0.01 --timeout 0.2
# Expected nonzero: the latest teaching release ignores a completed COMMENTED review.
acr install github:jbaruch/skill-issue-policy@v0.2.0 --hold
acr realize
acr check
# Repeat the same companion command: expected success, review_id=12.
acr update
acr realize
# Repeat again: the hold must keep the known-good behavior.
```

Read `agents.yaml` and `.agents/registry.lock`; record tag, commit, content hash
and hold. `acr resume github:jbaruch/skill-issue-policy` explicitly removes the
hold and follows latest again. While latest is deliberately broken, resuming
reintroduces the failure. A useful exercise predicts that before running it.
Restoring `agents.yaml` alone does not replace realized files: realize and start
a fresh agent session after every switch.

These commands describe the intended release pair, not evidence of publication.
See the instructor's preparation evidence before the room uses GitHub install.
