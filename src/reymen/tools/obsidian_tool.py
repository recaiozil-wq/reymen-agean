# -*- coding: utf-8 -*-
"""
obsidian_tool.py — ReYMeN Obsidian Vault Integration.

Inside Obsidian vault (.md):
  - List files
  - Read files
  - Create new notes
  - Update notes
  - Keyword / grep search
  - Explore vault structure

Vault path:
  1. Config: config.yaml > obsidian.vault_path
  2. Parameter: user can pass vault path directly to the tool
  3. Default: searches for .obsidian/ folder in project root

Dependencies: none (Python stdlib only)
"""

import logging
import os
import re
import subprocess
from pathlib import Path
from typing import List, Optional, Tuple

logger = logging.getLogger(__name__)

# ── Sabitler ─────────────────────────────────────────────────────────────

GUVENLI_UZANTILAR = {".md"}
MAKS_DOSYA_BOYUTU = 10 * 1024 * 1024  # 10 MB
MAKS_LISTELEME = 200  # tek seferde max dosya listele
MAKS_ARAMA_SONUC = 50


# ── Yardımcı Fonksiyonlar ────────────────────────────────────────────────


def _vault_yolu_bul(istenen_yol: str = "") -> Tuple[bool, str]:
    """Find the Obsidian vault path.

    Priority:
      1. Requested parameter path (if provided by user)
      2. config.yaml > obsidian.vault_path
      3. Search for .obsidian/ folder in project root
      4. Scan Obsidian vaults in user home directory

    Returns:
        (basarili_mi, vault_yolu | hata_mesaji)
    """
    # 1. Parametre olarak verilmiş yol
    if istenen_yol and istenen_yol.strip():
        yol = Path(istenen_yol.strip()).resolve()
        if yol.is_dir():
            return (True, str(yol))
        return (False, f"[Obsidian] Belirtilen yol bulunamadı: {istenen_yol}")

    # 2. config.yaml oku
    try:
        import yaml
        kok = Path(__file__).resolve().parent.parent.parent.parent  # ReYMeN-Ajan/
        config_yaml = kok / "config.yaml"
        if config_yaml.exists():
            with open(config_yaml, "r", encoding="utf-8") as f:
                cfg = yaml.safe_load(f)
            if cfg and "obsidian" in cfg and "vault_path" in cfg["obsidian"]:
                cfg_yol = Path(cfg["obsidian"]["vault_path"]).resolve()
                if cfg_yol.is_dir():
                    return (True, str(cfg_yol))
                return (False, f"[Obsidian] config.yaml'deki vault_path geçersiz: {cfg_yol}")
    except ImportError:
        pass  # yaml yoksa sessiz geç
    except Exception:
        pass

    # 3. Proje kökünde .obsidian/ klasörü ara
    proje_kok = Path(__file__).resolve().parent.parent.parent.parent  # ReYMeN-Ajan/
    obsidian_klasor = proje_kok / ".obsidian"
    if obsidian_klasor.is_dir():
        # vault_root = .obsidian'in bir üstü (yani proje kökü)
        return (True, str(proje_kok))

    # 4. Kullanıcı ana dizininde Obsidian vault'ları tara
    kullanici = Path.home()
    for aday in [
        kullanici / "Obsidian",
        kullanici / "Documents" / "Obsidian",
        kullanici / "Documents" / "Obsidian Vault",
        kullanici / "Desktop" / "Obsidian",
    ]:
        if aday.is_dir() and list(aday.glob("*.md"))[:1]:
            return (True, str(aday))

    return (False, "[Obsidian] Vault yolu bulunamadı. config.yaml > obsidian.vault_path ekleyin "
                   "veya araç çağrısında vault yolunu parametre olarak belirtin.")


def _yol_guvenli_mi(vault_kok: str, hedef: str) -> Tuple[bool, str]:
    """Verify target path stays within vault (directory traversal protection)."""
    try:
        kok = Path(vault_kok).resolve()
        hedef_abs = (kok / hedef).resolve()
        if not str(hedef_abs).startswith(str(kok)):
            return (False, f"[Guvenlik] Hedef yol vault dışına çıkıyor: {hedef}")
        return (True, str(hedef_abs))
    except Exception as e:
        return (False, f"[Guvenlik] Yol dogrulama hatasi: {e}")


