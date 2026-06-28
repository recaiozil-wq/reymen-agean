#!/usr/bin/env python3
"""
Process A-M range .md files in the AI_ML root:
1. Ensure frontmatter exists (add if missing: name, description, title, version)
2. Remove '> **Kategori:**' line(s)
3. Remove old 5N1K tables (both markdown table and ## 📋 5N1K formats)
4. Add new standardized 5N1K table
5. Validate YAML frontmatter -> write if valid
"""

import os
import re
import yaml
from pathlib import Path

BASE = Path(r"C:\Users\marko\Desktop\Reymen Proje\hermes_projesi\reymen\cereyan\skills\Skiller\AI_ML")


def get_am_files():
    """Return sorted A-M root-level .md files."""
    files = []
    for entry in os.listdir(BASE):
        full = BASE / entry
        if full.is_file() and entry.endswith(".md"):
            first_char = entry[0].lower()
            if 'a' <= first_char <= 'm':
                files.append(entry)
    files.sort()
    return files


def find_closing_fence(lines):
    """Find index of closing --- fence in frontmatter (line index in lines list).
    Handles both clean '---' on its own line and fused cases like 'key: val---'."""
    for i in range(1, len(lines)):
        s = lines[i].strip()
        if s == "---":
            return i, lines[i]
        if "---" in lines[i]:
            # Check if --- is at the end of a YAML value
            idx = lines[i].find("---")
            if idx > 0:
                # Split the line at ---
                lines[i] = lines[i][:idx]
                return i, "---"
    return None, None


def extract_frontmatter(content):
    """Return (yaml_text, rest_of_content, success)."""
    if not content.startswith("---"):
        return None, content, False
    lines = content.split('\n')
    end_idx, _ = find_closing_fence(lines)
    if end_idx is None:
        return None, content, False
    yaml_text = '\n'.join(lines[1:end_idx])
    rest = '\n'.join(lines[end_idx+1:])
    return yaml_text, rest, True


def ensure_fm_fields(fm_dict, filename):
    """Ensure name, description, title, version exist. Returns True if changed."""
    changed = False
    default_name = filename.replace('.md', '')
    default_title = default_name.replace('_', ' ').replace('-', ' ').title().strip()
    
    for key, default_val in [('name', default_name), ('description', ''),
                              ('title', default_title), ('version', '1.0.0')]:
        val = fm_dict.get(key)
        if val is None or (isinstance(val, str) and val.strip() == ''):
            fm_dict[key] = default_val
            changed = True
    return changed


def fm_to_yaml_str(fm_dict):
    """Serialize dict to YAML string with --- fences."""
    yaml_str = yaml.dump(fm_dict, default_flow_style=False,
                         allow_unicode=True, sort_keys=False).strip()
    return "---\n" + yaml_str + "\n---"


def remove_kategori(content):
    """Remove '> **Kategori:**' lines."""
    return re.sub(r'> \*\*Kategori:\*\*.*\n?', '', content)


def remove_old_5n1k(content):
    """Remove old-style 5N1K content (tables and inline key:value blocks)."""
    # Pattern A: `|| 5N1K | Açıklama |` markdown table
    content = re.sub(
        r'\|\| 5N1K \| Açıklama \|\n\|:----:\|:---------\|.*?(?=\n\n|\n---|\Z)',
        '', content, flags=re.DOTALL)
    # Pattern B: `## 📋 5N1K` section
    content = re.sub(
        r'## 📋 5N1K\n\n.*?(?=\n---|\Z)',
        '', content, flags=re.DOTALL)
    # Pattern C: inline 5N1K block (Kim:/Ne:/Nerede:/Ne Zaman:/Neden:/Nasil:)
    content = re.sub(
        r'Kim:.*\nNe:.*\nNerede:.*\nNe Zaman:.*\nNeden:.*\nNasil:.*\n?',
        '', content)
    # Collapse 3+ blank lines
    content = re.sub(r'\n{4,}', '\n\n\n', content)
    return content


