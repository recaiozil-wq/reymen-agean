#!/usr/bin/env python3
"""
Batch fix v2: Replace except X: ... pass with logged versions.
Preserves exact indentation of the 'pass' line for log.warning().
Creates .bak before modifying. Skips already-fixed files.
"""
import os, re, shutil, ast, datetime

PROJE = r"C:\Users\marko\Desktop\Reymen Proje\ReYMeN-Ajan"
LOG = []

def log(msg):
    print(msg)
    LOG.append(msg)

ALREADY_FIXED = [
    'src\\gateways\\telegram_bot.py', 'src\\gateways\\discord_bot.py',
    'src\\core\\credential_pool.py', 'src\\gateways\\authz_mixin.py',
    'src\\reymen\\sistem\\cozum_hafizasi.py',
]

def fix_file(filepath):
    rel = os.path.relpath(filepath, PROJE)
    if rel in ALREADY_FIXED:
        return 0, "skipped (already fixed)"
    
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
    
    changes = []
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        
        # Check if this line is: except X: or except: (possibly with pass on same line)
        m = re.match(r'^(\s*)(except\s+(\w+(?:\.\w+)*)?\s*:\s*)(pass)?\s*$', stripped)
        if m:
            base_indent = line[:len(line)-len(line.lstrip())]
            has_same_line_pass = m.group(4) is not None
            
            if has_same_line_pass:
                # Pattern: except X: pass (same line)
                exc_prefix = m.group(2).rstrip(':').rstrip()
                module = rel.replace('\\', '.').replace('.py', '').replace('src.', '')
                exc_type = m.group(3) or 'Exception'
                new_line = f"{base_indent}{exc_prefix} as e:\n{base_indent}    log.warning(f\"[{module}] {exc_type} at L{i+1}\")\n{base_indent}    pass\n"
                changes.append((i, line, new_line))
                i += 1
                continue
            
            else:
                # Check next non-blank line for 'pass'
                j = i + 1
                while j < len(lines) and lines[j].strip() in ('', '', '') and not lines[j].strip().startswith('#'):
                    j += 1
                
                if j < len(lines) and lines[j].strip() == 'pass':
                    pass_line = lines[j]
                    pass_indent = pass_line[:len(pass_line)-len(pass_line.lstrip())]
                    module = rel.replace('\\', '.').replace('.py', '').replace('src.', '')
                    exc_type = m.group(3) or 'Exception'
                    
                    # Replace the except line with except + log
                    # m.group(2) includes the trailing colon, strip it before adding " as e:"
                    exc_prefix = m.group(2).rstrip(':').rstrip()
                    if exc_type:
                        new_except = f"{base_indent}{exc_prefix} as e:\n{pass_indent}log.warning(f\"[{module}] {exc_type} at L{i+1}\")\n"
                    else:
                        # bare "except:" -> "except Exception as e:"
                        new_except = f"{base_indent}except Exception as e:\n{pass_indent}log.warning(f\"[{module}] Exception at L{i+1}\")\n"
                    changes.append((i, line, new_except))
                    # pass line stays as-is
                    i = j + 1
                    continue
        
        i += 1
    
    if not changes:
        return 0, "no changes"
    
    # Backup
    bak = filepath + f".bak.{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(filepath, bak)
    
    # Apply changes (reverse order to preserve indices)
    new_lines = list(lines)
    for idx, old_text, new_text in reversed(changes):
        new_lines[idx] = new_text
    
    new_content = ''.join(new_lines)
    
    # Syntax check
    try:
        ast.parse(new_content)
    except SyntaxError as e:
        shutil.copy2(bak, filepath)
        return 0, f"SYNTAX ERROR: {e}"
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    return len(changes), "ok"

# Main
log(f"=== Batch Fix v2: except:pass → log — {datetime.datetime.now()} ===")
log(f"Proje: {PROJE}\n")

total_fixed = 0
total_errors = 0
results = []

for root, dirs, files in os.walk(os.path.join(PROJE, 'src')):
    for f in files:
        if f.endswith('.py'):
            fp = os.path.join(root, f)
            fixed, status = fix_file(fp)
            if fixed > 0:
                rel = os.path.relpath(fp, PROJE)
                results.append((fixed, rel, status))
                total_fixed += fixed
                log(f"  ✅ {rel}: {fixed} fix")
            elif status != "no changes" and status != "skipped (already fixed)":
                total_errors += 1
                rel = os.path.relpath(fp, PROJE)
                log(f"  ❌ {rel}: {status}")

log(f"\n=== ÖZET ===")
log(f"  Düzeltilen: {total_fixed} instance")
log(f"  Hatalı: {total_errors}")

if total_errors == 0 and total_fixed > 0:
    log("\n✅ Tüm dosyalar başarıyla düzeltildi.")
elif total_errors > 0:
    log(f"\n⚠️ {total_errors} dosyada hata var, elle müdahale gerek.")
elif total_fixed == 0:
    log("\nℹ️ Düzeltilecek dosya bulunamadı.")
