# Skill Issue policy

Reference solutions for **How To Write Skills That Actually Work**, QCon
San Francisco, November 19, 2026. Use v0.2.0 for the finished skills, review
fixture and workshop hooks. The rollback lab uses v0.2.1 to show what happens
when the helper stops accepting completed comments.

## Install the known-good workshop release

Use ACR 0.6.0 and Python 3.11 or later on macOS, Linux or
[WSL](https://github.com/jbaruch/agentic-context-registry/issues/14). The labs
use local review fixtures. To try live GitHub review elsewhere, sign in with
`gh` and check that your reviewer and the required repository permissions are
available.

```sh
agent=codex                  # or claude-code or cursor
acr install github:jbaruch/skill-issue-policy@v0.2.0 --agent "$agent" --freshness none --non-interactive
acr realize
acr check
```

Start a fresh session with the agent you selected. ACR installs the skills
under `.codex/skills`, `.claude/skills`, or `.cursor/skills`. The installed
directories start with `acr__jbaruch__skill-issue-policy__`.
If you are using the starter repo, first run its
`tools/use_packaged_context.py` in the packaging clone. That moves the starter's
local `fix-the-ticket` out of the agent's search path.

For a local install rehearsal, run `acr install ../skill-issue-policy` and
`acr realize` in the packaging clone. Pass `--agent` on the first install. Use the tagged GitHub releases for the
`--hold` exercise.

## What ships

| Artifact | Responsibility |
| --- | --- |
| `fix-the-ticket` | Application code workflow; helper path anchored to the loaded skill |
| `update-docs` | Documentation work respecting the consumer's contribution policy |
| `tests-before-pr` | Always-loaded guidance; meaningful verification before a code PR |
| `evals-required` | A behavior change includes its regression scenario |
| Review companion | Waits for a fresh review from the requested reviewer on the captured head and returns JSON |
| `sandbox-publishing-only` | Denies non-sandbox calls to `mcp__workshop__publish` only |
| `record-skill` | Local completed Skill-tool events without prompts or argument text |

The `PreToolUse` hook checks the channel on `mcp__workshop__publish`. The MCP
server writes a local record in the lab. Shell commands and other publishing
tools fall outside this check.

This logger recognizes completed Claude Code Skill tool calls. On supported Claude Code versions,
a `UserPromptExpansion` hook can cover direct slash commands. To measure routing,
also count the tasks that should have used the skill. Review task outcomes
separately.

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

Use v0.2.1 only for the rollback exercise. Its review helper waits for
`APPROVED` and times out on the bundled `COMMENTED` review. Use v0.2.0 for
ordinary installs.

Run these commands in a disposable packaging clone. The unversioned install
selects the workshop's Latest release.

```sh
agent=codex
skill_root=.codex/skills      # claude-code uses .claude/skills; cursor uses .cursor/skills
skill="$skill_root/acr__jbaruch__skill-issue-policy__fix-the-ticket"
acr install github:jbaruch/skill-issue-policy --agent "$agent" --freshness none --non-interactive
acr realize
python3 "$skill/scripts/await_review.py" 7 --repo workshop/brickbox --fixture "$skill/fixtures/review.json" --interval 0.01 --timeout 0.2
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
reintroduces the failure. For the lab, leave the clone held on v0.2.0. After any version switch, run
`acr realize` to update the installed files and start a fresh agent session.
