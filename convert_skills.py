#!/usr/bin/env python3
"""
Batch convert skills/ .md files to SKILL.md format with YAML frontmatter.
Reads from: skills/
Writes to:  src/reymen/cereyan/skills/
"""

import os
import re
import sys

# Paths (relative to project root)
PROJECT_DIR = r"C:\Users\marko\Desktop\Reymen Proje\ReYMeN-Ajan"
SRC_DIR = os.path.join(PROJECT_DIR, "skills")
DST_DIR = os.path.join(PROJECT_DIR, "src", "reymen", "cereyan", "skills")


def parse_frontmatter(content):
    """Extract YAML frontmatter and body content from a .md file."""
    match = re.match(r'^---\s*\n(.*?)\n(?:---|\.\.\.)\s*\n(.*)', content, re.DOTALL)
    if match:
        return match.group(1), match.group(2)
    # Try with no body
    match = re.match(r'^---\s*\n(.*?)\n---\s*$', content, re.DOTALL)
    if match:
        return match.group(1), ''
    return None, content


def parse_yaml_fields(frontmatter_text):
    """Simple line-based YAML parser to extract key-value pairs."""
    fields = {}
    for line in frontmatter_text.split('\n'):
        stripped = line.strip()
        if not stripped or stripped.startswith('#'):
            continue
        match = re.match(r'^(\w[\w_-]*)\s*:\s*(.*)', line)
        if match:
            key = match.group(1).strip()
            value = match.group(2).strip()
            # Strip surrounding quotes
            if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
                value = value[1:-1]
            fields[key] = value
    return fields


def needs_yaml_quoting(val):
    """Check if a YAML value needs to be quoted for safety. Returns True only
    for values that would be ambiguous or invalid as unquoted YAML scalars."""
    if not val:
        return False
    # YAML array or dict — leave as-is (native YAML syntax)
    if val.startswith('[') or val.startswith('{'):
        return False
    # Contains leading/trailing whitespace
    if val != val.strip():
        return True
    # Contains colon-space (YAML mapping ambiguity)
    if ': ' in val:
        return True
    # YAML boolean/null keywords
    if val.lower() in ('true', 'false', 'yes', 'no', 'on', 'off', 'null', '~'):
        return True
    # Purely positive integer (YAML interprets as number, keep unquoted)
    if re.match(r'^[0-9]+$', val) and not val.startswith('0') and len(val) < 10:
        return False
    # Decimal number (keep unquoted as float)
    if re.match(r'^[0-9]+\.[0-9]+$', val):
        return False
    return False


def build_frontmatter(fields):
    """Build YAML frontmatter string with required fields first."""
    lines = ["---"]
    
    # Required fields (always first, in order)
    for key in ('name', 'description', 'category'):
        val = fields.get(key, '')
        lines.append(f"{key}: {val}")
    
    # All other fields, sorted alphabetically
    preserved = sorted(k for k in fields if k not in ('name', 'description', 'category'))
    for key in preserved:
        val = fields[key]
        if needs_yaml_quoting(val):
            lines.append(f'{key}: "{val}"')
        else:
            lines.append(f"{key}: {val}")
    
    lines.append("---")
    return '\n'.join(lines)


def process_file(src_path, dst_path):
    """Process a single .md file."""
    with open(src_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    frontmatter_text, body = parse_frontmatter(content)
    
    if frontmatter_text:
        fields = parse_yaml_fields(frontmatter_text)
    else:
        base = os.path.splitext(os.path.basename(src_path))[0]
        fields = {'name': base, 'description': f"{base} skill'i", 'category': 'genel'}
        body = content
    
    # Ensure required fields exist
    base = os.path.splitext(os.path.basename(src_path))[0]
    fields.setdefault('name', base)
    fields.setdefault('description', f"{fields['name']} skill'i")
    fields.setdefault('category', 'genel')
    
    # Rebuild and write
    new_fm = build_frontmatter(fields)
    final = new_fm + '\n\n'
    if body:
        final += body.strip() + '\n'
    
    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
    with open(dst_path, 'w', encoding='utf-8') as f:
        f.write(final)
    return True


def main():
    if not os.path.isdir(SRC_DIR):
        print(f"ERROR: Source dir not found: {SRC_DIR}")
        sys.exit(1)
    
    os.makedirs(DST_DIR, exist_ok=True)
    
    md_files = sorted([
        f for f in os.listdir(SRC_DIR)
        if f.endswith('.md') and os.path.isfile(os.path.join(SRC_DIR, f))
    ])
    
    print(f"Found {len(md_files)} .md files in {SRC_DIR}")
    
    success = 0
    failed = 0
    for i, filename in enumerate(md_files, 1):
        src = os.path.join(SRC_DIR, filename)
        dst = os.path.join(DST_DIR, filename)
        try:
            process_file(src, dst)
            success += 1
        except Exception as e:
            print(f"  ERROR [{filename}]: {e}")
            failed += 1
        if i % 100 == 0:
            print(f"  Progress: {i}/{len(md_files)}")
    
    print(f"\nDone: {success} converted, {failed} failed / {len(md_files)} total")


if __name__ == '__main__':
    main()
