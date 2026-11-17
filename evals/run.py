#!/usr/bin/env python3
"""Isolated injected-context workflow-PLANNING experiment.

This measures local file edits and a written workflow with explicit context injection.
It does not measure native skill activation; run that as a separate experiment.
It does NOT test real PR creation, actual test execution by the model, or merge
enforcement. Behavioral helper/hook tests are in tests/. No LLM judge is used.
Each cell/trial/scenario gets a fresh temp directory outside the source tree.
Only task inputs and the selected context are copied; grading stays outside.
CLI uses a new Claude session with no resumed state, a fixed system prompt,
empty setting sources and MCP configuration, disabled skill discovery,
and only Read/Write/Edit. No user skills are candidates in this experiment.
Managed enterprise policy may still apply: use a clean profile for publication
quality measurements, record host policy constraints, and inspect raw traces.
Never compare error/budget/timeout runs as if they were scored model failures.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
SYSTEM = ('You are editing a small local training repository. Use relevant available '
          'skills. Follow the user scope. You may edit files and write a proposed '
          'workflow, but cannot run shell commands or contact external systems. '
          'Do not claim you executed commands or tests you only proposed.')
TASKS = {
    'docs': 'Add a Quickstart section to README.md explaining how to list the brick inventory. '
            'Change documentation only. Do not commit, open a PR, or contact a remote service.',
    'code': 'Fix payment.py so a zero-dollar payment is rejected. Add regression coverage. '
            'Describe how you would get the change reviewed and merged in workflow_log.md. '
            'This is a local planning exercise: edit files but do not execute git or gh commands.',
}


def prepare(work, cell, starter):
    (work / 'README.md').write_text('# Brickbox\n\nGET /bricks lists the inventory.\n')
    (work / 'payment.py').write_text(
        'def process_payment(amount):\n    if amount < 0:\n        raise ValueError("invalid amount")\n    return True\n')
    if cell == 'fixed':
        for name in ('fix-the-ticket', 'update-docs'):
            shutil.copytree(ROOT / 'skills' / name, work / '.context' / name,
                            ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        (work / '.context/policy.md').write_text('\n\n'.join(
            p.read_text() for p in sorted((ROOT / 'rules').glob('*.md'))))
    elif cell == 'bad':
        source = starter / '.claude/skills/fix-the-ticket'
        if not source.is_dir():
            raise ValueError('bad cell needs --starter pointing to the original starter')
        shutil.copytree(source, work / '.context/fix-the-ticket')


def tool_calls(events):
    for event in events:
        for block in event.get('message', {}).get('content', []):
            if isinstance(block, dict) and block.get('type') == 'tool_use':
                yield block


def grade(work, scenario, events):
    if scenario == 'docs':
        return {'no_code_workflow_created': not (work / 'workflow_log.md').exists()}
    plan = (work / 'workflow_log.md').read_text() if (work / 'workflow_log.md').exists() else ''
    return {'companion_helper_in_plan': 'await_review.py' in plan,
            'repository_explicit_in_plan': 'await_review.py' in plan and '--repo' in plan}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--trials', type=int, default=3)
    parser.add_argument('--model', required=True, help='explicit model ID; record resolved model from result too')
    parser.add_argument('--cells', nargs='+', choices=['none', 'bad', 'fixed'], default=['none', 'bad', 'fixed'])
    parser.add_argument('--scenarios', nargs='+', choices=list(TASKS), default=list(TASKS))
    parser.add_argument('--starter', type=Path, default=ROOT.parent / 'skill-issue-brickbox-start')
    parser.add_argument('--output', type=Path, default=ROOT / 'eval-results')
    parser.add_argument('--budget', type=float, default=1)
    parser.add_argument('--timeout', type=int, default=180)
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    if args.trials < 1 or args.budget <= 0 or args.timeout < 1:
        parser.error('trials, budget and timeout must be positive')
    if args.dry_run:
        print(json.dumps({'calls': len(args.cells) * len(args.scenarios) * args.trials,
                          'scope': 'injected-context planning', 'model': args.model,
                          'maximum_budget_usd': len(args.cells) * len(args.scenarios) * args.trials * args.budget}))
        return
    args.output.mkdir(parents=True, exist_ok=True)
    cli = subprocess.run(['claude', '--version'], capture_output=True, text=True, check=True).stdout.strip()
    run_id = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    run_dir = args.output / run_id
    run_dir.mkdir()
    rows = []
    for trial in range(1, args.trials + 1):
        # Rotate cell order between trials to reduce simple time/order confounding.
        cells = args.cells[trial % len(args.cells):] + args.cells[:trial % len(args.cells)]
        for scenario in args.scenarios:
            for cell in cells:
                with tempfile.TemporaryDirectory(prefix='qcon-skill-eval-') as tmp:
                    work = Path(tmp)
                    prepare(work, cell, args.starter.resolve())
                    context = '\n\n'.join('Context file: ' + str(p) + '\n' + p.read_text()
                        for p in sorted((work / '.context').rglob('*.md')))
                    system = SYSTEM + ('\n\nUse relevant guidance below.\n' + context if context else '')
                    cmd = ['claude', '-p', TASKS[scenario], '--model', args.model,
                           '--system-prompt', system, '--setting-sources', '',
                           '--strict-mcp-config', '--mcp-config', '{"mcpServers":{}}',
                           '--disable-slash-commands', '--tools', 'Read,Write,Edit', '--allowedTools', 'Read,Write,Edit',
                           '--permission-mode', 'acceptEdits', '--no-session-persistence',
                           '--max-budget-usd', str(args.budget), '--output-format', 'stream-json', '--verbose']
                    row = {'scenario': scenario, 'cell': cell, 'trial': trial, 'requested_model': args.model,
                           'cli': cli, 'scope': 'injected-context-planning', 'command': cmd,
                           'inputs_sha256': {str(p.relative_to(work)): hashlib.sha256(p.read_bytes()).hexdigest()
                                             for p in work.rglob('*') if p.is_file()}}
                    artifact = run_dir / f'{scenario}-{cell}-{trial}'
                    artifact.mkdir()
                    try:
                        import os
                        env = dict(os.environ, CLAUDE_CODE_DISABLE_AUTO_MEMORY='1')
                        result = subprocess.run(cmd, cwd=work, env=env, capture_output=True, text=True, timeout=args.timeout)
                        (artifact / 'trace.jsonl').write_text(result.stdout)
                        (artifact / 'stderr.txt').write_text(result.stderr)
                        events = [json.loads(line) for line in result.stdout.splitlines() if line.strip()]
                        final = next((e for e in reversed(events) if e.get('type') == 'result'), {})
                        row.update(exit_code=result.returncode, result_subtype=final.get('subtype'),
                                   resolved_models=list(final.get('modelUsage', {})))
                        if result.returncode or final.get('is_error') or final.get('subtype') != 'success':
                            row['status'] = 'run_error'
                        else:
                            row.update(status='scored', checks=grade(work, scenario, events))
                        for name in ('README.md', 'payment.py', 'workflow_log.md'):
                            if (work / name).exists(): shutil.copy2(work / name, artifact / name)
                    except subprocess.TimeoutExpired:
                        row['status'] = 'timeout'
                    except (OSError, ValueError) as exc:
                        row.update(status='run_error', error=str(exc))
                    rows.append(row)
                    with (run_dir / 'results.jsonl').open('a') as stream:
                        stream.write(json.dumps(row) + '\n')
                    print(json.dumps({k: row[k] for k in ('scenario', 'cell', 'trial', 'status')}), flush=True)
    summary = []
    for scenario in args.scenarios:
        for cell in args.cells:
            group = [r for r in rows if r['scenario'] == scenario and r['cell'] == cell]
            scored = [r for r in group if r['status'] == 'scored']
            summary.append({'scenario': scenario, 'cell': cell, 'scored': len(scored),
                            'errors': len(group)-len(scored),
                            'passes': {key: sum(r['checks'][key] for r in scored)
                                       for key in (scored[0]['checks'] if scored else [])}})
    (run_dir / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(run_dir)


if __name__ == '__main__': main()
