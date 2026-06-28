#!/usr/bin/env python3
"""Kritik sessiz except tarayici - ReYMeN-Ajan"""
import ast, os, sys

WORKDIR = r"C:\Users\marko\Desktop\Reymen Proje\ReYMeN-Ajan"
os.chdir(WORKDIR)

KRITIK = []  # (dosya, satir_no, except_tipi, context)
DIGER = []   # (dosya, satir_no, except_tipi)

for root, dirs, files in os.walk('reymen'):
    dirs[:] = [d for d in dirs if d not in ('__pycache__', '.git', 'venv', 'hermes-memory-backup', 'hermes_backup', '.ReYMeN', 'node_modules')]
    for f in files:
        if not f.endswith('.py'):
            continue
        path = os.path.join(root, f)
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as fh:
                content = fh.read()
                lines = content.split('\n')
            tree = ast.parse(content, path)
        except SyntaxError:
            continue
        
        rel = os.path.relpath(path, 'reymen')
        
        for node in ast.walk(tree):
            if not isinstance(node, ast.Try):
                continue
            
            for handler in node.handlers:
                lineno = handler.lineno
                # log kontrolu
                has_log = False
                for k in range(max(1,lineno-3), min(len(lines), lineno+3)):
                    if 'logger.warning' in lines[k-1] or 'log.warning' in lines[k-1]:
                        has_log = True
                        break
                
                # context topla
                context = []
                for k in range(lineno, min(len(lines), lineno+3)):
                    stripped = lines[k-1].strip()
                    context.append(stripped)
                    if 'pass' in stripped and len(stripped) < 20:
                        break
                ctx_str = ' | '.join(context[:3])
                
                if handler.type is None:
                    # except: (bare)
                    if not has_log:
                        KRITIK.append((rel, lineno, 'except:', ctx_str))
                elif isinstance(handler.type, ast.Name):
                    exc_name = handler.type.id
                    if exc_name == 'Exception' and not has_log:
                        KRITIK.append((rel, lineno, 'except Exception:', ctx_str))
                    elif not has_log:
                        DIGER.append((rel, lineno, f'except {exc_name}:'))

print(f"KRITIK (except Exception: / except:): {len(KRITIK)}")
print()
for d, s, e, c in sorted(KRITIK):
    print(f"  {d}:{s} | {e}")
    print(f"    -> {c[:120]}")
print()
print(f"DIGER (spesifik, log'suz): {len(DIGER)}")
for d, s, e in sorted(DIGER):
    print(f"  {d}:{s} | {e}")
