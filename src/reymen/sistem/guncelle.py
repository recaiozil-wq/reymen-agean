# -*- coding: utf-8 -*-
"""
guncelle.py â€” ReYMeN AkÄ±llÄ± GÃ¼ncelleme ModÃ¼lÃ¼.

KullanÄ±m (program iÃ§inde):
    /guncelle          â†’ kontrol et ve gÃ¼ncelle
    /guncelle kapat    â†’ otomatik kontrol bildirimini kapat
    /guncelle ac       â†’ otomatik kontrol bildirimini aÃ§
    /guncelle durum    â†’ ayarÄ± gÃ¶ster

DoÄŸrudan Ã§alÄ±ÅŸtÄ±rma:
    python guncelle.py
    python guncelle.py --kapat
    python guncelle.py --ac
"""

import json
import os
import re
import subprocess
import sys
import threading
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

PROJE_KOKU = Path(__file__).parent.resolve()
GITHUB_BRANCH = "main"

# â”€â”€ Buraya kendi GitHub kullanÄ±cÄ± adÄ±nÄ± ve repo adÄ±nÄ± yaz â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
GITHUB_REPO = "KULLANICI_ADI/ReYMeN"  # Ã¶rn: "markopasa/ReYMeN"
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

# GÃ¼ncelleme sÄ±rasÄ±nda ASLA dokunulmayacak kiÅŸisel dosyalar
KORUNACAK = {
    ".env",
    ".ReYMeN/session.db",  # -> merkez_db/session_reymen.db
    ".ReYMeN/memories",
    ".ReYMeN/self_improvement.json",
    ".ReYMeN/cron/jobs.json",
    ".ReYMeN/session.db",  # -> merkez_db/session_reymen.db
    ".ReYMeN/memories",
}

AYAR_DOSYASI = PROJE_KOKU / ".ReYMeN" / "guncelleme.json"

_ARKA_PLAN_SONUC: dict = {}


# â”€â”€ Ayar yÃ¶netimi â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


def ayar_oku() -> dict:
    varsayilan = {"otomatik_kontrol": True, "gosterilen_sha": ""}
    try:
        if AYAR_DOSYASI.exists():
            return {
                **varsayilan,
                **json.loads(AYAR_DOSYASI.read_text(encoding="utf-8")),
            }
    except Exception as _guncelle_e54:
        print(f"[UYARI] guncelle.py:55 - {_guncelle_e54}")
    return varsayilan


def ayar_kaydet(ayar: dict):
    AYAR_DOSYASI.parent.mkdir(parents=True, exist_ok=True)
    AYAR_DOSYASI.write_text(
        json.dumps(ayar, ensure_ascii=False, indent=2), encoding="utf-8"
    )


# â”€â”€ Commit kontrol â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


def _yerel_commit() -> str | None:
    try:
        ref = PROJE_KOKU / ".git" / "refs" / "heads" / GITHUB_BRANCH
        if ref.exists():
            return ref.read_text(encoding="utf-8").strip()[:7]
        head = PROJE_KOKU / ".git" / "HEAD"
        if head.exists():
            ic = head.read_text(encoding="utf-8").strip()
            if not ic.startswith("ref:"):
                return ic[:7]
    except OSError as _guncelle_e76:
        print(f"[UYARI] guncelle.py:77 - {_guncelle_e76}")
    return None


def _uzak_commit() -> str | None:
    if "KULLANICI_ADI" in GITHUB_REPO:
        return None
    try:
        import urllib.request

        url = f"https://api.github.com/repos/{GITHUB_REPO}/commits/{GITHUB_BRANCH}"
        istek = urllib.request.Request(url, headers={"User-Agent": "ReYMeN-updater"})
        with urllib.request.urlopen(istek, timeout=6) as r:
            return json.loads(r.read().decode())["sha"][:7]
    except Exception:
        return None


def guncelleme_var_mi() -> tuple[bool, str | None, str | None]:
    yerel = _yerel_commit()
    uzak = _uzak_commit()
    if yerel and uzak:
        return yerel != uzak, uzak, yerel
    return False, uzak, yerel


# â”€â”€ DeÄŸiÅŸen dosyalarÄ± listele â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


