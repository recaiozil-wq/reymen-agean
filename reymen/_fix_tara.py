#!/usr/bin/env python3
"""Kritik sessiz except fix: except Exception: pass → logger.warning ekle"""
import ast, os, sys, re
from collections import defaultdict

WORKDIR = r"C:\Users\marko\Desktop\Reymen Proje\ReYMeN-Ajan\reymen"
os.chdir(WORKDIR)

# Dosya bazında topla
FIX_HEDEFLERI = defaultdict(list)
ZATEN_LOG_VAR = set()

for root, dirs, files in os.walk('.'):
    dirs[:] = [d for d in dirs if d not in ('__pycache__', '.git', 'venv', 
               'hermes-memory-backup', 'hermes_backup', '.ReYMeN', 'node_modules')]
    for f in files:
        if not f.endswith('.py'):
            continue
        path = os.path.join(root, f)
        rel = os.path.relpath(path, '.')
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as fh:
                content = fh.read()
                lines = content.split('\n')
            tree = ast.parse(content, path)
        except (SyntaxError, UnicodeDecodeError):
            continue
        
        has_logger_def = any('logger = logging.getLogger' in l or 'logger = logging.get_logger' in l for l in lines)
        has_logging_import = any('import logging' in l for l in lines)
        if has_logger_def or has_logging_import:
            ZATEN_LOG_VAR.add(rel)
        
        for node in ast.walk(tree):
            if not isinstance(node, ast.Try):
                continue
            for handler in node.handlers:
                kritik = False
                if handler.type is None:
                    kritik = True
                elif isinstance(handler.type, ast.Name) and handler.type.id == 'Exception':
                    kritik = True
                
                if not kritik:
                    continue
                
                lineno = handler.lineno
                has_log = False
                for k in range(max(1,lineno-3), min(len(lines), lineno+5)):
                    if any(x in lines[k-1] for x in ['logger.warning', 'log.warning', 'logger.error', 'logger.exception']):
                        has_log = True
                        break
                
                if has_log:
                    continue
                
                icerik = []
                for k in range(lineno, min(len(lines), lineno+5)):
                    s = lines[k-1].strip()
                    icerik.append(s)
                    if s == 'pass' or s.startswith('pass #'):
                        break
                
                sadece_pass = len([s for s in icerik if s == 'pass' or s.startswith('pass #') or (s and not s.startswith('#'))]) <= 1
                if not sadece_pass:
                    continue
                
                exc_type = 'except:' if handler.type is None else 'except Exception:'
                FIX_HEDEFLERI[rel].append((lineno, exc_type, ' | '.join(icerik[:3])))

# Çıktı
print(f"Duzeltilecek dosya: {len(FIX_HEDEFLERI)}")
toplam = sum(len(v) for v in FIX_HEDEFLERI.values())
print(f"Toplam nokta: {toplam}")
print()
for d, noktalar in sorted(FIX_HEDEFLERI.items()):
    print(f"  {d}: {len(noktalar)} nokta")
    for s, e, c in noktalar:
        print(f"    L{s} | {e} | {c[:80]}")
