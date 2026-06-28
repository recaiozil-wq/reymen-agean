#!/usr/bin/env python3
"""
Batch process all .md files in AI_ML root directory:
1. Add frontmatter if missing (name, description, title, version)
2. Add 5N1K table if missing (after frontmatter)
3. Remove '> **Kategori:**' lines
4. Remove old '## 📋 5N1K' sections (Soru/Cevap format)
5. Remove redundant plain-text Kim/Ne/Nerede sections  
6. Remove duplicate pipe-style 5N1K tables
7. Clean up stray separators and embedded malformed frontmatter
8. Validate YAML - only write valid files
"""

import os
import re
import yaml
import sys
import time

ROOT = r"C:\Users\marko\Desktop\Reymen Proje\hermes_projesi\reymen\cereyan\skills\Skiller\AI_ML"

FM_KEYS_COPY = frozenset({
    'name', 'description', 'title', 'version', 'phase', 'lesson', 'tags',
    'category', 'audience', 'origin'
})

def filename_no_ext(path):
    base = os.path.basename(path)
    name, _ = os.path.splitext(base)
    return name

def safe_yaml_load(text):
    """Safely load YAML, returning None on any error."""
    try:
        obj = yaml.safe_load(text)
        if isinstance(obj, dict):
            return obj
        return None
    except Exception:
        return None

def fmt_title(name):
    """Format a filename into a title."""
    return name.replace('-', ' ').replace('_', ' ').title()

def has_fm_start(text):
    return text.startswith('---\n') or text.startswith('---\r\n')

def parse_fm_at_start(text):
    """
    If text starts with ---, parse YAML frontmatter.
    Returns (dict, char_pos_after_closing) or (None, 0).
    """
    if not has_fm_start(text):
        return None, 0
    lines = text.split('\n')
    end_i = None
    for i in range(1, len(lines)):
        if lines[i].strip() == '---':
            end_i = i
            break
    if end_i is None or end_i < 2:
        return None, 0
    fm_text = '\n'.join(lines[1:end_i])
    if not fm_text.strip():
        return None, 0
    fm = safe_yaml_load(fm_text)
    if fm is None:
        return None, 0
    end_pos = sum(len(l) + 1 for l in lines[:end_i + 1])
    return fm, end_pos

def get_first_sentence(text):
    if not text:
        return ""
    text = text.strip()
    sents = re.split(r'(?<=[.!?])\s+', text)
    desc = sents[0].strip().strip('"').strip("'").strip('#').strip()
    return desc

def find_description(text, skip_fm=True):
    """
    Find first meaningful sentence in text (after optional frontmatter).
    Returns string or empty.
    """
    if skip_fm and has_fm_start(text):
        _, pos = parse_fm_at_start(text)
        text = text[pos:]
    lines = text.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith('|') or line.startswith('---') or line.startswith('>'):
            continue
        if any(line.startswith(k) for k in ('Kim:', 'Ne:', 'Nerede:', 'Ne Zaman:', 'Neden:', 'Nasil:', 'name:', 'description:', 'title:', 'audience:', 'tags:', 'category:', 'origin:')):
            continue
        if line.startswith('# ') or line.startswith('## '):
            t = line.lstrip('#').strip()
            if t:
                return get_first_sentence(t)
        if line:
            return get_first_sentence(line)
    return ""

def clean_old_sections(text):
    """Remove Kategori, old 5N1K, plain-text Kim/Ne, stray --- separators."""
    result = text
    # Remove > **Kategori:** lines (various formats)
    result = re.sub(r'^>\s*\*+.*?Kategori.*?\*+:?.*$\n?', '', result, flags=re.MULTILINE)
    # Remove old ## 📋 5N1K section (header + blank line + table)
    result = re.sub(r'##\s*📋\s*5N1K\s*\n\s*\n(?:\|[^\n]*\|\s*\n)*', '', result, flags=re.MULTILINE)
    result = re.sub(r'##\s*📋\s*5N1K\s*\n(?:\|[^\n]*\|\s*\n)*', '', result, flags=re.MULTILINE)
    # Remove plain-text Kim/Ne blocks
    result = re.sub(
        r'^---\s*\n(?:Kim|Ne|Nerede|Ne Zaman|Neden|Nasil)\s*:.*(?:\n(?:Kim|Ne|Nerede|Ne Zaman|Neden|Nasil)\s*:.*)*',
        '', result, flags=re.MULTILINE
    )
    # Remove loose Kim:/Ne: lines
    result = re.sub(
        r'^(?:Kim|Ne|Nerede|Ne Zaman|Neden|Nasil)\s*:\s*.*$\n?',
        '', result, flags=re.MULTILINE
    )
    return result

