#!/usr/bin/env python3
"""Log completed Skill tool calls locally; no prompt/argument/transcript content.

Claude PostToolUse stdin -> <event.cwd>/.workshop/skill-events.jsonl.
Errors warn and exit 0 (observability must not block work).
Direct /skill commands bypass Skill tool hooks; this is a partial usage signal.
"""
from datetime import datetime, timezone
import json
from pathlib import Path
import sys


def main():
    try:
        event = json.load(sys.stdin)
        if event.get("tool_name") != "Skill":
            return 0
        if event.get("hook_event_name") != "PostToolUse":
            return 0
        record = {"event": "skill_tool_completed", "policy_version": "0.1.6",
                  "at": datetime.now(timezone.utc).isoformat(),
                  "skill": event.get("tool_input", {}).get("skill"),
                  "session_id": event.get("session_id"),
                  "tool_use_id": event.get("tool_use_id")}
        root = Path(event["cwd"])
        if not root.is_absolute():
            raise ValueError("hook cwd must be absolute")
        target = root / ".workshop" / "skill-events.jsonl"
        target.parent.mkdir(exist_ok=True)
        with target.open("a") as stream:
            stream.write(json.dumps(record) + "\n")
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
        print(f"Skill telemetry unavailable: {type(exc).__name__}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
