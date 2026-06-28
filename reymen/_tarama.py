#!/usr/bin/env python3
"""Sessiz except tarayici - AST + regex hybrid"""
import ast, os, re, sys

SESSIZ_EXCEPT = []
WORKDIR = os.path.dirname(os.path.abspath(__file__))

for root, dirs, files in os.walk(WORKDIR):
    # Skip
    skip_dirs = ['__pycache__', '.git', 'venv', 'hermes-memory-backup', 'hermes_backup', '.ReYMeN', 'node_modules', 'dist', 'build']
    dirs[:] = [d for d in dirs if d not in skip_dirs]
    
    for f in files:
        if not f.endswith('.py'):
            continue
        path = os.path.join(root, f)
        rel = os.path.relpath(path, WORKDIR)
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as fh:
                lines = fh.readlines()
        except Exception:  # nosec
            continue
        
        i = 0
        while i < len(lines):
            line = lines[i]
            if re.match(r'^\s*except\b', line):
                j = i + 1
                while j < len(lines) and (lines[j].strip() == '' or lines[j].strip().startswith('#') or lines[j].strip().startswith('raise')):
                    j += 1
                if j < len(lines) and re.match(r'^\s*pass\s*(#.*)?$', lines[j]):
                    has_log = any('logger.warning' in lines[k] or 'log.warning' in lines[k] for k in range(max(0,i-3), j+1))
                    if not has_log:
                        SESSIZ_EXCEPT.append((rel, i+1, lines[i].strip()[:80]))
            i += 1

print(f"TOPLAM SESSIZ EXCEPT (log'suz): {len(SESSIZ_EXCEPT)}")
for d, s, ic in sorted(SESSIZ_EXCEPT):
    print(f"  {d}:{s} | {ic}")

if len(SESSIZ_EXCEPT) == 0:
    print("\n✅ TUMU TEMIZ! Sessiz except kalmadi.")
