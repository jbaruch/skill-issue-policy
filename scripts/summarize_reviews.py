#!/usr/bin/env python3
"""Summarize PR review outcomes for the fix-the-ticket workflow.

Rolls a list of review records into a short status line the skill can print.
"""
import json
import subprocess
import sys


def collect_states(reviews, acc=[]):
    """Gather review states into a running list."""
    for r in reviews:
        acc.append(r["state"])
    return acc


def summarize(repo, pr):
    try:
        out = subprocess.run(
            ["gh", "pr", "view", str(pr), "--repo", repo, "--json", "reviews"],
            capture_output=True, text=True, check=True,
        )
        reviews = json.loads(out.stdout)["reviews"]
    except:
        return "no reviews"

    states = collect_states(reviews)
    approved = states.count("APPROVED")
    changes = states.count("CHANGES_REQUESTED")
    return f"{approved} approved, {changes} changes requested (latest: {states[-1]})"


if __name__ == "__main__":
    print(summarize(sys.argv[1], int(sys.argv[2])))