def _md_dosyalari_listele(vault_kok: str, alt_dizin: str = "", uzanti: str = ".md") -> List[dict]:
    """List .md files in the vault.

    Returns:
        [{"yol": "relative/path/note.md", "ad": "note", "boyut": 1234, "degisti": "2024-01-01"}, ...]
    """
    baslangic = Path(vault_kok)
    if alt_dizin:
        baslangic = baslangic / alt_dizin

    if not baslangic.is_dir():
        return []

    sonuclar = []
    try:
        for f in sorted(baslangic.rglob(f"*{uzanti}"))[:MAKS_LISTELEME]:
            try:
                goreceli = str(f.relative_to(Path(vault_kok)))
                boyut = f.stat().st_size if f.exists() else 0
                degisti = None
                try:
                    mtime = f.stat().st_mtime
                    import datetime
                    degisti = datetime.datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M")
                except Exception:
                    pass
                sonuclar.append({
                    "yol": goreceli.replace("\\", "/"),
                    "ad": f.stem,
                    "boyut": boyut,
                    "degisti": degisti,
                })
            except Exception:
                continue
    except Exception as e:
        logger.warning("[Obsidian] Dosya listeleme hatasi: %s", e)

    return sonuclar


def _md_oku(vault_kok: str, dosya_yolu: str) -> Tuple[bool, str]:
    """Read the contents of a .md file.

    Returns:
        (basarili_mi, icerik | hata_mesaji)
    """
    guvenli, tam_yol = _yol_guvenli_mi(vault_kok, dosya_yolu)
    if not guvenli:
        return (False, tam_yol)

    yol = Path(tam_yol)
    if not yol.exists():
        return (False, f"[Obsidian] Dosya bulunamadı: {dosya_yolu}")
    if yol.suffix.lower() not in GUVENLI_UZANTILAR:
        return (False, f"[Obsidian] Sadece .md dosyalari okunabilir: {dosya_yolu}")
    if yol.stat().st_size > MAKS_DOSYA_BOYUTU:
        return (False, f"[Obsidian] Dosya çok büyük (>10MB): {dosya_yolu}")

    try:
        icerik = yol.read_text(encoding="utf-8")
        return (True, icerik)
    except Exception as e:
        return (False, f"[Obsidian] Okuma hatasi: {e}")


def _not_olustur(vault_kok: str, dosya_yolu: str, icerik: str) -> Tuple[bool, str]:
    """Create a new .md note.

    Args:
        vault_kok: Vault root directory
        dosya_yolu: Target path relative to vault (e.g. "gunluk/2024-01-01.md")
        icerik: Markdown content

    Returns:
        (basarili_mi, sonuc_mesaji | hata_mesaji)
    """
    guvenli, tam_yol = _yol_guvenli_mi(vault_kok, dosya_yolu)
    if not guvenli:
        return (False, tam_yol)

    yol = Path(tam_yol)
    if yol.exists():
        return (False, f"[Obsidian] Dosya zaten var: {dosya_yolu}")

    # Uzantı kontrolü
    if not yol.suffix:
        yol = yol.with_suffix(".md")
    elif yol.suffix.lower() not in GUVENLI_UZANTILAR:
        return (False, f"[Obsidian] Sadece .md dosyalari olusturulabilir: {dosya_yolu}")

    try:
        yol.parent.mkdir(parents=True, exist_ok=True)
        yol.write_text(icerik, encoding="utf-8")
        return (True, f"[Obsidian] Not oluşturuldu: {dosya_yolu}")
    except Exception as e:
        return (False, f"[Obsidian] Oluşturma hatası: {e}")