def add_new_5n1k(content, filename):
    """Insert new 5N1K table after frontmatter closing fence."""
    table = (
        "| 5N1K | Açıklama |\n"
        "|:----:|:---------|\n"
        f"| **Kim** | AI/ML mühendisi |\n"
        "| **Ne** |  |\n"
        f"| **Nerede** | `AI_ML/{filename}` |\n"
        "| **Ne Zaman** |  |\n"
        "| **Neden** |  |\n"
        "| **Nasıl** |  |"
    )
    
    lines = content.split('\n')
    # Find the closing --- of frontmatter
    end_fm = 0
    if content.startswith("---"):
        for i in range(1, len(lines)):
            s = lines[i].strip()
            if s == "---" or "---" in s and i > 0:
                end_fm = i
                break
    
    insert_at = end_fm + 1
    # Skip blank lines after frontmatter
    while insert_at < len(lines) and lines[insert_at].strip() == '':
        insert_at += 1
    
    new_lines = lines[:insert_at] + [table, ''] + lines[insert_at:]
    result = '\n'.join(new_lines)
    
    # Deduplicate if table somehow appears twice
    if result.count(table) > 1:
        parts = result.split(table)
        result = table + ''.join(parts[1:])
    
    return result


def process_file(filename):
    """Returns (status, detail)."""
    filepath = BASE / filename
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return "error", f"Cannot read: {e}"
    
    original = content
    
    # ── Step 1: Frontmatter ──
    if has_frontmatter(content):
        yaml_text, rest, ok = extract_frontmatter(content)
        if not ok or not yaml_text:
            return "skip", "Frontmatter malformed (no closing ---)"
        
        try:
            fm_dict = yaml.safe_load(yaml_text)
        except yaml.YAMLError as e:
            return "error", f"Broken YAML: {str(e)[:80]}"
        
        if not isinstance(fm_dict, dict):
            fm_dict = {}
        
        if ensure_fm_fields(fm_dict, filename):
            new_fm = fm_to_yaml_str(fm_dict)
            content = new_fm + '\n' + rest
    else:
        # Add basic frontmatter
        name = filename.replace('.md', '')
        fm_dict = {"name": name, "description": "",
                    "title": name.replace('_', ' ').replace('-', ' ').title().strip(),
                    "version": "1.0.0"}
        new_fm = fm_to_yaml_str(fm_dict)
        content = new_fm + '\n\n' + content
    
    # ── Step 2: Remove kategori lines ──
    content = remove_kategori(content)
    
    # ── Step 3: Remove old 5N1K ──
    content = remove_old_5n1k(content)
    
    # ── Step 4: Add new 5N1K table ──
    content = add_new_5n1k(content, filename)
    
    # ── Step 5: Validate final frontmatter ──
    yaml_text, rest, ok = extract_frontmatter(content)
    if not ok:
        return "error", "Cannot extract fm after changes"
    try:
        yaml.safe_load(yaml_text)
    except yaml.YAMLError as e:
        return "error", f"YAML invalid after changes: {str(e)[:80]}"
    
    # ── Step 6: Write ──
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return "fixed", "OK"
    else:
        return "unchanged", "No changes needed"


def has_frontmatter(content):
    return content.startswith("---")


def main():
    files = get_am_files()
    print(f"Total A-M root-level .md files: {len(files)}")
    
    stats = {"fixed": 0, "unchanged": 0, "error": 0, "skip": 0}
    errors = []
    
    for i, fname in enumerate(files, 1):
        status, msg = process_file(fname)
        stats[status] = stats.get(status, 0) + 1
        if status == "error":
            errors.append((fname, msg))
            if len(errors) <= 15:
                print(f"  ERR [{i}/{len(files)}] {fname}: {msg}")
        elif status == "skip":
            if len(errors) <= 15:
                print(f"  SKP [{i}/{len(files)}] {fname}: {msg}")
        elif status == "fixed" and i % 300 == 0:
            print(f"  OK [{i}/{len(files)}] fixed={stats['fixed']} err={stats['error']} skip={stats['skip']}")
    
    print(f"\n{'='*60}")
    print("REPORT")
    print(f"{'='*60}")
    print(f"Total A-M files scanned: {len(files)}")
    print(f"  Fixed:     {stats['fixed']}")
    print(f"  Unchanged: {stats['unchanged']}")
    print(f"  Errors:    {stats['error']}")
    print(f"  Skipped:   {stats['skip']}")
    
    if errors:
        print(f"\nAll errors ({len(errors)} total):")
        for fname, msg in errors:
            print(f"  {fname}: {msg}")


if __name__ == "__main__":
    main()
