# -*- coding: utf-8 -*-
"""
db_backup.py â€” ReYMeN Veritabani Yedekleme Sistemi

*** YENI DB KURALI (MADDE 3.7): ***
Yeni bir .db/.sqlite dosyasi olusturmadan once:
1. Mevcut bir DB'ye yeni tablo eklenebilir mi? (tercih edilen)
2. Yeni DB zorunluysa, bu karar decisions.md'ye kaydedilmeli
3. Yeni DB'nin backup kapsamina alindigindan emin olunmali
4. Eski/kullanilmayan DB'ler aylik temizlikte silinmeli
*** IHLAL: Duzelt-sonra-tekrarla pattern'ini tetikler ***

Hedef: OneDrive Belgeler + yerel yedek (hibrit)
SÄ±klik: Haftalik tam + gunluk incremental
Kapsam: .db, .sqlite3, config.yaml, durum.json, .env.example
(Hassas .env DAHIL EDILMEZ)

Kullanim:
  python db_backup.py              # Gunluk incremental
  python db_backup.py --full       # Haftalik tam
  python db_backup.py --list       # Mevcut yedekleri listele
  python db_backup.py --check      # Son yedek yasini kontrol et
  python db_backup.py --restore-test  # Geri yuklenebilirlik testi
"""

import hashlib
import json
import os
import shutil
import sqlite3
import sys
from datetime import datetime, timedelta
from pathlib import Path

# â”€â”€ Bulgu panosu audit (K1-K4) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
_FB_IMPORTED = False


def _findings_board_kaydet(sonuc: dict, tip: str):
    """db_backup sonucunu findings_board'a kaydet (otomatik)."""
    global _FB_IMPORTED
    try:
        if not _FB_IMPORTED:
            import importlib

            _fb = importlib.import_module("reymen.sistem.findings_board")
            globals()["_audit_tamamla"] = _fb.audit_tamamla
            _FB_IMPORTED = True
        basarili = sonuc.get("basarili", 0)
        basarisiz = sonuc.get("basarisiz", 0)
        toplam = sonuc.get("toplam_dosya", 0) or sonuc.get("taranan_dosya", 0)
        globals()["_audit_tamamla"](
            "reymen",
            [
                {
                    "konu": f"db_backup {tip}: {toplam} dosya, {basarili} basarili, {basarisiz} basarisiz",
                    "onem": "kritik"
                    if basarisiz > 0
                    else ("orta" if toplam > 0 else "dusuk"),
                    "dosya_yolu": f"db_backup/{tip}",
                    "aciklama": sonuc.get("mesaj", f"{tip} yedek tamamlandi"),
                    "durum": "duzeltildi" if basarisiz == 0 else "yeni",
                }
            ],
        )
    except Exception:
        pass  # findings_board yoksa sessizce gec


# ============================================================
# KONFIGURASYON
# ============================================================

PROJE_KOK = Path(__file__).parent.parent.parent.parent  # ReYMeN-Ajan/
if not (PROJE_KOK / "durum.json").exists():
    # Fallback: script her yerden calistirilabilir
    PROJE_KOK = Path.cwd()

# Birincil hedef: OneDrive Belgeler (bulut senkronizasyonu icin)
ONEDRIVE_BELGELER = Path.home() / "OneDrive" / "Belgeler" / "ReYMeN-DB-Yedek"
# Ikincil hedef: yerel (OneDrive problemsiz calismazsa)
YEREL_YEDEK = Path.home() / "ReYMeN-DB-Yedek"
# Quarantine klasoru (silinecek eski dosyalar icin)
QUARANTINE = PROJE_KOK / "__silinecek_eski"

# Yedeklenecek dosya pattern'leri
DB_PATTERNleri = [".db", ".sqlite3", ".sqlite"]
CONFIG_DOSYALARI = [
    "durum.json",
    "shared_state/reymen_state.json",
    "config.yaml",
    ".env.example",
    ".gitignore",
]

# HASSAS dosyalar â€” ASLA yedeklenmez
HASSAS_DOSYALAR = [
    ".env",
    "token.txt",
    "token.json",
    "credentials.json",
    "service_account.json",
]

# HARIC tutulacak klasorler
HARIC_KLASORLER = {
    "venv",
    ".git",
    "__pycache__",
    "node_modules",
    ".venv",
    "env",
    ".pytest-cache",
    ".pytest_cache",
    "__silinecek_eski",
}

