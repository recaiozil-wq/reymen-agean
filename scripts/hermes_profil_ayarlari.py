"""
Hermes Profil Ayarlari — Otomatik yapilandirma
Yeni kurulumda su ayarlari uygular:
  1. GATEWAY_ALLOW_ALL_USERS=false (3 profil)
  2. allowed_chats whitelist (6328823909)
  3. approvals.mode: gateway (3 profil)
  4. external_dirs → master skills/ (3 profil)
  5. Startup .bat olusturma
  6. Skill sync (reymen → default + kiral38)

Kullanim: python scripts/hermes_profil_ayarlari.py
"""

import os
import shutil
import sys
from pathlib import Path

HERMES = Path.home() / "AppData/Local/hermes"
PROFILES = HERMES / "profiles"
MASTER_SKILLS = HERMES / "skills"
STARTUP = Path.home() / "AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Startup"

def oku(dosya: Path) -> str:
    return dosya.read_text(encoding="utf-8") if dosya.exists() else ""

def yaz(dosya: Path, icerik: str):
    dosya.parent.mkdir(parents=True, exist_ok=True)
    dosya.write_text(icerik, encoding="utf-8")

def env_ayarla(profil: str):
    """GATEWAY_ALLOW_ALL_USERS=false + ALLOWED_CHATS ekle"""
    env = PROFILES / profil / ".env"
    icerik = oku(env)
    
    degisti = False
    if "GATEWAY_ALLOW_ALL_USERS" not in icerik:
        icerik += "\nGATEWAY_ALLOW_ALL_USERS=false\n"
        degisti = True
    
    if "ALLOWED_CHATS" not in icerik and "allowed_chats" not in icerik.lower():
        icerik += "# ALLOWED_CHATS=6328823909\n"
        degisti = True
    
    if degisti:
        yaz(env, icerik)
        print(f"  [OK] {profil}/.env guncellendi")
    else:
        print(f"  [--] {profil}/.env zaten dogru")

def config_ayarla(profil: str):
    """external_dirs'i master skills/ yoluna yonlendir"""
    config = PROFILES / profil / "config.yaml"
    icerik = oku(config)
    
    if not icerik:
        print(f"  [!!] {profil}/config.yaml bulunamadi")
        return
    
    eski_yol = "C:\\Users\\marko\\Desktop\\Reymen Proje\\hermes_projesi\\skills"
    yeni_yol = str(HERMES / "skills").replace("\\", "\\\\")
    
    if eski_yol in icerik:
        icerik = icerik.replace(eski_yol, yeni_yol)
        yaz(config, icerik)
        print(f"  [OK] {profil}/config.yaml external_dirs duzeltildi")
    else:
        print(f"  [--] {profil}/config.yaml zaten dogru")

    # approvals.mode kontrol
    if "mode: gateway" in icerik:
        print(f"  [--] {profil} approvals.mode: gateway (aktif)")
    else:
        print(f"  [!!] {profil} approvals.mode bulunamadi!")

def skill_sync(profil: str):
    """reymen'deki skill'leri profile kopyala"""
    kaynak = PROFILES / "reymen" / "skills"
    hedef = PROFILES / profil / "skills"
    
    if not kaynak.exists():
        print(f"  [!!] Kaynak skills/ bulunamadi: {kaynak}")
        return
    
    hedef.mkdir(parents=True, exist_ok=True)
    say = 0
    for item in kaynak.iterdir():
        if item.is_dir() and not (hedef / item.name).exists():
            shutil.copytree(item, hedef / item.name, dirs_exist_ok=False)
            say += 1
    
    if say > 0:
        print(f"  [OK] {profil}: {say} yeni skill kopyalandi")
    else:
        toplam = len(list(hedef.iterdir())) if hedef.exists() else 0
        print(f"  [--] {profil}: {toplam} skill (guncel)")

def startup_olustur():
    """Startup klasorune gateway baslatma .bat'i ekle"""
    icerik = """@echo off
chcp 65001 >nul
cd /d "C:\\Users\\marko\\AppData\\Local\\hermes"
:: Default profil (@Pasa_38_bot)
start /MIN "" "C:\\Users\\marko\\AppData\\Local\\hermes\\hermes-agent\\venv\\Scripts\\pythonw.exe" -m hermes_cli.main gateway run
timeout /t 5 /nobreak >nul
:: ReYMeN profili (@ReYMeN_ReYMeNbot)
start /MIN "" "C:\\Users\\marko\\AppData\\Local\\hermes\\hermes-agent\\venv\\Scripts\\hermes.exe" -p reymen gateway run --replace
timeout /t 3 /nobreak >nul
:: Kiral38 profili (@Kiral38bot)
start /MIN "" "C:\\Users\\marko\\AppData\\Local\\hermes\\hermes-agent\\venv\\Scripts\\hermes.exe" -p kiral38 gateway run --replace
exit /b 0
"""
    hedef = STARTUP / "Hermes_Gateway_Startup.bat"
    yaz(hedef, icerik)
    print(f"  [OK] Startup .bat olusturuldu")

def main():
    print("=" * 55)
    print("  Hermes Profil Ayarlari — Otomatik Yapilandirma")
    print("=" * 55)
    
    # 1-2. .env ayarlari
    print("\n[1/4] .env ayarlari (GATEWAY_ALLOW_ALL_USERS, ALLOWED_CHATS)...")
    for p in ["default", "reymen", "kiral38"]:
        env_ayarla(p)
    
    # 3. config.yaml
    print("\n[2/4] config.yaml ayarlari (external_dirs, approvals)...")
    for p in ["default", "reymen", "kiral38"]:
        config_ayarla(p)
    
    # 4. Skill sync
    print("\n[3/4] Skill senkronizasyonu (reymen → default + kiral38)...")
    if (PROFILES / "reymen" / "skills").exists():
        for p in ["default", "kiral38"]:
            if p != "reymen":
                skill_sync(p)
    else:
        print("  [!!] reymen skills/ bulunamadi — once Hermes kurulu olmali")
    
    # 5. Startup
    print("\n[4/4] Startup kaydi...")
    if STARTUP.exists():
        startup_olustur()
    else:
        print("  [!!] Startup klasoru bulunamadi")
    
    print("\n" + "=" * 55)
    print("  TAMAM. Ayarlar uygulandi.")
    print("  NOT: .env dosyalarina TELEGRAM_BOT_TOKEN elle eklenmeli.")
    print("=" * 55)

if __name__ == "__main__":
    main()