def _not_guncelle(vault_kok: str, dosya_yolu: str, icerik: str, mod: str = "overwrite") -> Tuple[bool, str]:
    """Update an existing .md note.

    Args:
        vault_kok: Vault root directory
        dosya_yolu: File path relative to vault
        icerik: New content or content to add
        mod: "overwrite" (replace entirely) | "append" (append to end) | "prepend" (prepend to start)

    Returns:
        (basarili_mi, sonuc_mesaji | hata_mesaji)
    """
    guvenli, tam_yol = _yol_guvenli_mi(vault_kok, dosya_yolu)
    if not guvenli:
        return (False, tam_yol)

    yol = Path(tam_yol)
    if not yol.exists():
        return (False, f"[Obsidian] Dosya bulunamadı: {dosya_yolu}")

    try:
        if mod == "overwrite":
            yol.write_text(icerik, encoding="utf-8")
        elif mod == "append":
            mevcut = yol.read_text(encoding="utf-8")
            yol.write_text(mevcut.rstrip() + "\n\n" + icerik, encoding="utf-8")
        elif mod == "prepend":
            mevcut = yol.read_text(encoding="utf-8")
            yol.write_text(icerik.rstrip() + "\n\n" + mevcut, encoding="utf-8")
        else:
            return (False, f"[Obsidian] Geçersiz mod: {mod} (secenekler: overwrite, append, prepend)")

        return (True, f"[Obsidian] Not güncellendi ({mod}): {dosya_yolu}")
    except Exception as e:
        return (False, f"[Obsidian] Güncelleme hatası: {e}")


def _vault_ara(vault_kok: str, sorgu: str, dosya_adi_filtre: str = "", 
               harf_duyarlilik: bool = False) -> Tuple[bool, str]:
    """Search vault by keyword / grep.

    Args:
        vault_kok: Vault root directory
        sorgu: Text to search (supports regex)
        dosya_adi_filtre: Search only specific filenames (e.g. "gunluk/*")
        harf_duyarlilik: Case sensitivity

    Returns:
        (basarili_mi, sonuclar | hata_mesaji)
    """
    if not sorgu or not sorgu.strip():
        return (False, "[Obsidian] Arama sorgusu boş olamaz")

    try:
        import re as regex_module
        try:
            pattern = regex_module.compile(sorgu, 0 if harf_duyarlilik else regex_module.IGNORECASE)
        except regex_module.error as e:
            return (False, f"[Obsidian] Geçersiz regex: {e}")

        baslangic = Path(vault_kok)
        sonuclar = []
        dosya_sayisi = 0
        eslesme_sayisi = 0

        for md_yol in sorted(baslangic.rglob("*.md")):
            # Dosya adı filtresi
            if dosya_adi_filtre:
                try:
                    if not regex_module.search(dosya_adi_filtre.replace("*", ".*"), str(md_yol.name), 
                                                regex_module.IGNORECASE):
                        continue
                except regex_module.error:
                    pass

            dosya_sayisi += 1
            try:
                icerik = md_yol.read_text(encoding="utf-8", errors="replace")
                for i, satir in enumerate(icerik.split("\n"), 1):
                    if pattern.search(satir):
                        goreceli = str(md_yol.relative_to(Path(vault_kok))).replace("\\", "/")
                        satir_kesik = satir.strip()[:150]
                        sonuclar.append(f"{goreceli}:{i}: {satir_kesik}")
                        eslesme_sayisi += 1
                        if len(sonuclar) >= MAKS_ARAMA_SONUC:
                            break
            except Exception:
                continue
            if len(sonuclar) >= MAKS_ARAMA_SONUC:
                break

        if not sonuclar:
            return (True, f"[Obsidian] Arama sonucu bulunamadı: '{sorgu}' ({dosya_sayisi} dosya tarandı)")

        ozet = f"[Obsidian] '{sorgu}' için {eslesme_sayisi} eşleşme ({dosya_sayisi} dosyada):\n"
        return (True, ozet + "\n".join(sonuclar))

    except Exception as e:
        return (False, f"[Obsidian] Arama hatası: {e}")


def _vault_bilgisi(vault_kok: str) -> Tuple[bool, str]:
    """Return summary info about the vault."""
    try:
        kok = Path(vault_kok)
        md_dosyalar = list(kok.rglob("*.md"))
        toplam_boyut = sum(f.stat().st_size for f in md_dosyalar if f.exists())
        alt_dizinler = len(set(f.parent for f in md_dosyalar))

        # En son değişen dosyalar
        son_dosyalar = sorted(md_dosyalar, key=lambda f: f.stat().st_mtime, reverse=True)[:5]
        son_liste = "\n".join(
            f"  - {str(f.relative_to(kok)).replace(chr(92), '/')}"
            for f in son_dosyalar
        )

        return (True, 
            f"[Obsidian] Vault Bilgisi:\n"
            f"  📁 Konum: {vault_kok}\n"
            f"  📄 Toplam not: {len(md_dosyalar)}\n"
            f"  📦 Toplam boyut: {toplam_boyut / 1024:.1f} KB\n"
            f"  📂 Alt dizin: {alt_dizinler}\n"
            f"  🕐 Son değişenler:\n{son_liste}")
    except Exception as e:
        return (False, f"[Obsidian] Vault bilgisi alınamadı: {e}")


