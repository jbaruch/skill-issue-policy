"""The review trigger's `if:` gate, evaluated for each kind of pull request.

Same-repo pull requests dispatch the fleet review; fork and Dependabot pull
requests cannot read the dispatch secret, so they skip it and the scheduled
backstop reviews them.
"""
import pathlib
import re

WORKFLOW = pathlib.Path(__file__).resolve().parents[1] / ".github/workflows/review-trigger.yml"


def _condition() -> str:
    text = WORKFLOW.read_text(encoding="utf-8")
    match = re.search(r"^    if: >-\n((?:      .+\n)+)", text, re.M)
    assert match, "review-trigger.yml has no folded `if: >-` on the trigger job"
    return " ".join(line.strip() for line in match.group(1).splitlines())


def _runs(head_repo: str, actor: str) -> bool:
    """Evaluate the condition's `a == b && c != 'd'` clauses for one event."""
    context = {
        "github.event.pull_request.head.repo.full_name": head_repo,
        "github.repository": "jbaruch/skill-issue-policy",
        "github.actor": actor,
    }

    def operand(token: str) -> str:
        token = token.strip()
        if token.startswith("'") and token.endswith("'"):
            return token[1:-1]
        assert token in context, f"unknown operand in the trigger condition: {token}"
        return context[token]

    for clause in _condition().split("&&"):
        left, op, right = re.fullmatch(r"\s*(\S+)\s*(==|!=)\s*(\S+)\s*", clause).groups()
        equal = operand(left) == operand(right)
        if equal != (op == "=="):
            return False
    return True


def test_a_same_repo_pull_request_dispatches_the_review():
    assert _runs("jbaruch/skill-issue-policy", "jbaruch")


def test_a_fork_pull_request_is_skipped():
    assert not _runs("someone/skill-issue-policy", "someone")


def test_a_dependabot_pull_request_is_skipped():
    assert not _runs("jbaruch/skill-issue-policy", "dependabot[bot]")