def remove_dup_tables(text):
    """Keep only first pipe-5N1K table."""
    p = r'\| 5N1K \| Açıklama \|\s*\|:----:\|:---------\|\s*(?:\| \*\*.*?\*\* \| .* \|\s*)*'
    matches = list(re.finditer(p, text, re.MULTILINE))
    if len(matches) <= 1:
        return text
    for m in reversed(matches[1:]):
        text = text[:m.start()] + text[m.end():]
    return text

def has_5n1k(text):
    return '| 5N1K | Açıklama |' in text

def build_table(desc):
    if not desc:
        desc = "AI/ML görevi"
    return (
        f"| 5N1K | Açıklama |\n"
        f"|:----:|:---------|\n"
        f"| **Kim** | AI/ML mühendisi |\n"
        f"| **Ne** | {desc} |\n"
        f"| **Nerede** | AI_ML/ |\n"
        f"| **Ne Zaman** | AI/ML görevi gerektiğinde |\n"
        f"| **Neden** | standardize etmek için |\n"
        f"| **Nasıl** | Skill adımlarını takip ederek |"
    )

def build_fm(fname, desc=""):
    if not desc:
        desc = fmt_title(fname)
    # Quote description if it contains special YAML characters
    if needs_yaml_quoting(desc):
        desc = yaml_quote(desc)
    return (
        f"---\n"
        f"name: {fname}\n"
        f"description: {desc}\n"
        f'title: "{fmt_title(fname)}"\n'
        f"version: 1.0.0\n"
        f"---"
    )

def needs_yaml_quoting(val):
    """Check if a YAML scalar value needs quoting."""
    if not val:
        return False
    # Colons followed by space or end-of-string
    if re.search(r':\s|:$', val):
        return True
    # Starts with special characters
    if re.match(r'^[\[\]\{\}\'\"\>\|&\*!%@`]', val):
        return True
    # Contains YAML special characters
    for ch in '#,':
        if ch in val:
            return True
    return False

def yaml_quote(val):
    """Quote a YAML scalar value properly."""
    # Use double quotes, escape inner double quotes and backslashes
    escaped = val.replace('\\', '\\\\').replace('"', '\\"')
    return f'"{escaped}"'

def format_fm_value(key, val):
    """Format a YAML frontmatter key-value pair, properly quoting if needed."""
    if key == 'title':
        if isinstance(val, str) and not val.startswith('"'):
            return f'{key}: "{val}"'
        return f'{key}: {val}'
    if isinstance(val, str):
        if needs_yaml_quoting(val):
            return f'{key}: {yaml_quote(val)}'
        return f'{key}: {val}'
    # Non-string values (lists, ints, etc.)
    return f'{key}: {val}'

def validate_yaml(text):
    """Validate frontmatter YAML. Returns (is_valid, message_or_dict)."""
    lines = text.split('\n')
    if not lines or lines[0].strip() != '---':
        return False, "No opening ---"
    end_line = None
    for i in range(1, len(lines)):
        if lines[i].strip() == '---':
            end_line = i
            break
    if end_line is None:
        return False, "Unclosed frontmatter"
    fm_text = '\n'.join(lines[1:end_line])
    try:
        fm = yaml.safe_load(fm_text)
        if fm is None:
            return False, "Empty frontmatter"
        if not isinstance(fm, dict):
            return False, f"Not a dict"
        return True, fm
    except yaml.YAMLError as e:
        return False, f"YAML error: {e}"