# ── Motor Arayüz Fonksiyonları ────────────────────────────────────────────
# Bu fonksiyonlar motor._plugin_arac_kaydet() ile kaydedilir.
# Tümü tek parametre (ham string) alır, string döndürür.


def _obsidian_liste_araci(ham: str) -> str:
    """OBSIDIAN_LISTE: List .md files in the vault.

    Parameters (pipe-separated):
      - vault_yolu (opt): Vault directory (empty = use config/default)
      - alt_dizin (opt): Only show files in specific subdirectory
      - uzanti (opt): File extension (default: .md)

    Example: OBSIDIAN_LISTE(vault_yolu|alt_dizin)
    Example: OBSIDIAN_LISTE(C:/Users/marko/Obsidian Main|gunluk)
    """
    try:
        params = [p.strip() for p in ham.split("|", 2)] if ham.strip() else [""]
        istenen_vault = params[0] if len(params) > 0 and params[0] else ""
        alt_dizin = params[1] if len(params) > 1 else ""

        basarili, vault_yolu = _vault_yolu_bul(istenen_vault)
        if not basarili:
            return vault_yolu

        dosyalar = _md_dosyalari_listele(vault_yolu, alt_dizin)
        if not dosyalar:
            return f"[Obsidian] Vault'ta .md dosyasi bulunamadi: {vault_yolu}"

        satirlar = [f"[Obsidian] Vault: {vault_yolu} ({len(dosyalar)} dosya):"]
        for d in dosyalar:
            boyut_str = f"{d['boyut']/1024:.1f}KB" if d['boyut'] > 0 else "0B"
            satirlar.append(f"  📄 {d['yol']} ({boyut_str})")
            if d.get('degisti'):
                satirlar[-1] += f" — {d['degisti']}"

        return "\n".join(satirlar)

    except Exception as e:
        logger.exception("[Obsidian] Liste hatasi")
        return f"[Obsidian] Hata: {e}"


def _obsidian_oku_araci(ham: str) -> str:
    """OBSIDIAN_OKU: Read the contents of a .md file.

    Parameters (pipe-separated):
      - dosya_yolu: File path relative to vault (e.g. "gunluk/not.md")
      - vault_yolu (opt): Vault directory

    Example: OBSIDIAN_OKU(gunluk/2024-01-01.md)
    Example: OBSIDIAN_OKU(projeler/not.md|C:/Users/marko/Obsidian Main)
    """
    try:
        params = [p.strip() for p in ham.split("|", 1)] if ham.strip() else [""]
        dosya_yolu = params[0] if params[0] else ""
        istenen_vault = params[1] if len(params) > 1 else ""

        if not dosya_yolu:
            return ("[Obsidian] Kullanım: OBSIDIAN_OKU(dosya_yolu) — "
                    "örnek: OBSIDIAN_OKU(gunluk/2024-01-01.md)")

        basarili, vault_yolu = _vault_yolu_bul(istenen_vault)
        if not basarili:
            return vault_yolu

        basarili, icerik = _md_oku(vault_yolu, dosya_yolu)
        if not basarili:
            return icerik  # hata mesajı

        baslik = Path(dosya_yolu).name
        return f"[Obsidian] 📄 {baslik}\n```markdown\n{icerik}\n```"

    except Exception as e:
        logger.exception("[Obsidian] Okuma hatasi")
        return f"[Obsidian] Hata: {e}"


