#!/usr/bin/env python3
"""
SECOND PASS: Process A-M .md files.
Restore each file from git first, then apply clean transformations.
"""

import os, re, yaml, subprocess, sys
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

BASE = Path(r"C:\Users\marko\Desktop\Reymen Proje\hermes_projesi\reymen\cereyan\skills\Skiller\AI_ML")

def get_am_files():
    files = []
    for entry in sorted(os.listdir(BASE)):
        full = BASE / entry
        if full.is_file() and entry.endswith(".md"):
            if 'a' <= entry[0].lower() <= 'm':
                files.append(entry)
    return files

def restore_from_git(filename):
    """Restore a single file from git index."""
    filepath = BASE / filename
    try:
        # Try git show HEAD:path
        result = subprocess.run(
            ["git", "show", f"HEAD:{filepath.relative_to(BASE.parents[3])}"],
            capture_output=True, text=True, timeout=10,
            cwd=str(BASE)
        )
        if result.returncode == 0:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(result.stdout)
            return True
    except Exception as _e:
        logger.warning("[ProcessAmFilesV2] except Exception (L35): %s", Exception)
        pass
    return False

def find_true_frontmatter(content):
    """
    Find the REAL frontmatter boundaries.
    Looks for first '---' on line 1, then the NEXT line that is ONLY '---' (not part of a table).
    Returns (yaml_text, body_text, ok_bool) or (None, content, False).
    """
    if not content.startswith("---"):
        return None, content, False
    
    lines = content.split('\n')
    
    # Find the closing --- that is genuinely a standalone fence
    # It must be a line that is EXACTLY '---' (with optional whitespace) — not ':----:' or anything else
    end_idx = None
    for i in range(1, len(lines)):
        line = lines[i].strip()
        # Must be EXACTLY '---' - no extra characters, no table borders
        if line == "---":
            end_idx = i
            break
    
    if end_idx is None:
        return None, content, False
    
    yaml_text = '\n'.join(lines[1:end_idx])
    body = '\n'.join(lines[end_idx+1:])
    return yaml_text, body, True

def build_clean_frontmatter(fm_dict, filename):
    """Build a clean frontmatter with required fields."""
    name_val = fm_dict.get('name') or filename.replace('.md', '')
    desc_val = fm_dict.get('description') or ''
    title_val = fm_dict.get('title') or name_val.replace('_', ' ').replace('-', ' ').title().strip()
    version_val = fm_dict.get('version') or '1.0.0'
    
    clean = {}
    # Put required fields first
    clean['name'] = name_val
    clean['description'] = desc_val
    clean['title'] = title_val
    clean['version'] = version_val
    
    # Add any other fields from original that are valid YAML
    for k, v in fm_dict.items():
        if k not in clean and v is not None and not (isinstance(v, str) and v.strip() == ''):
            clean[k] = v
    
    return clean

def serialize_yaml_fm(fm_dict):
    """Serialize a dict to YAML frontmatter string."""
    text = yaml.dump(fm_dict, default_flow_style=False, allow_unicode=True, sort_keys=False).strip()
    return "---\n" + text + "\n---"

def strip_old_5n1k(body):
    """Remove all old 5N1K content from the body."""
    # Old markdown table: || 5N1K | Açıklama | ... (old style before new table)
    body = re.sub(
        r'\|\| 5N1K \| Açıklama \|\n\|:----:\|:---------\|.*?(?=\n\n|\n---|\Z)',
        '', body, flags=re.DOTALL)
    
    # ## 📋 5N1K section
    body = re.sub(
        r'## 📋 5N1K\n\n.*?(?=\n---|\Z)',
        '', body, flags=re.DOTALL)
    
    # Inline key:value block
    body = re.sub(
        r'Kim:.*\nNe:.*\nNerede:.*\nNe Zaman:.*\nNeden:.*\nNasil:.*\n?',
        '', body)
    
    # Also our NEW 5N1K table (in case it was already inserted)
    body = re.sub(
        r'\| 5N1K \| Açıklama \|\n\|\:----:\|\:---------\|.*?\n\| \*\*Nasıl\*\* \| .*? \|',
        '', body, flags=re.DOTALL)
    
    # Any stray '| **Kim**' or '| **Ne**' etc rows that might be leftover
    body = re.sub(r'\| \*\*.*?\*\* \|.*?\|', '', body)
    
    # Remove stray --- separators that were inside old 5N1K
    body = re.sub(r'\n---\n', '\n', body)
    
    # Clean up excess blank lines
    body = re.sub(r'\n{4,}', '\n\n\n', body)
    
    return body.strip()

