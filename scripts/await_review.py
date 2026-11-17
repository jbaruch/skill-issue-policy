#!/usr/bin/env python3
"""Compatibility CLI for source checkouts. Installed consumers use the skill companion."""
from pathlib import Path
import runpy

if __name__ == "__main__":
    runpy.run_path(str(Path(__file__).resolve().parents[1] / "skills/fix-the-ticket/scripts/await_review.py"), run_name="__main__")
