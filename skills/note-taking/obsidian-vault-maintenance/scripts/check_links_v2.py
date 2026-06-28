#!/usr/bin/env python3
"""
Obsidian vault link checker v2 — respects full relative paths, not just basenames.
Usage: python check_links_v2.py [vault_root]
Default vault: C:\\Users\\marko\\OneDrive\\Belgeler\\Obsidian Vault\\ReYMeN
"""

import os
import re
import sys

VAULT = r"C:\Users\marko\OneDrive\Belgeler\Obsidian Vault\ReYMeN"
if len(sys.argv) > 1:
    VAULT = sys.argv[1]

if not os.path.isdir(VAULT):
    print(f"ERROR: Vault not found: {VAULT}")
    sys.exit(1)

# Build index: all .md files with their relative paths (w/o extension)
existing_stems = set()     # just the filename stem
existing_relpaths = set()  # full relpath w/ forward slashes
for root, dirs, files in os.walk(VAULT):
    for f in files:
        if not f.endswith('.md'):
            continue
        full = os.path.join(root, f)
        rel = os.path.relpath(full, VAULT).replace('\\', '/')
        rel_noext = rel.replace('.md', '')
        existing_relpaths.add(rel_noext)
        existing_stems.add(f.replace('.md', ''))

# Scan all files for [[links]]
broken = {}  # source_file -> [target_list]
total_links = 0

for root, dirs, files in os.walk(VAULT):
    for f in files:
        if not f.endswith('.md'):
            continue
        path = os.path.join(root, f)
        rel = os.path.relpath(path, VAULT).replace('\\', '/')
        try:
            with open(path, 'r', encoding='utf-8', errors='replace') as fh:
                content = fh.read()
        except:
            continue

        for m in re.finditer(r'\[\[([^\]]+?)\]\]', content):
            total_links += 1
            target = m.group(1).split('|')[0].split('#')[0].strip()
            if not target or target.startswith('http'):
                continue

            # Skip "Pasted image" patterns (Obsidian auto-generated)
            if target.startswith('Pasted image '):
                continue

            # Check: exact match in relpaths?
            if target in existing_relpaths:
                continue

            # Check: basename match
            if target in existing_stems:
                continue

            # Check: target appears as a subdirectory link (e.g. `autonomous-ai-agents/_index`)
            found = False
            for e in existing_relpaths:
                if e.endswith('/' + target):
                    found = True
                    break
            if found:
                continue

            # Truly broken
            if rel not in broken:
                broken[rel] = []
            broken[rel].append(target)

# Report
total_files = sum(1 for r, d, fs in os.walk(VAULT) for f in fs if f.endswith('.md'))
print(f"=== Obsidian Link Check Report ===")
print(f"Vault: {VAULT}")
print(f"MD files: {total_files}")
print(f"Total [[links]] found: {total_links}")
print(f"Broken links: {sum(len(v) for v in broken.values())}")
print()

if broken:
    print("Broken links by file:")
    for src in sorted(broken):
        for tgt in broken[src]:
            print(f"  {src} -> [[{tgt}]]")
else:
    print("ALL CLEAN — zero broken links.")
