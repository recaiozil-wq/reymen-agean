#!/usr/bin/env python3
"""
Batch fix: Replace all except X: pass patterns with logged versions.
Creates a backup of each file before modifying.
Only fixes files that have NOT already been processed by fix_batch1.
"""
import os, re, shutil, ast, datetime

PROJE = r"C:\Users\marko\Desktop\Reymen Proje\ReYMeN-Ajan"
LOG = []

def log(msg):
    print(msg)
    LOG.append(msg)

def fix_except_pass(filepath):
    """Fix except X: pass patterns in a file. Returns (fixed_count, error)."""
    rel = os.path.relpath(filepath, PROJE)
    
    # Skip already-fixed files
    already_fixed = [
        'src\\gateways\\telegram_bot.py',
        'src\\gateways\\discord_bot.py', 
        'src\\core\\credential_pool.py',
        'src\\gateways\\authz_mixin.py',
        'src\\reymen\\sistem\\cozum_hafizasi.py',
    ]
    if rel in already_fixed:
        return (0, None)
    
    if not os.path.exists(filepath):
        return (0, f"File not found")
    
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        lines = content.split('\n')
    
    fixed = 0
    new_lines = list(lines)
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        # Pattern: except X: pass (same line)
        m = re.match(r'^(.*)(except\s+(\w+(\.\w+)*)\s*:\s*)pass\s*$', stripped)
        if m:
            indent = line[:len(line) - len(line.lstrip())]
            exc_type = m.group(3)
            module_name = rel.replace('\\', '.').replace('.py', '').replace('src.', '')
            
            if exc_type == 'Exception':
                new_line = f"{indent}{m.group(2)}log.warning(f\"[{module_name}] Exception at L{i+1}\")\n{indent}pass"
            else:
                new_line = f"{indent}{m.group(2)}log.warning(f\"[{module_name}] {exc_type} at L{i+1}\")\n{indent}pass"
            
            new_lines[i] = new_line
            fixed += 1
            continue
        
        # Pattern: except X: \n pass (next line)
        m2 = re.match(r'^(.*)(except\s+(\w+(\.\w+)*)\s*:\s*)$', stripped)
        if m2:
            # Check next non-empty/comment line is 'pass'
            j = i + 1
            while j < len(lines) and (lines[j].strip() == '' or lines[j].strip().startswith('#')):
                j += 1
            if j < len(lines) and lines[j].strip() == 'pass':
                indent = line[:len(line) - len(line.lstrip())]
                exc_type = m2.group(3)
                module_name = rel.replace('\\', '.').replace('.py', '').replace('src.', '')
                
                pass_indent = new_lines[j][:len(new_lines[j]) - len(new_lines[j].lstrip())]
                
                if exc_type == 'Exception':
                    new_line = f"{indent}{m2.group(2)}log.warning(f\"[{module_name}] Exception at L{i+1}\")"
                else:
                    new_line = f"{indent}{m2.group(2)}log.warning(f\"[{module_name}] {exc_type} at L{i+1}\")"
                
                new_lines[i] = new_line
                fixed += 1
    
    if fixed == 0:
        return (0, None)
    
    # Backup
    bak = filepath + f".bak.{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(filepath, bak)
    
    new_content = '\n'.join(new_lines)
    
    # Syntax check
    try:
        ast.parse(new_content)
    except SyntaxError as e:
        # Restore backup
        shutil.copy2(bak, filepath)
        return (0, f"Syntax error after patch: {e}")
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    return (fixed, None)

# Main
log(f"=== Batch Fix: except:pass → log — {datetime.datetime.now()} ===")
log(f"Proje: {PROJE}\n")

total_fixed = 0
total_errors = 0

for root, dirs, files in os.walk(os.path.join(PROJE, 'src')):
    for f in files:
        if f.endswith('.py'):
            fp = os.path.join(root, f)
            rel = os.path.relpath(fp, PROJE)
            fixed, error = fix_except_pass(fp)
            if fixed > 0:
                log(f"  ✅ {rel}: {fixed} fix")
                total_fixed += fixed
            elif error:
                log(f"  ❌ {rel}: {error}")
                total_errors += 1

log(f"\n=== ÖZET ===")
log(f"  Toplam düzeltilen: {total_fixed}")
log(f"  Hatalı: {total_errors}")

if total_errors == 0 and total_fixed > 0:
    log("\n✅ Tüm dosyalar başarıyla düzeltildi.")
elif total_fixed == 0 and total_errors == 0:
    log("\nℹ️ Düzeltilecek dosya bulunamadı.")