def find_embedded_fm(text):
    """
    Look for a malformed embedded frontmatter.
    Only matches if text doesn't already have valid frontmatter at position 0.
    Returns (dict, end_pos) or (None, 0).
    """
    if has_fm_start(text):
        fm_at_start, _ = parse_fm_at_start(text)
        if fm_at_start and fm_at_start.get('name'):
            return None, 0
    
    m = re.search(r'^---\s*\n(name:\s+\S+)', text, re.MULTILINE)
    if not m:
        return None, 0
    
    start = m.start()
    # Collect lines that look like YAML key:value pairs (frontmatter fields)
    # Stop at the first line that doesn't match, or at --- or end
    after_opening = text[start + 3:]  # skip opening ---
    lines = after_opening.split('\n')
    
    fm_lines = []
    content_rest_start = 0
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped == '---':
            content_rest_start = start + 3 + sum(len(l) + 1 for l in lines[:i+1])
            break
        # Check if line is a valid YAML key: value pair
        if re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*\s*:', stripped):
            fm_lines.append(line)
        elif i > 0 and not stripped:
            # Allow blank lines inside frontmatter
            fm_lines.append(line)
        elif i > 0 and stripped.startswith('#'):
            # Allow comments
            fm_lines.append(line)
        else:
            # First non-frontmatter line after the opening
            if i == 0:
                # First line after --- should be name:, if not, this isn't frontmatter
                return None, 0
            content_rest_start = start + 3 + sum(len(l) + 1 for l in lines[:i])
            break
    else:
        content_rest_start = len(text)
    
    fm_body = '\n'.join(fm_lines).strip()
    if not fm_body:
        return None, 0
    
    # Clean trailing --- artifacts from last value
    fm_body = re.sub(r'---+\s*$', '', fm_body).strip()
    
    fm = safe_yaml_load(fm_body)
    if fm is None:
        return None, 0
    
    return fm, content_rest_start

def remove_stray_separators(text):
    """Remove --- lines that are not part of frontmatter."""
    lines = text.split('\n')
    if not lines:
        return text
    
    result = []
    in_fm = False
    fm_count = 0
    in_code = False
    
    for line in lines:
        stripped = line.strip()
        
        # Track code blocks
        if stripped.startswith('```'):
            in_code = not in_code
        
        if in_code:
            result.append(line)
            continue
        
        if len(result) == 0 and stripped == '---':
            in_fm = True
            fm_count = 1
            result.append(line)
        elif in_fm and stripped == '---':
            fm_count += 1
            result.append(line)
            if fm_count == 2:
                in_fm = False  # frontmatter closed
        elif in_fm:
            result.append(line)
        elif stripped == '---' and not in_fm:
            # Stray separator outside frontmatter - skip it
            continue
        else:
            result.append(line)
    
    return '\n'.join(result)

