import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


def hook(name, event):
    return subprocess.run([sys.executable, str(ROOT / 'hooks' / name)],
                          input=json.dumps(event), capture_output=True, text=True)


class HookTests(unittest.TestCase):
    def test_production_publish_is_blocked(self):
        result = hook('sandbox_publishing_only.py', {
            'tool_name': 'mcp__workshop__publish', 'tool_input': {'channel': 'production'}})
        self.assertEqual(result.returncode, 2)

    def test_sandbox_publish_is_allowed(self):
        self.assertEqual(hook('sandbox_publishing_only.py', {
            'tool_name': 'mcp__workshop__publish', 'tool_input': {'channel': 'sandbox'}}).returncode, 0)

    def test_unknown_channel_is_blocked_for_this_tool(self):
        self.assertEqual(hook('sandbox_publishing_only.py', {
            'tool_name': 'mcp__workshop__publish', 'tool_input': {}}).returncode, 2)

    def test_other_tools_are_outside_gate_scope(self):
        self.assertEqual(hook('sandbox_publishing_only.py', {
            'tool_name': 'Read', 'tool_input': {'file_path': '/tmp/example'}}).returncode, 0)

    def test_completed_skill_event_excludes_prompts_and_args(self):
        with tempfile.TemporaryDirectory() as tmp:
            event = {'hook_event_name': 'PostToolUse', 'tool_name': 'Skill',
                     'cwd': tmp, 'tool_input': {'skill': 'fix-the-ticket', 'args': 'private'},
                     'session_id': 'synthetic', 'tool_use_id': 'one', 'prompt': 'private'}
            self.assertEqual(hook('record_skill.py', event).returncode, 0)
            text = (Path(tmp) / '.workshop/skill-events.jsonl').read_text()
            self.assertNotIn('private', text)
            self.assertEqual(json.loads(text)['event'], 'skill_tool_completed')

    def test_attempts_and_unrelated_tools_do_not_count_as_completed_skills(self):
        with tempfile.TemporaryDirectory() as tmp:
            for name, tool in [('PreToolUse', 'Skill'), ('PostToolUse', 'Read')]:
                hook('record_skill.py', {'hook_event_name': name, 'tool_name': tool, 'cwd': tmp})
            self.assertFalse((Path(tmp) / '.workshop').exists())
