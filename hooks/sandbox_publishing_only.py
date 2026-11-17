#!/usr/bin/env python3
"""Claude PreToolUse gate for the workshop publish tool only.

stdin: hook JSON. Exit 2 denies production calls to mcp__workshop__publish;
exit 0 leaves other tools/channels alone. This is a tool-specific demo, not a
shell sandbox. The lab uses synthetic output and no production credentials.
"""
import json
import sys


def main():
    try:
        event = json.load(sys.stdin)
        if event.get("tool_name") == "mcp__workshop__publish":
            args = event.get("tool_input")
            if not isinstance(args, dict) or args.get("channel") != "sandbox":
                print("Workshop publishing is restricted to channel=sandbox.", file=sys.stderr)
                return 2
        return 0
    except (ValueError, TypeError, AttributeError):
        print("Cannot validate hook input.", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
