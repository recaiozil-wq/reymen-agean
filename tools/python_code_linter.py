# -*- coding: utf-8 -*-
"""python_code_linter.py — Python kodu lint kontrolü.

AST ile temel sözdizimi + kod kalitesi denetimi yapar.
pyflakes/pylint kurulu değilse fallback olarak sadece AST doğrulaması.
"""

import ast
import json
import sys

# Opsiyonel: tokenize
try:
    import tokenize  # noqa: F401
    HAS_TOKENIZE = True
except ImportError:
    HAS_TOKENIZE = False


TOOL_META = {
    "aciklama": "Python kodunu lint kontrolünden geçirir. AST tabanlı syntax ve kod kalitesi denetimi.",
    "parametreler": [
        {"ad": "kod", "tip": "str", "aciklama": "Kontrol edilecek Python kodu (string)."}
    ],
    "ornek": 'PYTHON_KODU_LINTER(\'print("merhaba")\')',
    "kategori": "code_execution",
}


def run(kod: str = "", *args, **kwargs) -> str:
    """Python kodunu lint kontrolünden geçir.

    Args:
        kod: Kontrol edilecek Python kodu (string).

    Returns:
        JSON: lint sonuçları (hata sayısı, uyarılar, detaylar).
    """
    if not kod:
        return json.dumps({"hata": "kod parametresi zorunludur.", "hata_sayisi": 1}, ensure_ascii=False)

    sonuclar = {"hata_sayisi": 0, "uyari_sayisi": 0, "hatalar": [], "uyarilar": []}

    try:
        # AST ile sözdizimi kontrolü
        tree = ast.parse(kod)
        sonuclar["ast_durum"] = "basarili"
    except SyntaxError as e:
        sonuclar["ast_durum"] = "hata"
        sonuclar["hata_sayisi"] += 1
        sonuclar["hatalar"].append({
            "tip": "SyntaxError",
            "mesaj": str(e),
            "satir": e.lineno or 0,
            "kolon": e.offset or 0,
        })
        return json.dumps(sonuclar, ensure_ascii=False, indent=2)

    # AST tabanlı kod kalitesi kontrolleri
    try:
        for node in ast.walk(tree):
            # Kullanılmayan import uyarısı
            if isinstance(node, ast.Import):
                for alias in node.names:
                    name = alias.asname or alias.name
                    if not _is_name_used(tree, name, node):
                        sonuclar["uyarilar"].append({
                            "tip": "gereksiz_import",
                            "mesaj": f"'{name}' import edildi ancak kullanılmadı.",
                            "satir": getattr(node, 'lineno', 0),
                        })
                        sonuclar["uyari_sayisi"] += 1

            # from ... import kontrolü
            if isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    name = alias.asname or alias.name
                    if not _is_name_used(tree, name, node):
                        sonuclar["uyarilar"].append({
                            "tip": "gereksiz_import",
                            "mesaj": f"'{name}' import edildi ancak kullanılmadı.",
                            "satir": getattr(node, 'lineno', 0),
                        })
                        sonuclar["uyari_sayisi"] += 1

        # Uzun satır kontrolü
        lines = kod.split('\n')
        for i, line in enumerate(lines, 1):
            if len(line) > 79:
                sonuclar["uyarilar"].append({
                    "tip": "uzun_satir",
                    "mesaj": f"Satir {i} cok uzun ({len(line)} > 79 karakter).",
                    "satir": i,
                })
                sonuclar["uyari_sayisi"] += 1

    except Exception as e:
        sonuclar["uyarilar"].append({
            "tip": "lint_hatasi",
            "mesaj": f"Kontrol sirasinda hata: {str(e)}",
        })
        sonuclar["uyari_sayisi"] += 1

    return json.dumps(sonuclar, ensure_ascii=False, indent=2)


def _is_name_used(tree: ast.AST, name: str, exclude_node: ast.AST) -> bool:
    """Verilen ismin AST'de kullanılıp kullanılmadığını kontrol eder."""
    for node in ast.walk(tree):
        if node is exclude_node:
            continue
        if isinstance(node, ast.Name) and node.id == name:
            return True
        if isinstance(node, ast.Attribute):
            if isinstance(node.value, ast.Name) and node.value.id == name:
                return True
    return False


if __name__ == "__main__":
    test_kod = """
import os
import sys
import math

def selam():
    x = 1
    print("Merhaba")
"""
    print(run(test_kod))
