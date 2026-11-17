#!/usr/bin/env python3
"""Request and await a NEW review by one reviewer on the current PR head.

Python 3.11+. Live mode needs gh authentication and reviewer access.
--fixture reads synthetic snapshots only; no gh, network, or PR changes.
Exit 0: new completed review received, NOT permission to merge.
Exit 1: API/data error, changed head, or bounded timeout. Exit 2: bad arguments.
Success JSON goes to stdout, error JSON to stderr. Inline threads, CI and
branch protection must be checked separately; this helper never merges.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import subprocess
import sys
import time

REVIEWER = "copilot-pull-request-reviewer[bot]"
# INTENTIONAL workshop regression: a completed review need not be an approval.
COMPLETED = {"APPROVED"}


class ReviewError(Exception):
    pass


def positive(value: str) -> float:
    result = float(value)
    if not 0 < result < float("inf"):
        raise argparse.ArgumentTypeError("must be finite and positive")
    return result


class GitHub:
    def __init__(self, repo: str, pr: int, deadline: float):
        self.base = f"repos/{repo}/pulls/{pr}"
        self.deadline = deadline

    def api(self, *args: str):
        remaining = self.deadline - time.monotonic()
        if remaining <= 0:
            raise ReviewError("timeout")
        try:
            result = subprocess.run(
                ["gh", "api", *args], capture_output=True, text=True,
                check=True, timeout=min(remaining, 15),
            )
            return json.loads(result.stdout) if result.stdout.strip() else None
        except subprocess.CalledProcessError as exc:
            # API response bodies may contain private data. Do not reproduce them.
            raise ReviewError(f"gh api failed (exit {exc.returncode})") from exc
        except subprocess.TimeoutExpired as exc:
            raise ReviewError("GitHub request timed out") from exc
        except (OSError, ValueError) as exc:
            raise ReviewError(f"GitHub transport error: {type(exc).__name__}") from exc

    def head(self):
        return self.api(self.base)["head"]["sha"]

    def snapshot(self):
        head = self.head()
        pages = self.api(f"{self.base}/reviews?per_page=100", "--paginate", "--slurp")
        return head, [review for page in pages for review in page]

    def request(self, reviewer):
        self.api("-X", "POST", f"{self.base}/requested_reviewers",
                 "-f", f"reviewers[]={reviewer}")


class Fixture:
    """Snapshot 0 is the baseline; later snapshots are successive polls."""
    def __init__(self, path):
        data = json.loads(Path(path).read_text())
        self.snapshots = data["snapshots"]
        if len(self.snapshots) < 2:
            raise ReviewError("fixture requires a baseline and a poll")
        self.index = 0
        self.current = self.snapshots[0]
        self.request_error = data.get("request_error")
        self.final_head = data.get("final_head")

    def snapshot(self):
        self.current = self.snapshots[min(self.index, len(self.snapshots) - 1)]
        self.index += 1
        return self.current["head"], self.current["reviews"]

    def head(self):
        return self.final_head or self.current["head"]

    def request(self, reviewer):
        if self.request_error:
            raise ReviewError(self.request_error)


def select_review(reviews, *, head, reviewer, previous_ids):
    eligible = [r for r in reviews
                if r["id"] not in previous_ids
                and r.get("user", {}).get("login") == reviewer
                and r.get("commit_id") == head
                and r.get("state") in COMPLETED
                and r.get("submitted_at")]
    return max(eligible, key=lambda r: (r["submitted_at"], r["id"]), default=None)


def await_review(transport, *, reviewer, deadline, interval,
                 clock=time.monotonic, sleep=time.sleep):
    head, existing = transport.snapshot()
    previous_ids = {r["id"] for r in existing}
    transport.request(reviewer)
    while clock() < deadline:
        current_head, reviews = transport.snapshot()
        if current_head != head:
            raise ReviewError("PR head changed; restart review for the new commit")
        review = select_review(reviews, head=head, reviewer=reviewer,
                               previous_ids=previous_ids)
        if review is not None:
            if transport.head() != head:
                raise ReviewError("PR head changed during final check")
            if clock() >= deadline:
                raise ReviewError("timeout")
            return {"head_sha": head, "review_id": review["id"],
                    "reviewer": reviewer, "state": review["state"],
                    "body": review.get("body") or "", "url": review.get("html_url"),
                    "received": True, "merge_authorized": False}
        sleep(min(interval, max(0, deadline - clock())))
    raise ReviewError("timeout waiting for a new review on the current head")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pr", type=int)
    parser.add_argument("--repo", required=True)
    parser.add_argument("--reviewer", default=REVIEWER)
    parser.add_argument("--interval", type=positive, default=5)
    parser.add_argument("--timeout", type=positive, default=120)
    parser.add_argument("--fixture", type=Path)
    args = parser.parse_args(argv)
    if args.pr <= 0 or not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", args.repo):
        parser.error("use a positive PR number and --repo owner/repository")
    deadline = time.monotonic() + args.timeout
    try:
        transport = Fixture(args.fixture) if args.fixture else GitHub(args.repo, args.pr, deadline)
        result = await_review(transport, reviewer=args.reviewer,
                              deadline=deadline, interval=args.interval)
        print(json.dumps({"pr": args.pr, "repo": args.repo, **result}))
        return 0
    except (ReviewError, OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({"received": False, "error": str(exc)}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