def _obsidian_yaz_araci(ham: str) -> str:
    """OBSIDIAN_YAZ: Create a new .md note.

    Parameters (|| separated — content may contain pipes/commas):
      - dosya_yolu: Target path relative to vault
      - icerik: Markdown content
      - vault_yolu (opt): Vault directory

    Example: OBSIDIAN_YAZ(gunluk/not.md||# Title\n\nContent here.)
    Example: OBSIDIAN_YAZ(projeler/not.md||# Project\\nPlan|C:/Users/marko/Obsidian)
    """
    try:
        # İlk parametre: dosya_yolu
        ilk_pipe = ham.find("||")
        if ilk_pipe == -1:
            return ("[Obsidian] Kullanım: OBSIDIAN_YAZ(dosya_yolu||içerik) — "
                    "içerik ve dosya yolunu || ile ayırın")

        dosya_yolu = ham[:ilk_pipe].strip()
        kalan = ham[ilk_pipe + 2:]

        # İkinci || vault_yolu için
        ikinci_pipe = -1
        # vault_yolu opsiyonel, en sonda | ile belirtilebilir
        # Ama ||'den sonraki kısım içerik olabilir, içinde | olabilir
        # O yüzden vault_yolu parametresini ayrı bir mekanizma ile almayalım
        # Sadece dosya_yolu ve içerik zorunlu
        icerik = kalan.strip()

        if not dosya_yolu or not icerik:
            return ("[Obsidian] Kullanım: OBSIDIAN_YAZ(dosya_yolu||içerik) — "
                    "her iki parametre de zorunlu")

        basarili, vault_yolu = _vault_yolu_bul("")
        if not basarili:
            return vault_yolu

        basarili, sonuc = _not_olustur(vault_yolu, dosya_yolu, icerik)
        if not basarili:
            return sonuc

        return sonuc + f"\n  📍 Vault: {vault_yolu}"

    except Exception as e:
        logger.exception("[Obsidian] Yazma hatasi")
        return f"[Obsidian] Hata: {e}"


def _obsidian_guncelle_araci(ham: str) -> str:
    """OBSIDIAN_GUNCELLE: Update an existing .md note.

    Parameters (|| separated):
      - dosya_yolu: File path relative to vault
      - icerik: New content
      - mod (opt): overwrite | append | prepend (default: overwrite)

    Example: OBSIDIAN_GUNCELLE(gunluk/not.md||# Updated||append)
    Example: OBSIDIAN_GUNCELLE(projeler/not.md||# New title||overwrite)
    """
    try:
        parts = ham.split("||")
        dosya_yolu = parts[0].strip() if len(parts) > 0 else ""
        icerik = parts[1].strip() if len(parts) > 1 else ""
        mod = parts[2].strip() if len(parts) > 2 else "overwrite"

        if not dosya_yolu or not icerik:
            return ("[Obsidian] Kullanım: OBSIDIAN_GUNCELLE(dosya_yolu||içerik||mod) — "
                    "dosya_yolu ve içerik zorunlu, mod opsiyonel (overwrite|append|prepend)")

        if mod not in ("overwrite", "append", "prepend"):
            return f"[Obsidian] Geçersiz mod: '{mod}' (secenekler: overwrite, append, prepend)"

        basarili, vault_yolu = _vault_yolu_bul("")
        if not basarili:
            return vault_yolu

        basarili, sonuc = _not_guncelle(vault_yolu, dosya_yolu, icerik, mod)
        if not basarili:
            return sonuc

        return sonuc + f"\n  📍 Vault: {vault_yolu}"

    except Exception as e:
        logger.exception("[Obsidian] Güncelleme hatasi")
        return f"[Obsidian] Hata: {e}"


def _obsidian_ara_araci(ham: str) -> str:
    """OBSIDIAN_ARA: Search vault text.

    Parameters (| separated):
      - sorgu: Text to search (supports regex)
      - vault_yolu (opt): Vault directory
      - harf_duyarli (opt): true|false (default: false)

    Example: OBSIDIAN_ARA(hello world)
    Example: OBSIDIAN_ARA(task|C:/Users/marko/Obsidian)
    Example: OBSIDIAN_ARA(Regex.*example||true)
    """
    try:
        params = [p.strip() for p in ham.split("|", 2)] if ham.strip() else [""]
        sorgu = params[0] if len(params) > 0 and params[0] else ""
        istenen_vault = params[1] if len(params) > 1 else ""
        harf_duyarli = params[2].lower() == "true" if len(params) > 2 else False

        if not sorgu:
            return "[Obsidian] Kullanım: OBSIDIAN_ARA(sorgu) — arama sorgusu zorunlu"

        basarili, vault_yolu = _vault_yolu_bul(istenen_vault)
        if not basarili:
            return vault_yolu

        basarili, sonuc = _vault_ara(vault_yolu, sorgu, harf_duyarlilik=harf_duyarli)
        if not basarili:
            return sonuc

        return sonuc

    except Exception as e:
        logger.exception("[Obsidian] Arama hatasi")
        return f"[Obsidian] Hata: {e}"


