"""Regressions: fresh reviewer/head identity, transport failures, bounded wait."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("await_review", ROOT / "skills/fix-the-ticket/scripts/await_review.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def review(identity=2, author=mod.REVIEWER, head="abc", state="APPROVED"):
    return {"id": identity, "user": {"login": author}, "commit_id": head,
            "state": state, "submitted_at": "2026-11-17T12:00:00Z",
            "body": "Inspect inline threads before merging.", "html_url": "https://example.invalid/review"}


class Clock:
    def __init__(self): self.now = 0
    def __call__(self): return self.now
    def sleep(self, seconds): self.now += seconds


class Transport:
    def __init__(self, snapshots, *, error=None, final_head=None):
        self.snapshots = iter(snapshots)
        self.current = None
        self.error, self.final_head, self.requests = error, final_head, []
    def snapshot(self):
        self.current = next(self.snapshots, self.current)
        return self.current
    def head(self): return self.final_head or self.current[0]
    def request(self, reviewer):
        self.requests.append(reviewer)
        if self.error: raise self.error


class AwaitTests(unittest.TestCase):
    def run_wait(self, snapshots, **kwargs):
        clock = Clock()
        transport = Transport(snapshots, **kwargs)
        result = mod.await_review(transport, reviewer=mod.REVIEWER,
                                  deadline=3, interval=1, clock=clock, sleep=clock.sleep)
        return result, transport, clock

    def test_waits_past_old_review_until_new_review(self):
        old, new = review(1), review(2)
        result, transport, clock = self.run_wait([
            ("abc", [old]), ("abc", [old]), ("abc", [old, new])])
        self.assertEqual(result["review_id"], 2)
        self.assertEqual(clock.now, 1)
        self.assertEqual(transport.requests, [mod.REVIEWER])

    def test_ignores_different_reviewer_and_commit(self):
        result, _, clock = self.run_wait([
            ("abc", []), ("abc", [review(author="someone-else"), review(3, head="old")]),
            ("abc", [review(4)])])
        self.assertEqual(result["review_id"], 4)
        self.assertEqual(clock.now, 1)

    def test_ignores_pending_review(self):
        result, _, clock = self.run_wait([
            ("abc", []), ("abc", [review(state="PENDING")]), ("abc", [review()])])
        self.assertEqual(clock.now, 1)
        self.assertTrue(result["received"])

    def test_does_not_depend_on_api_order(self):
        result, _, _ = self.run_wait([("abc", []), ("abc", [review(9), review(2)])])
        self.assertEqual(result["review_id"], 9)

    def test_changed_head_refuses(self):
        with self.assertRaisesRegex(mod.ReviewError, "head changed"):
            self.run_wait([("abc", []), ("def", [review(head="def")])])

    def test_final_head_is_rechecked(self):
        with self.assertRaisesRegex(mod.ReviewError, "final check"):
            self.run_wait([("abc", []), ("abc", [review()])], final_head="def")

    def test_request_error_stops(self):
        with self.assertRaisesRegex(mod.ReviewError, "request rejected"):
            self.run_wait([("abc", [review(1)])], error=mod.ReviewError("request rejected"))

    def test_old_review_alone_times_out(self):
        clock = Clock()
        transport = Transport([("abc", [review(1)])])
        with self.assertRaisesRegex(mod.ReviewError, "timeout"):
            mod.await_review(transport, reviewer=mod.REVIEWER, deadline=2.5,
                             interval=2, clock=clock, sleep=clock.sleep)
        self.assertEqual(clock.now, 2.5)

    def test_changes_requested_is_not_merge_permission(self):
        result, _, _ = self.run_wait([("abc", []), ("abc", [review(state="CHANGES_REQUESTED")])])
        self.assertEqual(result["state"], "CHANGES_REQUESTED")
        self.assertFalse(result["merge_authorized"])
        self.assertIn("inline threads", result["body"])

    def test_gh_failure_is_not_ignored_and_calls_are_bounded(self):
        github = mod.GitHub("test/repo", 1, mod.time.monotonic() + 20)
        with patch.object(mod.subprocess, "run", side_effect=subprocess.CalledProcessError(1, "gh")) as run:
            with self.assertRaises(mod.ReviewError): github.request(mod.REVIEWER)
        self.assertTrue(run.call_args.kwargs["check"])
        self.assertLessEqual(run.call_args.kwargs["timeout"], 15)

    def test_cli_fixture(self):
        result = subprocess.run([sys.executable, str(ROOT / "skills/fix-the-ticket/scripts/await_review.py"),
            "7", "--repo", "workshop/brickbox", "--fixture", str(ROOT / "skills/fix-the-ticket/fixtures/review.json"),
            "--interval", "0.001", "--timeout", "0.2"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["review_id"], 12)

    def test_invalid_interval_refuses(self):
        for value in ("0", "-1", "nan", "inf"):
            result = subprocess.run([sys.executable, str(ROOT / "skills/fix-the-ticket/scripts/await_review.py"),
                "7", "--repo", "workshop/brickbox", "--interval", value], capture_output=True)
            self.assertEqual(result.returncode, 2)


if __name__ == "__main__": unittest.main()
