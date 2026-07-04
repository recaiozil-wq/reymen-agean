#!/usr/bin/env python3
"""
Batch fix v3: Replace except X:\\n    pass with logged versions.
Reads the pass line's indentation and inserts log.warning at that level.
Backup first, then patch, then syntax check.
"""
import os, re, shutil, ast, datetime

PROJE = r"C:\Users\marko\Desktop\Reymen Proje\ReYMeN-Ajan"
LOG = []

# Files already fixed in batch 1 — skip
ALREADY_FIXED = {
    'src\\gateways\\telegram_bot.py',
    'src\\gateways\\discord_bot.py', 
    'src\\core\\credential_pool.py',
    'src\\gateways\\authz_mixin.py',
    'src\\reymen\\sistem\\cozum_hafizasi.py',
}

def fix_file(filepath):
    """Returns (fixed_count, error_message_or_None)."""
    rel = os.path.relpath(filepath, PROJE)
    if rel in ALREADY_FIXED:
        return (0, None)
    
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        lines = content.split('\n')
    
    new_lines = list(lines)
    fixes_made = 0
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped.startswith('except '):
            continue
        
        # Check if there's a :pass on the same line
        m = re.match(r'^(.*)(except\s+[\w.]+(\s+as\s+\w+)?\s*:\s*)pass\s*$', stripped)
        if m:
            indent = line[:len(line) - len(line.lstrip())]
            module_short = rel.replace('\\', '.').replace('.py', '')
            new_lines[i] = f"{indent}{m.group(2)}"
            # Insert log line and pass BELOW at current indent + body indent
            body_indent = indent + '    '
            new_lines.insert(i+1, f'{body_indent}log.warning(f"[{module_short}] Exception at L{i+1}")')
            new_lines.insert(i+2, f'{body_indent}pass')
            fixes_made += 1
            continue
        
        # Check if it ends with : and next non-empty is pass
        if not stripped.rstrip().endswith(':'):
            continue
        if ':' not in stripped:
            continue
            
        # Find the position of the colon
        colon_pos = stripped.rfind(':')
        before_colon = stripped[:colon_pos]
        after_colon = stripped[colon_pos+1:]
        
        # If there's content after colon that isn't just whitespace/comment, skip
        if after_colon.strip() and not after_colon.strip().startswith('#'):
            continue
        
        # Find next non-empty line
        j = i + 1
        while j < len(lines) and (lines[j].strip() == '' or lines[j].strip().startswith('#')):
            j += 1
        
        if j >= len(lines) or lines[j].strip() != 'pass':
            continue
        
        # Found pattern: except X: ...  (empty body except pass)
        indent = line[:len(line) - len(line.lstrip())]
        pass_indent = new_lines[j][:len(new_lines[j]) - len(new_lines[j].lstrip())]
        module_short = rel.replace('\\', '.').replace('.py', '')
        
        # Extract exception type
        exc_match = re.match(r'except\s+([\w.]+)', stripped)
        exc_type = exc_match.group(1) if exc_match else 'Exception'
        
        # Replace the except line
        new_lines[i] = f'{indent}except {exc_type} as _e:'
        # Insert log warning at pass indentation level
        new_lines.insert(i+1, f'{pass_indent}log.warning(f"[{module_short}] {exc_type} at L{i+1}")')
        # The original pass stays where it is, just at same indent level
        # But we inserted a line, so shift j
        j_shifted = j + 1
        fixes_made += 1
    
    if fixes_made == 0:
        return (0, None)
    
    # Backup
    bak = filepath + f".bak.{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(filepath, bak)
    
    new_content = '\n'.join(new_lines)
    
    # Syntax check
    try:
        ast.parse(new_content)
    except SyntaxError as e:
        shutil.copy2(bak, filepath)
        return (0, f"Syntax error: {e}")
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    return (fixes_made, None)


print("=== Batch Fix v3: except:pass → log ===")
print(f"Tarih: {datetime.datetime.now()}\n")

total_fixed = 0
total_errors = 0

for root, dirs, files in os.walk(os.path.join(PROJE, 'src')):
    for f in files:
        if f.endswith('.py'):
            fp = os.path.join(root, f)
            fixed, error = fix_file(fp)
            if fixed:
                rel = os.path.relpath(fp, PROJE)
                print(f"  ✅ {rel}: {fixed} fix")
                total_fixed += fixed
            elif error:
                rel = os.path.relpath(fp, PROJE)
                print(f"  ❌ {rel}: {error}")
                total_errors += 1

print(f"\n=== ÖZET ===")
print(f"  Düzeltilen: {total_fixed}")
print(f"  Hata: {total_errors}")

if total_errors == 0 and total_fixed > 0:
    print("\n✅ Tüm dosyalar başarıyla düzeltildi.")
elif total_errors > 0:
    print(f"\n⚠️ {total_errors} dosyada hata — backup'tan restore edildi.")
