#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
env_probe.py — Ortam keşif aracı.
Sistem ortamını tespit eder: Python versiyonu, OS, PATH, kullanılabilir komutlar.
"""

import os
import sys
import json
import platform
import subprocess
import shutil


def _python_bilgisi():
    """Python versiyon ve yol bilgisi."""
    return {
        "versiyon": sys.version,
        "yorumlayici": sys.executable,
        "platform": sys.platform,
        "modul_yollari": sys.path[:5]
    }


def _os_bilgisi():
    """İşletim sistemi bilgisi."""
    return {
        "sistem": platform.system(),
        "node": platform.node(),
        "release": platform.release(),
        "versiyon": platform.version(),
        "makine": platform.machine(),
        "islemci": platform.processor(),
        "ortam_degiskenleri": dict(os.environ) if os.environ else {}
    }


def _path_bilgisi():
    """PATH ortam değişkeni ve içeriği."""
    path_str = os.environ.get('PATH', '')
    path_list = path_str.split(os.pathsep) if path_str else []
    var_olan = [p for p in path_list if os.path.isdir(p)]
    return {
        "path_sayisi": len(path_list),
        "var_olan_dizinler": var_olan
    }


def _kullanilabilir_komutlar():
    """Kullanılabilir sistem komutlarını döndür."""
    # Yaygın komutlar
    yaygin_komutlar = [
        "python", "python3", "pip", "pip3", "node", "npm", "git", "curl",
        "wget", "grep", "sed", "awk", "find", "ls", "cat", "mkdir", "rm",
        "cp", "mv", "chmod", "chown", "tar", "gzip", "unzip", "ssh", "scp",
        "docker", "docker-compose", "make", "cmake", "gcc", "g++", "java",
        "ruby", "perl", "php", "go", "rustc", "cargo", "powershell", "cmd"
    ]
    var_olan = []
    for komut in yaygin_komutlar:
        if shutil.which(komut):
            var_olan.append(komut)
    return {
        "toplam": len(var_olan),
        "komutlar": var_olan
    }


def run(sorgu="tumu"):
    """
    Sistem ortamını keşfeder.
    
    Parametreler:
        sorgu (str): python / os / path / komut / tumu
    
    Returns:
        str: Keşif sonucu JSON formatında
    """
    try:
        sonuc = {"durum": "basarili", "sorgu": sorgu}

        if sorgu == "python" or sorgu == "tumu":
            sonuc["python"] = _python_bilgisi()
        if sorgu == "os" or sorgu == "tumu":
            sonuc["os"] = _os_bilgisi()
        if sorgu == "path" or sorgu == "tumu":
            sonuc["path"] = _path_bilgisi()
        if sorgu == "komut" or sorgu == "tumu":
            sonuc["komutlar"] = _kullanilabilir_komutlar()

        if sorgu not in ("python", "os", "path", "komut", "tumu"):
            return json.dumps({"durum": "hata", "mesaj": f"bilinmeyen sorgu: {sorgu}"}, ensure_ascii=False)

        return json.dumps(sonuc, ensure_ascii=False, default=str)

    except Exception as e:
        return json.dumps({"durum": "hata", "mesaj": str(e)}, ensure_ascii=False)


if __name__ == "__main__":
    print(run("tumu"))
