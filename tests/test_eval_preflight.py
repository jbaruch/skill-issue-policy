"""Missing comparison input must fail before the CLI is called or quota is spent."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

RUNNER = Path(__file__).resolve().parents[1] / 'evals/run.py'


class EvalPreflightTests(unittest.TestCase):
    def test_missing_bad_cell_input_never_calls_claude(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            marker = root / 'cli-called'
            binary = root / 'claude'
            binary.write_text('#!/usr/bin/env python3\nfrom pathlib import Path\nPath(' +
                              repr(str(marker)) + ').write_text("called")\nraise SystemExit(99)\n')
            binary.chmod(0o755)
            output = root / 'output'
            result = subprocess.run([sys.executable, str(RUNNER), '--model', 'unused',
                '--starter', str(root / 'missing'), '--cells', 'none', 'bad', '--output', str(output)],
                env=dict(os.environ, PATH=str(root) + os.pathsep + os.environ.get('PATH', '')),
                capture_output=True, text=True)
            self.assertEqual(result.returncode, 2, result.stderr)
            self.assertIn('no model calls made', result.stderr)
            self.assertFalse(marker.exists())
            self.assertFalse(output.exists())

    def test_fixed_only_does_not_require_starter(self):
        result = subprocess.run([sys.executable, str(RUNNER), '--model', 'unused',
            '--starter', '/nonexistent/workshop-starter', '--cells', 'fixed', '--dry-run'],
            capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