def process_file(filepath):
    """Process a single markdown file."""
    fname = filename_no_ext(filepath)
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            original = f.read()
    except Exception as e:
        return False, f"Read error: {e}"
    
    if not original.strip():
        desc = fmt_title(fname)
        fm = build_fm(fname, desc)
        tbl = build_table(desc)
        new_content = f"{fm}\n\n{tbl}\n"
        valid, info = validate_yaml(new_content)
        if valid:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return True, "Created (was empty)"
        return False, f"YAML invalid after creation: {info}"
    
    content = original
    
    # Step 1: Clean old sections
    content = clean_old_sections(content)
    content = remove_dup_tables(content)
    content = remove_stray_separators(content)
    content = re.sub(r'\n{4,}', '\n\n\n', content)
    content = content.strip()
    
    changes = []
    
    # Check for embedded malformed frontmatter (ecc_* style)
    embedded_fm, embedded_end = find_embedded_fm(content)
    rest = ""  # Will hold content after embedded frontmatter if found
    if embedded_fm:
        changes.append("Found embedded frontmatter")
        rest = content[embedded_end:].strip()
    
    # Check for proper frontmatter at start
    fm, fm_end = parse_fm_at_start(content)
    
    if fm is None:
        # No frontmatter - add one
        desc = ""
        if embedded_fm:
            desc = embedded_fm.get('description', '')
        if not desc:
            desc = find_description(content)
        if not desc:
            desc = fmt_title(fname)
        
        frontmatter = build_fm(fname, desc)
        if embedded_fm and embedded_end > 0:
            # Use rest after embedded fm
            content = f"{frontmatter}\n\n{rest}"
        else:
            content = f"{frontmatter}\n\n{content}"
        changes.append("Added frontmatter")
    else:
        # Has frontmatter - ensure required fields
        needs_update = False
        
        # Use embedded fm to supplement missing fields
        if embedded_fm:
            for key in ('name', 'description', 'title'):
                if (key not in fm or not fm.get(key)) and key in embedded_fm and embedded_fm[key]:
                    fm[key] = embedded_fm[key]
                    needs_update = True
                    changes.append(f"Filled {key} from embedded frontmatter")
        
        if 'name' not in fm or not fm.get('name'):
            fm['name'] = fname
            needs_update = True
        if 'description' not in fm or not fm.get('description'):
            desc = find_description(content[fm_end:])
            if not desc:
                desc = fmt_title(fname)
            fm['description'] = desc
            needs_update = True
        if 'title' not in fm or not fm.get('title'):
            fm['title'] = fmt_title(fname)
            needs_update = True
        if 'version' not in fm:
            fm['version'] = '1.0.0'
            needs_update = True
        
        if needs_update:
            fm_lines = ['---']
            for key, val in fm.items():
                fm_lines.append(format_fm_value(key, val))
            fm_lines.append('---')
            new_fm = '\n'.join(fm_lines)
            if embedded_fm:
                content = new_fm + '\n\n' + rest
            else:
                content = new_fm + '\n\n' + content[fm_end:].strip()
            changes.append("Fixed frontmatter")
        else:
            changes.append("Frontmatter OK")
    
    # Add 5N1K table if missing
    if not has_5n1k(content):
        fm, fm_end = parse_fm_at_start(content)
        desc = fm.get('description', '') if fm else ''
        if not desc:
            desc = find_description(content[fm_end:] if fm else content)
        if not desc:
            desc = fmt_title(fname)
        
        table = build_table(desc)
        
        lines = content.split('\n')
        fm_close = None
        count = 0
        for i, line in enumerate(lines):
            if line.strip() == '---':
                count += 1
                if count == 2:
                    fm_close = i
                    break
        
        if fm_close is not None:
            insert_pos = fm_close + 1
            while insert_pos < len(lines) and lines[insert_pos].strip() == '':
                insert_pos += 1
            new_lines = lines[:insert_pos] + ['', table, ''] + lines[insert_pos:]
        else:
            new_lines = lines + ['', table, '']
        content = '\n'.join(new_lines)
        changes.append("Added 5N1K table")
    else:
        changes.append("5N1K table exists")
    
    # Final cleanup
    content = re.sub(r'\n{4,}', '\n\n\n', content)
    content = content.strip() + '\n'
    
    # Remove stray separators again (may have been introduced)
    content = remove_stray_separators(content)
    
    # Validate YAML
    valid, info = validate_yaml(content)
    if not valid:
        return False, f"YAML invalid: {info}"
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True, f"Written: {', '.join(changes)}"
    else:
        return True, "No changes needed"

def main():
    files = []
    for f in os.listdir(ROOT):
        full = os.path.join(ROOT, f)
        if f.endswith('.md') and os.path.isfile(full):
            files.append(full)
    
    script_path = os.path.join(ROOT, 'process_5n1k.py')
    files = [f for f in files if f != script_path]
    files.sort()
    
    print(f"Found {len(files)} .md files in AI_ML root")
    print()
    
    stats = {'written': 0, 'no_change': 0, 'errors': 0}
    error_list = []
    
    t0 = time.time()
    
    for i, filepath in enumerate(files):
        if i % 200 == 0 and i > 0:
            elapsed = time.time() - t0
            rate = i / elapsed if elapsed > 0 else 0
            pct = i * 100 // len(files)
            print(f"  [{pct}%] {i}/{len(files)} | written={stats['written']} errors={stats['errors']} | {rate:.1f} files/s")
        
        success, msg = process_file(filepath)
        if success:
            if msg.startswith("Written"):
                stats['written'] += 1
            else:
                stats['no_change'] += 1
        else:
            stats['errors'] += 1
            error_list.append((os.path.basename(filepath), msg))
    
    t1 = time.time()
    
    print(f"\n{'='*60}")
    print(f"RESULTS")
    print(f"{'='*60}")
    print(f"  Total files:       {len(files)}")
    print(f"  Written (changed): {stats['written']}")
    print(f"  No changes:        {stats['no_change']}")
    print(f"  Errors:            {stats['errors']}")
    print(f"  Time:              {t1-t0:.1f}s")
    
    if error_list:
        print(f"\n  Error details (first 30):")
        for fn, msg in error_list[:30]:
            print(f"    ✗ {fn}: {msg}")
        if len(error_list) > 30:
            print(f"    ... and {len(error_list) - 30} more errors")
    
    return stats

if __name__ == '__main__':
    main()