def _degisen_dosyalar() -> dict:
    """git diff ile gÃ¼ncelleme Ã¶ncesi nelerin deÄŸiÅŸeceÄŸini gÃ¶ster."""
    sonuc = {"py": [], "skill": [], "diger": [], "korunan": []}
    try:
        # Uzak repo'dan fetch et
        subprocess.run(
            ["git", "fetch", "origin", GITHUB_BRANCH],
            capture_output=True,
            cwd=str(PROJE_KOKU),
            timeout=15,
        )
        r = subprocess.run(
            ["git", "diff", f"HEAD..origin/{GITHUB_BRANCH}", "--name-only"],
            capture_output=True,
            text=True,
            cwd=str(PROJE_KOKU),
            timeout=10,
        )
        for dosya in r.stdout.strip().splitlines():
            dosya = dosya.strip()
            if not dosya:
                continue
            # Korunacak mÄ±?
            koruma = any(
                dosya == k or dosya.startswith(k + "/") or dosya.startswith(k)
                for k in KORUNACAK
            )
            if koruma:
                sonuc["korunan"].append(dosya)
            elif dosya.endswith(".py"):
                sonuc["py"].append(dosya)
            elif ".ReYMeN/skills" in dosya or "SKILL.md" in dosya:
                sonuc["skill"].append(dosya)
            else:
                sonuc["diger"].append(dosya)
    except Exception as _guncelle_e134:
        print(f"[UYARI] guncelle.py:135 - {_guncelle_e134}")
    return sonuc


# â”€â”€ GÃ¼ncelleme â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


def _git_pull() -> tuple[bool, str]:
    try:
        sonuc = subprocess.run(
            ["git", "pull", "origin", GITHUB_BRANCH],
            capture_output=True,
            text=True,
            cwd=str(PROJE_KOKU),
            timeout=60,
        )
        cikti = (sonuc.stdout + sonuc.stderr).strip()
        return sonuc.returncode == 0, cikti
    except FileNotFoundError:
        return False, "git bulunamadÄ±"
    except subprocess.TimeoutExpired:
        return False, "Zaman aÅŸÄ±mÄ±"
    except Exception as e:
        return False, str(e)


def _zip_ile_guncelle() -> tuple[bool, str]:
    """Git olmayan kullanÄ±cÄ±lar iÃ§in â€” kiÅŸisel dosyalarÄ± atlar."""
    if "KULLANICI_ADI" in GITHUB_REPO:
        return False, "GITHUB_REPO ayarlanmamÄ±ÅŸ."
    try:
        import urllib.request, zipfile, tempfile

        url = f"https://github.com/{GITHUB_REPO}/archive/refs/heads/{GITHUB_BRANCH}.zip"
        print("  ArÅŸiv indiriliyor...")
        with urllib.request.urlopen(url, timeout=120) as r:
            with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp:
                tmp.write(r.read())
                tmp_yol = Path(tmp.name)

        repo_adi = f"{GITHUB_REPO.split('/')[-1]}-{GITHUB_BRANCH}"
        guncellenen = 0

        with zipfile.ZipFile(tmp_yol, "r") as zf:
            for uye in zf.namelist():
                if not uye.startswith(f"{repo_adi}/"):
                    continue
                hedef_yol = uye[len(repo_adi) + 1 :]
                if not hedef_yol:
                    continue

                # Korunacak dosyalarÄ± atla
                koruma = any(
                    hedef_yol == k
                    or hedef_yol.startswith(k + "/")
                    or hedef_yol.startswith(k)
                    for k in KORUNACAK
                )
                if koruma:
                    continue

                # Sadece .py ve skill dosyalarÄ±
                if not (
                    hedef_yol.endswith(".py")
                    or "skills" in hedef_yol
                    or hedef_yol.endswith(".md")
                    or hedef_yol.endswith(".json")
                ):
                    if hedef_yol.endswith(".txt") or hedef_yol.endswith(".yaml"):
                        pass
                    else:
                        continue

                hedef = PROJE_KOKU / hedef_yol
                hedef.parent.mkdir(parents=True, exist_ok=True)
                with zf.open(uye) as k, open(hedef, "wb") as h:
                    h.write(k.read())
                guncellenen += 1

        tmp_yol.unlink(missing_ok=True)
        return True, f"{guncellenen} dosya gÃ¼ncellendi (zip yÃ¶ntemi)."
    except Exception as e:
        return False, f"Zip gÃ¼ncellemesi baÅŸarÄ±sÄ±z: {e}"


