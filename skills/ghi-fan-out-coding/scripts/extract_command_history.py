#!/usr/bin/env python3
"""Extract command history from an Antigravity subagent transcript.

Usage:
  python3 extract_command_history.py <transcript.jsonl> [--audit]

Outputs timestamped commands to stdout.
With --audit, also flags dangerous commands.
"""
import json
import sys
import re
import os

DANGEROUS_PATTERNS = [
    (r'git\s+add\s+\.', '🔴 DANGEROUS: git add . (tracks ignored files)'),
    (r'git\s+add\s+-[Aa]', '🔴 DANGEROUS: git add -A/-a (tracks ignored files)'),
    (r'git\s+add\s+-f', '🔴 DANGEROUS: git add -f (force-tracks ignored files)'),
    (r'git\s+commit\s+-a', '🔴 DANGEROUS: git commit -a (commits all tracked changes)'),
    (r'git\s+reset\s+--hard', '🔴 DANGEROUS: git reset --hard (destroys uncommitted work)'),
    (r'git\s+clean\s+-[fd]', '🔴 DANGEROUS: git clean (deletes untracked files)'),
    (r'git\s+push\s+.*--force', '🟠 RISKY: git push --force (rewrites remote history)'),
    (r'git\s+push\s+-f', '🟠 RISKY: git push -f (rewrites remote history)'),
    (r'rm\s+-rf\s+/', '🔴 DANGEROUS: rm -rf / (catastrophic delete)'),
    (r'rm\s+-rf\s+\.gemini', '🔴 DANGEROUS: rm -rf .gemini (deletes execution logs)'),
    (r'git\s+checkout\s+--\s+\.', '🟠 RISKY: git checkout -- . (discards all changes)'),
    (r'git\s+stash\s+drop', '🟠 RISKY: git stash drop (loses stashed work)'),
]

def extract_commands(transcript_path, audit=False):
    commands = []
    danger_count = 0
    
    with open(transcript_path) as f:
        for line in f:
            try:
                step = json.loads(line.strip())
            except json.JSONDecodeError:
                continue
            
            tool_calls = step.get('tool_calls', [])
            if not tool_calls:
                continue
                
            ts = step.get('created_at', '????-??-??T??:??:??Z')
            
            for tc in tool_calls:
                name = tc.get('name', tc.get('tool_name', ''))
                if name != 'run_command':
                    continue
                
                args = tc.get('args', tc.get('arguments', {}))
                if isinstance(args, str):
                    try:
                        args = json.loads(args)
                    except json.JSONDecodeError:
                        continue
                
                cmd = args.get('CommandLine', '').strip().strip('"')
                cwd = args.get('Cwd', '').strip().strip('"')
                
                if not cmd:
                    continue
                
                entry = f'{ts}  [{cwd}]  {cmd}'
                commands.append(entry)
                print(entry)
                
                if audit:
                    for pattern, warning in DANGEROUS_PATTERNS:
                        if re.search(pattern, cmd):
                            print(f'  ⚠️  {warning}')
                            danger_count += 1
    
    if audit:
        print(f'\n{"="*60}')
        print(f'Total commands: {len(commands)}')
        print(f'Dangerous flags: {danger_count}')
        if danger_count == 0:
            print('✅ No dangerous commands detected.')
        else:
            print(f'🔴 {danger_count} dangerous command(s) found!')
    
    return commands, danger_count

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f'Usage: {sys.argv[0]} <transcript.jsonl> [--audit]')
        sys.exit(1)
    
    transcript = sys.argv[1]
    audit = '--audit' in sys.argv
    
    if not os.path.exists(transcript):
        print(f'Error: {transcript} not found')
        sys.exit(1)
    
    extract_commands(transcript, audit=audit)