# Backup yonetim dosyasi
YONETIM_DOSYASI = PROJE_KOK / ".ReYMeN" / "backup_state.json"


def _yonetim_oku() -> dict:
    """Backup yonetim dosyasini oku."""
    if YONETIM_DOSYASI.exists():
        try:
            return json.loads(YONETIM_DOSYASI.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}
    return {"full_backups": [], "incremental_backups": [], "last_restore_test": None}


def _yonetim_yaz(veri: dict):
    """Backup yonetim dosyasina yaz."""
    YONETIM_DOSYASI.parent.mkdir(parents=True, exist_ok=True)
    YONETIM_DOSYASI.write_text(
        json.dumps(veri, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def _db_dosyalari() -> list[Path]:
    """Projedeki tum DB dosyalarini bul (venv ve git haric)."""
    db_dosyalar = []
    for root, dirs, files in os.walk(str(PROJE_KOK)):
        # Haric klasorleri atla
        rel = Path(root).relative_to(PROJE_KOK)
        if any(str(rel).startswith(h) for h in HARIC_KLASORLER):
            continue
        if str(rel).startswith("venv") or str(rel).startswith(".git"):
            continue

        for f in files:
            fpath = Path(root) / f
            if any(f.endswith(p) for p in DB_PATTERNleri):
                db_dosyalar.append(fpath)
            elif f in CONFIG_DOSYALARI:
                db_dosyalar.append(fpath)
            elif f in HASSAS_DOSYALAR:
                pass  # Hassas dosyalari atla

    return sorted(db_dosyalar)


def _dosya_hash(dosya_yolu: Path) -> str:
    """Dosyanin MD5 hash'ini hesapla."""
    if not dosya_yolu.exists():
        return ""
    h = hashlib.md5()
    with open(dosya_yolu, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _yedek_klasoru(tam_mi: bool = False) -> Path:
    """Hedef yedek klasorunu belirle."""
    bugun = datetime.now().strftime("%Y-%m-%d")
    tip = "tam" if tam_mi else "gunluk"

    # OneDrive varsa onu kullan, yoksa yerel
    if ONEDRIVE_BELGELER.exists():
        hedef = ONEDRIVE_BELGELER / tip / bugun
    else:
        hedef = YEREL_YEDEK / tip / bugun

    hedef.mkdir(parents=True, exist_ok=True)
    return hedef


def _sqlite_integrity_check(db_yolu: Path) -> tuple[bool, str]:
    """SQLite veritabaninin butunlugunu kontrol et."""
    try:
        conn = sqlite3.connect(str(db_yolu))
        cur = conn.cursor()
        sonuc = cur.execute("PRAGMA integrity_check").fetchone()
        conn.close()
        if sonuc and sonuc[0] == "ok":
            return True, "ok"
        return False, str(sonuc[0]) if sonuc else "bilinmiyor"
    except Exception as e:
        return False, str(e)


def tam_yedek() -> dict:
    """Tum DB + config dosyalarinin tam yedeÄŸini al."""
    yonetim = _yonetim_oku()
    hedef = _yedek_klasoru(tam_mi=True)
    dosyalar = _db_dosyalari()

    rapor = {
        "tarih": datetime.now().isoformat(),
        "tip": "tam",
        "hedef": str(hedef),
        "toplam_dosya": len(dosyalar),
        "basarili": 0,
        "basarisiz": 0,
        "hatalar": [],
        "dosyalar": [],
    }

    for dosya in dosyalar:
        try:
            rel_path = dosya.relative_to(PROJE_KOK)
            hedef_dosya = hedef / rel_path
            hedef_dosya.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(dosya, hedef_dosya)

            # Integrity check (sadece .db dosyalari icin)
            integrity = None
            if dosya.suffix in (".db", ".sqlite3", ".sqlite"):
                ok, msg = _sqlite_integrity_check(dosya)
                integrity = {"ok": ok, "msg": msg}

            rapor["dosyalar"].append(
                {
                    "dosya": str(rel_path),
                    "boyut": dosya.stat().st_size,
                    "hash": _dosya_hash(dosya),
                    "integrity": integrity,
                }
            )
            rapor["basarili"] += 1
        except Exception as e:
            rapor["basarisiz"] += 1
            rapor["hatalar"].append(f"{dosya.name}: {e}")

    # Yonetim dosyasini guncelle
    yonetim["full_backups"].append(
        {
            "tarih": datetime.now().isoformat(),
            "hedef": str(hedef),
            "dosya_sayisi": rapor["basarili"],
            "toplam_boyut": sum(d["boyut"] for d in rapor["dosyalar"] if "boyut" in d),
        }
    )
    _yonetim_yaz(yonetim)

    return rapor


def gunluk_yedek() -> dict:
    """Sadece degisen dosyalarin yedeÄŸini al (incremental)."""
    yonetim = _yonetim_oku()
    hedef = _yedek_klasoru(tam_mi=False)
    dosyalar = _db_dosyalari()

    # Son tam yedek tarihini bul
    son_tam = ""
    if yonetim.get("full_backups"):
        son_tam = yonetim["full_backups"][-1]["tarih"]

    # Son 24 saatte degisen dosyalari bul
    son_24s = datetime.now() - timedelta(hours=24)
    degisenler = [
        d for d in dosyalar if datetime.fromtimestamp(d.stat().st_mtime) > son_24s
    ]

    rapor = {
        "tarih": datetime.now().isoformat(),
        "tip": "gunluk",
        "son_tam_yedek": son_tam,
        "hedef": str(hedef),
        "taranan_dosya": len(dosyalar),
        "degisen_dosya": len(degisenler),
        "basarili": 0,
        "basarisiz": 0,
        "hatalar": [],
        "dosyalar": [],
    }

    for dosya in degisenler:
        try:
            rel_path = dosya.relative_to(PROJE_KOK)
            hedef_dosya = hedef / rel_path
            hedef_dosya.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(dosya, hedef_dosya)
            rapor["dosyalar"].append(
                {
                    "dosya": str(rel_path),
                    "boyut": dosya.stat().st_size,
                    "hash": _dosya_hash(dosya),
                    "degisim_tarihi": datetime.fromtimestamp(
                        dosya.stat().st_mtime
                    ).isoformat(),
                }
            )
            rapor["basarili"] += 1
        except Exception as e:
            rapor["basarisiz"] += 1
            rapor["hatalar"].append(f"{dosya.name}: {e}")

    rapor["mesaj"] = (
        f"{rapor['degisen_dosya']} dosyadan {rapor['basarili']}'i yedeklendi"
    )
    return rapor


def yedek_yasi_kontrol() -> dict:
    """Son yedegin kac gun once alindigini kontrol et."""
    yonetim = _yonetim_oku()

    son_tam = None
    if yonetim.get("full_backups"):
        son_tam_iso = yonetim["full_backups"][-1]["tarih"]
        son_tam = datetime.fromisoformat(son_tam_iso)
        gun_farki = (datetime.now() - son_tam).days
    else:
        gun_farki = 999

    # ReYMeN-memory-backup klasorunu de kontrol et
    memory_backup = PROJE_KOK / "ReYMeN-memory-backup"
    memory_yasi = 999
    if memory_backup.exists():
        en_son = max(
            (p.stat().st_mtime for p in memory_backup.rglob("*") if p.is_file()),
            default=0,
        )
        if en_son > 0:
            memory_yasi = (datetime.now() - datetime.fromtimestamp(en_son)).days

    return {
        "analiz_tarihi": datetime.now().isoformat(),
        "son_tam_yedek_gun": gun_farki,
        "son_tam_yedek_str": f"{gun_farki} gun once"
        if gun_farki < 365
        else "Hic alinmamis",
        "memory_backup_yasi_gun": memory_yasi,
        "memory_backup_durum": "GUNUNU GECIRMIS" if memory_yasi > 14 else "GUNcel",
        "acil_mi": gun_farki > 7,
        "oneri": (
            f"âš ï¸ Son yedek {gun_farki} gun once! Hemen tam yedek al."
            if gun_farki > 7
            else f"âœ… Son yedek {gun_farki} gun once. Durum normal."
        ),
    }


def restore_test() -> dict:
    """En son yedegin geri yuklenebilirligini test et."""
    yonetim = _yonetim_oku()
    if not yonetim.get("full_backups"):
        return {"durum": "HATA", "mesaj": "Hic tam yedek bulunamadi, test yapilamadi."}

    en_son = yonetim["full_backups"][-1]
    hedef = Path(en_son["hedef"])

    if not hedef.exists():
        return {"durum": "HATA", "mesaj": f"Yedek klasoru bulunamadi: {hedef}"}

    rapor = {
        "tarih": datetime.now().isoformat(),
        "yedek_tarihi": en_son["tarih"],
        "yedek_klasoru": str(hedef),
        "test_klasoru": str(
            QUARANTINE / "restore_test" / datetime.now().strftime("%Y%m%d_%H%M%S")
        ),
        "durum": "BASARILI",
        "test_edilen_dosya": 0,
        "basarili": 0,
        "basarisiz": 0,
        "detay": [],
    }

    test_klasor = Path(rapor["test_klasoru"])
    test_klasor.mkdir(parents=True, exist_ok=True)

    # Yedekteki tum dosyalari test klasorune kopyala ve dogrula
    for root, dirs, files in os.walk(str(hedef)):
        for f in files:
            kaynak = Path(root) / f
            rel = kaynak.relative_to(hedef)
            hedef_test = test_klasor / rel
            hedef_test.parent.mkdir(parents=True, exist_ok=True)

            try:
                shutil.copy2(kaynak, hedef_test)

                # Hash dogrulama
                kaynak_hash = _dosya_hash(kaynak)
                hedef_hash = _dosya_hash(hedef_test)
                hash_ok = kaynak_hash == hedef_hash

                # SQLite integrity (sadece DB'ler)
                integrity = None
                if f.endswith((".db", ".sqlite3", ".sqlite")):
                    ok, msg = _sqlite_integrity_check(hedef_test)
                    integrity = {"ok": ok, "msg": msg}

                rapor["test_edilen_dosya"] += 1
                if hash_ok:
                    rapor["basarili"] += 1
                    rapor["detay"].append(
                        {
                            "dosya": str(rel),
                            "hash_dogrulama": "OK",
                            "integrity": integrity,
                        }
                    )
                else:
                    rapor["basarisiz"] += 1
                    rapor["detay"].append(
                        {
                            "dosya": str(rel),
                            "hash_dogrulama": "HATA",
                            "integrity": integrity,
                        }
                    )
                    rapor["durum"] = "KISMEN BASARISIZ"

            except Exception as e:
                rapor["basarisiz"] += 1
                rapor["detay"].append({"dosya": str(rel), "hata": str(e)})
                rapor["durum"] = "KISMEN BASARISIZ"

    # Test klasorunu temizle
    shutil.rmtree(test_klasor, ignore_errors=True)

    # Yonetimi guncelle
    yonetim["last_restore_test"] = rapor["tarih"]
    _yonetim_yaz(yonetim)

    rapor["mesaj"] = (
        f"{rapor['test_edilen_dosya']} dosyadan {rapor['basarili']}'i basarili, "
        f"{rapor['basarisiz']}'i basarisiz"
    )
    return rapor


def listele() -> list[dict]:
    """Mevcut yedekleri listele."""
    yonetim = _yonetim_oku()
    liste = []

    for tip in ["full_backups", "incremental_backups"]:
        for kayit in yonetim.get(tip, []):
            hedef = Path(kayit["hedef"])
            var_mi = hedef.exists() and any(hedef.iterdir())
            liste.append(
                {
                    "tip": tip.replace("_backups", ""),
                    "tarih": kayit["tarih"],
                    "dosya_sayisi": kayit.get("dosya_sayisi", "?"),
                    "klasor": kayit["hedef"],
                    "mevcut_mu": "EVET" if var_mi else "HAYIR (silinmis)",
                }
            )

    restore_test_tarih = yonetim.get("last_restore_test", "Hic yapilmamis")
    if liste:
        liste.append(
            {
                "tip": "---",
                "tarih": f"Son restore testi: {restore_test_tarih}",
                "dosya_sayisi": "",
                "klasor": "",
                "mevcut_mu": "",
            }
        )

    return liste if liste else [{"mesaj": "Henuz yedek alinmamis."}]


def eski_kopyalari_quarantine() -> dict:
    """ReYMeN-memory-backup icindeki eski DB kopyalarini quarantine'e tasi."""
    memory_backup = PROJE_KOK / "ReYMeN-memory-backup"
    if not memory_backup.exists():
        return {"durum": "ATLANDI", "mesaj": "ReYMeN-memory-backup klasoru yok"}

    quarantine_klasor = (
        QUARANTINE / f"memory_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    )
    tasinanlar = []

    # Eski DB kopyalarini bul
    for root, dirs, files in os.walk(str(memory_backup)):
        for f in files:
            if f.endswith((".db", ".sqlite3", ".sqlite")):
                kaynak = Path(root) / f
                rel = kaynak.relative_to(memory_backup)
                hedef = quarantine_klasor / rel
                hedef.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(kaynak), str(hedef))
                tasinanlar.append(str(rel))

    return {
        "durum": "TAMAM" if tasinanlar else "TEMIZ",
        "quarantine_klasoru": str(quarantine_klasor),
        "tasinan_dosya": len(tasinanlar),
        "dosyalar": tasinanlar,
    }


def ilk_tam_yedek_ve_temizlik():
    """MADDE 1.3: Ilk calistirmada mevcut durumu yedekle + eski kopyalari temizle."""
    print("=" * 60)
    print("REYMEN DB BACKUP â€” ILK CALISTIRMA")
    print("=" * 60)

    # 1. Eski kopyalari quarantine'e tasi
    print("\n[1/3] Eski kopyalar quarantine'e tasiniyor...")
    q_result = eski_kopyalari_quarantine()
    print(
        f"  {q_result['durum']}: {q_result.get('mesaj', '')} ({q_result.get('tasinan_dosya', 0)} dosya)"
    )

    # 2. Tam yedek al
    print("\n[2/3] Ilk tam yedek aliniyor...")
    tam = tam_yedek()
    print(f"  {tam['basarili']}/{tam['toplam_dosya']} dosya yedeklendi")
    if tam["basarisiz"] > 0:
        for h in tam["hatalar"]:
            print(f"  HATA: {h}")

    # 3. Restore testi yap
    print("\n[3/3] Geri yuklenebilirlik testi yapiliyor...")
    test = restore_test()
    print(f"  {test['durum']}: {test.get('mesaj', '')}")
    if test["basarisiz"] > 0:
        for d in test["detay"]:
            if d.get("hash_dogrulama") == "HATA" or d.get("hata"):
                print(
                    f"  SORUN: {d['dosya']} â€” {d.get('hata', 'hash dogrulama basarisiz')}"
                )

    print("\n" + "=" * 60)
    print(f"ILK YEDEK TAMAMLANDI â€” Hedef: {ONEDRIVE_BELGELER}")
    print(f"Quarantine: {QUARANTINE}")
    print("=" * 60)

    return {"tam_yedek": tam, "restore_test": test, "quarantine": q_result}


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="ReYMeN DB Yedekleme")
    parser.add_argument("--full", action="store_true", help="Tam yedek")
    parser.add_argument("--list", action="store_true", help="Yedekleri listele")
    parser.add_argument("--check", action="store_true", help="Yedek yasini kontrol et")
    parser.add_argument(
        "--restore-test", action="store_true", help="Geri yuklenebilirlik testi"
    )
    parser.add_argument(
        "--ilk", action="store_true", help="Ilk calistirma (temizlik + yedek + test)"
    )
    parser.add_argument(
        "--quarantine-eski",
        action="store_true",
        help="Eski kopyalari quarantine'e tasi",
    )

    args = parser.parse_args()

    if args.ilk:
        sonuc = ilk_tam_yedek_ve_temizlik()
        print(json.dumps(sonuc, indent=2, ensure_ascii=False))
        _findings_board_kaydet(sonuc.get("tam_yedek", {}), "ilk_tam")
    elif args.full:
        sonuc = tam_yedek()
        print(json.dumps(sonuc, indent=2, ensure_ascii=False))
        _findings_board_kaydet(sonuc, "tam")
    elif args.list:
        sonuc = listele()
        print(json.dumps(sonuc, indent=2, ensure_ascii=False))
    elif args.check:
        sonuc = yedek_yasi_kontrol()
        print(json.dumps(sonuc, indent=2, ensure_ascii=False))
    elif args.restore_test:
        sonuc = restore_test()
        print(json.dumps(sonuc, indent=2, ensure_ascii=False))
    elif args.quarantine_eski:
        sonuc = eski_kopyalari_quarantine()
        print(json.dumps(sonuc, indent=2, ensure_ascii=False))
    else:
        # Varsayilan: gunluk incremental
        sonuc = gunluk_yedek()
        print(json.dumps(sonuc, indent=2, ensure_ascii=False))
        _findings_board_kaydet(sonuc, "gunluk")