def guncelle(onaysiz: bool = False) -> bool:
    """
    GÃ¼ncelleme yap. Ã–nce deÄŸiÅŸenleri gÃ¶ster, sonra onay iste.

    Returns:
        True â†’ gÃ¼ncellendi / False â†’ iptal veya hata
    """
    print()
    var_mi, uzak, yerel = guncelleme_var_mi()

    if not var_mi and uzak is not None:
        print(f"  Zaten gÃ¼ncel ({yerel}).")
        return False

    if uzak:
        print(f"  Mevcut sÃ¼rÃ¼m : {yerel or '(git yok)'}")
        print(f"  Yeni sÃ¼rÃ¼m   : {uzak}")

    # Git varsa nelerin deÄŸiÅŸeceÄŸini gÃ¶ster
    git_dir = PROJE_KOKU / ".git"
    if git_dir.exists():
        degisen = _degisen_dosyalar()
        print()
        if degisen["py"]:
            print(f"  GÃ¼ncellenecek  : {len(degisen['py'])} Python dosyasÄ±")
        if degisen["skill"]:
            print(f"  Yeni/gÃ¼ncellen.: {len(degisen['skill'])} skill")
        if degisen["diger"]:
            print(f"  DiÄŸer          : {len(degisen['diger'])} dosya")
        if degisen["korunan"]:
            print(
                f"  Korunacak      : {len(degisen['korunan'])} kiÅŸisel dosya (.env, hafÄ±za vb.)"
            )

    print()

    if not onaysiz:
        print("  [e] GÃ¼ncelle    [h] Bu sefer atla    [kapat] Bir daha sorma")
        yanit = input("  SeÃ§im: ").strip().lower()
        if yanit == "kapat":
            otomatik_kapat()
            return False
        if yanit != "e":
            print("  AtlandÄ±.")
            return False

    if git_dir.exists():
        print("  git pull yapÄ±lÄ±yor...")
        basari, cikti = _git_pull()
    else:
        print("  Zip yÃ¶ntemiyle gÃ¼ncelleniyor...")
        basari, cikti = _zip_ile_guncelle()

    if basari:
        print(f"  âœ“ {cikti}")
        print("\n  GÃ¼ncelleme tamamlandÄ±! ProgramÄ± yeniden baÅŸlatÄ±n.")
        # SHA'yÄ± "gÃ¶sterildi" olarak kaydet
        ayar = ayar_oku()
        ayar["gosterilen_sha"] = uzak or ""
        ayar_kaydet(ayar)
    else:
        print(f"  âœ— Hata: {cikti}")
    return basari


# â”€â”€ AÃ§ma / Kapatma â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


def otomatik_ac():
    """Otomatik gÃ¼ncelleme bildirimini aÃ§."""
    ayar = ayar_oku()
    ayar["otomatik_kontrol"] = True
    ayar["gosterilen_sha"] = ""  # Bildirimi sÄ±fÄ±rla
    ayar_kaydet(ayar)
    print("  âœ“ Otomatik gÃ¼ncelleme kontrolÃ¼ aÃ§Ä±ldÄ±.")


def otomatik_kapat():
    """Otomatik gÃ¼ncelleme bildirimini kapat."""
    ayar = ayar_oku()
    ayar["otomatik_kontrol"] = False
    ayar_kaydet(ayar)
    print("  Otomatik gÃ¼ncelleme kapatÄ±ldÄ±.")
    print("  Tekrar aÃ§mak iÃ§in: /guncelle ac")


def durum_goster():
    """GÃ¼ncelleme ayarÄ±nÄ± ve son durumu gÃ¶ster."""
    ayar = ayar_oku()
    aktif = "AÃ§Ä±k" if ayar.get("otomatik_kontrol", True) else "KapalÄ±"
    print(f"  Otomatik kontrol : {aktif}")
    print(f"  GitHub repo      : {GITHUB_REPO}")
    yerel = _yerel_commit()
    print(f"  Yerel sÃ¼rÃ¼m      : {yerel or '(git repo deÄŸil)'}")


