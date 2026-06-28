#!/usr/bin/env python3
"""ReYMeN-Ajan sessiz except tarayici — ADIM 1 & 2"""
import ast, os, sys

WORKDIR = r"C:\Users\marko\Desktop\Reymen Proje\ReYMeN-Ajan\reymen"
os.chdir(WORKDIR)

SESSIZ_EXCEPT = []  # (dosya_rel, satir, except_tipi, context, has_log)
DIGER_EXCEPT  = []

for root, dirs, files in os.walk('.'):
    dirs[:] = [d for d in dirs if d not in ('__pycache__', '.git', 'venv', 
               'hermes-memory-backup', 'hermes_backup', '.ReYMeN', 'node_modules')]
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
        
        rel = os.path.relpath(path, '.')
        
        for node in ast.walk(tree):
            if not isinstance(node, ast.Try):
                continue
            
            for handler in node.handlers:
                lineno = handler.lineno
                # log/pass kontrolu
                has_log = False
                has_print = False
                has_return = False
                blok_satirlari = []
                for k in range(lineno, min(len(lines), lineno + 5)):
                    satir = lines[k-1].strip()
                    blok_satirlari.append(satir)
                    if 'logger.warning' in satir or 'log.warning' in satir or 'logger.error' in satir or 'logger.exception' in satir:
                        has_log = True
                    if satir.startswith('print(') or satir.startswith('print ('):
                        has_print = True
                    if satir.startswith('return'):
                        has_return = True
                    if 'pass' in satir and len(satir) < 20:
                        break
                
                # Sessiz mi? (sadece pass var, başka hiçbir şey yok)
                sadece_pass = False
                for s in blok_satirlari:
                    if s == 'pass' or s.startswith('pass #'):
                        sadece_pass = True
                    elif s == '' or s.startswith('#'):
                        continue
                    elif s.startswith('pass'):
                        sadece_pass = True
                
                gercek_sessiz = sadece_pass and not has_log and not has_print and not has_return
                
                if handler.type is None:
                    exc_type = 'except:'
                elif isinstance(handler.type, ast.Name):
                    exc_type = f'except {handler.type.id}:'
                elif isinstance(handler.type, ast.Tuple):
                    names = [e.id if isinstance(e, ast.Name) else '?' for e in handler.type.elts]
                    exc_type = f'except ({", ".join(names)}):'
                else:
                    exc_type = f'except ({type(handler.type).__name__}):'
                ctx = ' | '.join(blok_satirlari[:3])
                
                if gercek_sessiz:
                    SESSIZ_EXCEPT.append((rel, lineno, exc_type, ctx))

# Rapor
print("=" * 60)
print("ADIM 1 — SESSIZ EXCEPT TARAMASI (ReYMeN-Ajan)")
print("=" * 60)
print(f"\nToplam sessiz except (sadece pass, logger/print/return yok): {len(SESSIZ_EXCEPT)}")
print()

# Grupla
from collections import Counter
dosya_say = Counter(d for d, s, e, c in SESSIZ_EXCEPT)
print("DOSYA BAZINDA DAGILIM:")
for d, n in dosya_say.most_common():
    print(f"  {d}: {n} nokta")

print()
print("TUM NOKTALAR (dosya:satir):")
for d, s, e, c in sorted(SESSIZ_EXCEPT):
    print(f"  {d}:{s} | {e}")
