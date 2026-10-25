"""Green/red tests for await_review's pure review-state logic.

The network parts (gh calls) are I/O; the testable core is `latest_state`,
which picks the most recent review from a list. This is what DEMO-02 writes live.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))

from await_review import latest_state, verdict_message  # noqa: E402  # pyright: ignore[reportMissingImports]


def test_no_reviews_returns_none():
    assert latest_state([]) is None


def test_latest_review_wins():
    reviews = [{"state": "CHANGES_REQUESTED"}, {"state": "APPROVED"}]
    assert latest_state(reviews) == "APPROVED"


def test_single_review():
    assert latest_state([{"state": "COMMENTED"}]) == "COMMENTED"


def test_verdict_approved():
    assert "safe to merge" in verdict_message("APPROVED")


def test_verdict_changes_requested():
    assert "Changes requested" in verdict_message("CHANGES_REQUESTED")


def test_verdict_commented():
    assert "comments" in verdict_message("COMMENTED")


def test_verdict_no_review_yet():
    assert "No review yet" in verdict_message(None)