# â”€â”€ Arka plan kontrolÃ¼ â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


def _arka_plan_kontrol():
    try:
        ayar = ayar_oku()
        if not ayar.get("otomatik_kontrol", True):
            return
        var_mi, uzak, yerel = guncelleme_var_mi()
        _ARKA_PLAN_SONUC["var_mi"] = var_mi
        _ARKA_PLAN_SONUC["uzak"] = uzak
        _ARKA_PLAN_SONUC["yerel"] = yerel
        _ARKA_PLAN_SONUC["gosterilen"] = ayar.get("gosterilen_sha", "")
    except Exception:
        _ARKA_PLAN_SONUC["var_mi"] = False


def arka_plan_baslat():
    """Startup'ta Ã§aÄŸÄ±r â€” arka planda kontrol baÅŸlatÄ±r, kullanÄ±cÄ±yÄ± bekletmez."""
    if "KULLANICI_ADI" in GITHUB_REPO:
        return
    t = threading.Thread(target=_arka_plan_kontrol, daemon=True)
    t.start()


def guncelleme_bildirimi() -> str | None:
    """
    Arka plan sonucu hazÄ±rsa ve yeni bir SHA ise bildirim dÃ¶ndÃ¼r.
    main.py dÃ¶ngÃ¼sÃ¼nde her turda Ã§aÄŸrÄ±lÄ±r, bir kez gÃ¶sterir.
    """
    if not _ARKA_PLAN_SONUC.get("var_mi"):
        return None
    uzak = _ARKA_PLAN_SONUC.get("uzak", "?")
    yerel = _ARKA_PLAN_SONUC.get("yerel", "?")
    gosterilen = _ARKA_PLAN_SONUC.get("gosterilen", "")

    # AynÄ± sÃ¼rÃ¼m iÃ§in tekrar gÃ¶sterme
    if uzak == gosterilen:
        return None

    return (
        f"\n  â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—\n"
        f"  â•‘  Yeni sÃ¼rÃ¼m mevcut: {yerel} â†’ {uzak}  â•‘\n"
        f"  â•‘  Skill ve kod gÃ¼ncellemesi var.       â•‘\n"
        f"  â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•\n"
        f"  '/guncelle' â†’ gÃ¼ncelle\n"
        f"  '/guncelle kapat' â†’ bir daha sorma\n"
    )


# â”€â”€ /guncelle komut yÃ¶nlendirici â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


def komut_isle(args: str = "") -> bool:
    """
    main.py'den '/guncelle [args]' ÅŸeklinde Ã§aÄŸrÄ±lÄ±r.

    Args:
        args: "kapat", "ac", "durum" veya "" (gÃ¼ncelle)

    Returns:
        True â†’ program yeniden baÅŸlatÄ±lmalÄ±
    """
    args = args.strip().lower()

    if args == "kapat":
        otomatik_kapat()
        return False

    if args == "ac":
        otomatik_ac()
        return False

    if args == "durum":
        durum_goster()
        return False

    # VarsayÄ±lan: gÃ¼ncelle
    return guncelle(onaysiz=False)


# â”€â”€ DoÄŸrudan Ã§alÄ±ÅŸtÄ±rma â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

if __name__ == "__main__":
    args = sys.argv[1:]

    if "--kapat" in args:
        otomatik_kapat()
        sys.exit(0)

    if "--ac" in args:
        otomatik_ac()
        sys.exit(0)

    if "--durum" in args:
        durum_goster()
        sys.exit(0)

    print("=== ReYMeN GÃ¼ncelleme AracÄ± ===")
    print(f"Repo  : {GITHUB_REPO}")
    print(f"Yerel : {_yerel_commit() or '(git repo deÄŸil)'}")

    if "KULLANICI_ADI" in GITHUB_REPO:
        print("\n[!] guncelle.py iÃ§indeki GITHUB_REPO deÄŸiÅŸkenini ayarla.")
        print('    Ã–rnek: GITHUB_REPO = "markopasa/ReYMeN"')
        sys.exit(1)

    guncelle(onaysiz=False)