def _obsidian_bilgi_araci(ham: str) -> str:
    """OBSIDIAN_BILGI: Show summary info about the vault.

    Parameters:
      - vault_yolu (opt): Vault directory

    Example: OBSIDIAN_BILGI
    Example: OBSIDIAN_BILGI(C:/Users/marko/Obsidian Main)
    """
    try:
        istenen_vault = ham.strip() if ham.strip() else ""

        basarili, vault_yolu = _vault_yolu_bul(istenen_vault)
        if not basarili:
            return vault_yolu

        basarili, sonuc = _vault_bilgisi(vault_yolu)
        return sonuc

    except Exception as e:
        logger.exception("[Obsidian] Bilgi hatasi")
        return f"[Obsidian] Hata: {e}"


# ── Motor Kayıt ──────────────────────────────────────────────────────────


def motor_kaydet(motor) -> None:
    """Register Obsidian tools with the Motor.

    Automatically called from the module list in
    Motor._plugin_moduller_yukle().
    """
    if not hasattr(motor, "_plugin_arac_kaydet"):
        return

    k = lambda ad, fonk, aciklama="": motor._plugin_arac_kaydet(ad, fonk, aciklama)

    k("OBSIDIAN_LISTE", _obsidian_liste_araci,
      "Obsidian vault'taki .md dosyalarını listeler. "
      "Parametreler (|): vault_yolu (ops), alt_dizin (ops). "
      "Örnek: OBSIDIAN_LISTE veya OBSIDIAN_LISTE(C:/Users/marko/Vault|gunluk)")

    k("OBSIDIAN_OKU", _obsidian_oku_araci,
      "Obsidian vault'tan bir .md dosyasının içeriğini okur. "
      "Parametreler (|): dosya_yolu (zorunlu), vault_yolu (ops). "
      "Örnek: OBSIDIAN_OKU(gunluk/not.md)")

    k("OBSIDIAN_YAZ", _obsidian_yaz_araci,
      "Obsidian vault'ta yeni bir .md notu oluşturur. "
      "Parametreler (||): dosya_yolu || içerik. "
      "Örnek: OBSIDIAN_YAZ(projeler/fikir.md||# Fikir\\n\\nYeni fikir burada)")

    k("OBSIDIAN_GUNCELLE", _obsidian_guncelle_araci,
      "Obsidian vault'ta mevcut bir .md notunu günceller. "
      "Parametreler (||): dosya_yolu || içerik || mod (ops: overwrite|append|prepend). "
      "Örnek: OBSIDIAN_GUNCELLE(gunluk/not.md||# Yeni icerik||append)")

    k("OBSIDIAN_ARA", _obsidian_ara_araci,
      "Obsidian vault içinde metin araması yapar (regex destekler). "
      "Parametreler (|): sorgu (zorunlu), vault_yolu (ops), harf_duyarli (ops: true|false). "
      "Örnek: OBSIDIAN_ARA(görev) veya OBSIDIAN_ARA(Regex.*test|C:\\Vault|true)")

    k("OBSIDIAN_BILGI", _obsidian_bilgi_araci,
      "Obsidian vault hakkında özet bilgi gösterir: dosya sayısı, boyut, son değişenler. "
      "Parametre: vault_yolu (ops). "
      "Örnek: OBSIDIAN_BILGI veya OBSIDIAN_BILGI(C:/Users/marko/Vault)")

    print("[Obsidian] 6 arac kayit edildi: OBSIDIAN_LISTE, OBSIDIAN_OKU, OBSIDIAN_YAZ, "
          "OBSIDIAN_GUNCELLE, OBSIDIAN_ARA, OBSIDIAN_BILGI")
    logger.info("[Obsidian] 6 arac motor'a kaydedildi.")