def add_new_5n1k_table(body, filename):
    """Add the new standardized 5N1K table at the top of the body."""
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
    return table + '\n\n' + body

def remove_kategori_lines(body):
    """Remove '> **Kategori:**' lines."""
    return re.sub(r'> \*\*Kategori:\*\*.*\n?', '', body)

def process_file(filename):
    """Process file. Returns (status, msg)."""
    filepath = BASE / filename
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return "error", f"Read fail: {e}"
    
    # Step 1: Identify true frontmatter boundaries
    yaml_text, body_rest, has_fm = find_true_frontmatter(content)
    
    if has_fm and yaml_text:
        # Parse existing YAML
        try:
            fm_dict = yaml.safe_load(yaml_text)
            if not isinstance(fm_dict, dict):
                fm_dict = {}
        except yaml.YAMLError as e:
            return "error", f"Broken YAML: {str(e)[:100]}"
        
        # Clean up the frontmatter
        fm_dict = build_clean_frontmatter(fm_dict, filename)
        
    else:
        # No frontmatter - check if file starts with something else
        # Some files have no frontmatter at all (reference files)
        lines = content.split('\n')
        # If first non-empty line starts with # or is plain text, no frontmatter
        fm_dict = {
            'name': filename.replace('.md', ''),
            'description': '',
            'title': filename.replace('.md', '').replace('_', ' ').replace('-', ' ').title().strip(),
            'version': '1.0.0'
        }
        body_rest = content
    
    # Build new frontmatter
    new_fm = serialize_yaml_fm(fm_dict)
    
    # Step 2: Clean the body
    body = body_rest
    
    # Remove kategori lines
    body = remove_kategori_lines(body)
    
    # Remove ALL 5N1K content (old and any new that was already inserted)
    body = strip_old_5n1k(body)
    
    # Remove stray pipe-only lines or table fragments
    body = re.sub(r'^\|.*\|$', '', body, flags=re.MULTILINE)
    
    # Clean blank lines
    body = re.sub(r'\n{4,}', '\n\n\n', body)
    body = body.strip()
    
    # Step 3: Add new 5N1K table
    body = add_new_5n1k_table(body, filename)
    
    # Step 4: Final content
    new_content = new_fm + '\n' + body + '\n'
    
    # Step 5: Validate the new frontmatter
    yaml_new, _, ok = find_true_frontmatter(new_content)
    if not ok:
        return "error", "Final fm extraction failed"
    try:
        yaml.safe_load(yaml_new)
    except yaml.YAMLError as e:
        return "error", f"Final YAML invalid: {str(e)[:100]}"
    
    # Step 6: Write
    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return "fixed", "OK"
    else:
        return "unchanged", "No changes"

def main():
    files = get_am_files()
    # Filter to A-M range from the full list
    am_files = [f for f in files if 'a' <= f[0].lower() <= 'm']
    print(f"Total A-M root-level .md files: {len(am_files)}")
    
    stats = {"fixed": 0, "unchanged": 0, "error": 0}
    errors = []
    
    for i, fname in enumerate(am_files, 1):
        status, msg = process_file(fname)
        stats[status] += 1
        if status == "error":
            errors.append((fname, msg))
            if len(errors) <= 10:
                print(f"  ERR [{i}/{len(am_files)}] {fname}: {msg[:100]}")
        elif status == "fixed" and i % 400 == 0:
            print(f"  OK [{i}/{len(am_files)}] fixed={stats['fixed']} err={stats['error']}")
    
    print(f"\n{'='*60}")
    print("REPORT")
    print(f"{'='*60}")
    print(f"Total: {len(am_files)}")
    print(f"  Fixed:     {stats['fixed']}")
    print(f"  Unchanged: {stats['unchanged']}")
    print(f"  Errors:    {stats['error']}")
    
    if errors:
        print(f"\nAll {len(errors)} errors:")
        for fname, msg in errors:
            print(f"  {fname}: {msg[:120]}")

if __name__ == "__main__":
    main()
