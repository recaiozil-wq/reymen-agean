#!/usr/bin/env python3
"""
convert_to_skillmd.py

Converts every .md file under src/reymen/cereyan/skills/ into proper
Hermes SKILL.md format: skills/abc.md -> skills/abc/SKILL.md

Preserves existing subdirectories (e.g., AI_ML/ stays as-is; AI_ML.md
is placed inside it as AI_ML/SKILL.md).
"""

import os
import shutil
import sys
from pathlib import Path

# ── Config ──────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent
SKILLS_DIR = PROJECT_ROOT / "src" / "reymen" / "cereyan" / "skills"

# Safety: require explicit confirmation for >= 10 files
BULK_THRESHOLD = 10


def main():
    if not SKILLS_DIR.is_dir():
        print(f"❌ Skills directory not found: {SKILLS_DIR}")
        sys.exit(1)

    # Collect all .md files (top-level only, per Hermes convention)
    md_files = sorted(f for f in SKILLS_DIR.iterdir() if f.is_file() and f.suffix == ".md")
    total = len(md_files)
    print(f"📁 Found {total} .md file(s) in {SKILLS_DIR}")

    if total == 0:
        print("✅ Nothing to do.")
        return

    # Bulk safety prompt
    if total >= BULK_THRESHOLD:
        print(f"\n⚠️  This will move {total} files into individual subdirectories.")
        print(f"   Example: {md_files[0].name} -> {md_files[0].stem}/SKILL.md")
        response = input("Continue? [y/N] ").strip().lower()
        if response != "y":
            print("❌ Aborted by user.")
            sys.exit(1)
        print()

    moved = 0
    skipped = 0
    errors = []

    for md_file in md_files:
        skill_name = md_file.stem  # filename without .md
        target_dir = SKILLS_DIR / skill_name
        target_file = target_dir / "SKILL.md"

        # ── Create directory (no-op if it already exists) ─────────────
        try:
            target_dir.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            errors.append((md_file.name, f"mkdir failed: {e}"))
            continue

        # ── Check for conflict ────────────────────────────────────────
        if target_file.exists():
            print(f"  ⚠️   Skipped: {md_file.name} -> {target_file} (already exists)")
            skipped += 1
            continue

        # ── Move ──────────────────────────────────────────────────────
        try:
            shutil.move(str(md_file), str(target_file))
            print(f"  ✅ {md_file.name} -> {skill_name}/SKILL.md")
            moved += 1
        except OSError as e:
            errors.append((md_file.name, f"move failed: {e}"))

    # ── Report ────────────────────────────────────────────────────────
    print(f"\n{'='*50}")
    print(f"Done: {moved} moved, {skipped} skipped, {len(errors)} error(s)")
    if errors:
        print(f"\nErrors ({len(errors)}):")
        for name, reason in errors:
            print(f"  ❌ {name}: {reason}")

    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
