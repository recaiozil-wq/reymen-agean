# -*- coding: utf-8 -*-
"""
claude_code_tool.py — ReYMeN <-> Claude Code İşbirliği Aracı.

ReYMeN'in yerel Ollama modeli yetersiz kaldığında Claude Code CLI'yi
subprocess olarak çağırmasını sağlar.

Sunulan araçlar (ToolRegistry üzerinden):
  CLAUDE_YARDIM("görev")          — Claude'dan otonom yardım iste
  CLAUDE_ANALIZ("metin/kod")      — Claude'a analiz/inceleme yaptır
  CLAUDE_KOD_YAZ("açıklama")     — Claude'a kod yazdır
  CLAUDE_HATA_AYIKLA("hata+kod") — Claude ile hata ayıkla
  CLAUDE_PLAN("hedef")            — Claude'dan adım adım plan al
  CLAUDE_REVIZE("kod", "talep")   — Mevcut kodu Claude ile refactor et
  CLAUDE_DURUM()                  — claude CLI erişilebilir mi kontrol et

Gereksinim: claude CLI PATH'te olmalı.
Kurulum: https://claude.ai/code
"""

import os
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).parent.parent


def _claude_yolu_bul():
    """Claude CLI yolunu Windows/Unix uyumlu şekilde bul."""
    for aday in ("claude", "claude.cmd", "claude.exe"):
        yol = shutil.which(aday)
        if yol:
            return yol
    adaylar = [
        Path.home() / ".local" / "bin" / "claude.cmd",
        Path.home() / ".local" / "bin" / "claude.exe",
        Path.home() / "AppData" / "Local" / "Programs" / "claude" / "claude.exe",
    ]
    for aday in adaylar:
        if aday.exists():
            return str(aday)
    return None


_CLAUDE_EXE = _claude_yolu_bul()

_MAX_CIKTI = 6000
_VARSAYILAN_TIMEOUT = 120

_SISTEM_BAGLAMI = (
    "Sen ReYMeN adlı otonom yazılım ajanının yardımcısısın. "
    "ReYMeN, Windows'ta Ollama tabanlı yerel bir LLM ile ReAct döngüsü üzerinden çalışır. "
    "Senden bir alt görev isteniyor. Kısa, net, uygulanabilir Türkçe yanıt ver. "
    "Kod örneklerini doğrudan yaz; uzun açıklama yapma.\n\n"
)


def _claude_calistir(prompt, timeout=_VARSAYILAN_TIMEOUT):
    """claude CLI'yi -p (print) modu ile çağır, metin çıktısını döndür."""
    if not _CLAUDE_EXE or not Path(_CLAUDE_EXE).exists():
        return (
            "[Claude Code]: claude CLI bulunamadı. "
            "PATH'e ekleyin veya https://claude.ai/code adresinden kurun."
        )
    try:
        sonuc = subprocess.run(
            [_CLAUDE_EXE, "-p", prompt, "--output-format", "text"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            cwd=str(ROOT),
        )
        cikti = (sonuc.stdout or "").strip()
        hata_cikti = (sonuc.stderr or "").strip()

        if sonuc.returncode != 0 and not cikti:
            return f"[Claude Code Hata] (kod {sonuc.returncode}): {hata_cikti[:500]}"

        if not cikti:
            return "[Claude Code]: Yanıt boş döndü."

        if len(cikti) > _MAX_CIKTI:
            cikti = cikti[:_MAX_CIKTI] + f"\n... [+{len(cikti) - _MAX_CIKTI} karakter kesildi]"

        return cikti

    except subprocess.TimeoutExpired:
        return f"[Claude Code]: Zaman aşımı ({timeout}s). Daha kısa bir görev deneyin."
    except FileNotFoundError:
        return "[Claude Code]: claude komutu bulunamadı. PATH kontrolü yapın."
    except Exception as e:
        return f"[Claude Code Hata]: {e}"


def claude_yardim(gorev=""):
    """Claude Code'dan otonom yardım iste. Kullanım: CLAUDE_YARDIM("görev")"""
    if not gorev.strip():
        return "[Claude Code]: Görev parametresi boş olamaz."
    return _claude_calistir(_SISTEM_BAGLAMI + gorev)


def claude_analiz(metin=""):
    """Claude'a kod veya metin analizi yaptır. Kullanım: CLAUDE_ANALIZ("kod")"""
    if not metin.strip():
        return "[Claude Code]: Analiz için metin parametresi gerekli."
    prompt = (
        _SISTEM_BAGLAMI
        + "Aşağıdaki kodu veya metni analiz et. "
        "Hataları, iyileştirme noktalarını ve güvenlik sorunlarını maddeler hâlinde Türkçe yaz:\n\n"
        + metin
    )
    return _claude_calistir(prompt, timeout=90)


def claude_kod_yaz(aciklama=""):
    """Claude'a belirtilen işi yapan Python kodu yazdır. Kullanım: CLAUDE_KOD_YAZ("açıklama")"""
    if not aciklama.strip():
        return "[Claude Code]: Açıklama parametresi boş olamaz."
    prompt = (
        _SISTEM_BAGLAMI
        + "Aşağıdaki açıklamaya göre çalışan, temiz Python kodu yaz. "
        "Sadece kodu döndür; gereksiz yorum ekleme:\n\n"
        + aciklama
    )
    return _claude_calistir(prompt, timeout=90)


def claude_hata_ayikla(hata_ve_kod=""):
    """Claude ile Python/shell hatasını ayıkla. Kullanım: CLAUDE_HATA_AYIKLA("hata+kod")"""
    if not hata_ve_kod.strip():
        return "[Claude Code]: Hata mesajı ve/veya kod parametresi boş olamaz."
    prompt = (
        _SISTEM_BAGLAMI
        + "Aşağıdaki hata mesajını ve kodu incele. "
        "Hatanın nedenini bir cümleyle belirt, ardından düzeltilmiş kodu ver:\n\n"
        + hata_ve_kod
    )
    return _claude_calistir(prompt, timeout=90)


def claude_plan(hedef=""):
    """Claude'dan verilen hedef için adım adım plan al. Kullanım: CLAUDE_PLAN("hedef")"""
    if not hedef.strip():
        return "[Claude Code]: Hedef parametresi boş olamaz."
    prompt = (
        _SISTEM_BAGLAMI
        + "Aşağıdaki hedefe ulaşmak için numaralı, uygulanabilir adımlar listesi oluştur. "
        "Her adım tek bir iş içersin. Komut/kod gereken yerde kısaca belirt:\n\n"
        + hedef
    )
    return _claude_calistir(prompt, timeout=90)


def claude_revize(kod_ve_talep=""):
    """Mevcut kodu Claude ile refactor et. Kullanım: CLAUDE_REVIZE("kod\\n---\\ntalep")"""
    if not kod_ve_talep.strip():
        return "[Claude Code]: Kod ve talep parametresi boş olamaz."
    prompt = (
        _SISTEM_BAGLAMI
        + "Aşağıdaki kodu verilen talebe göre düzenle. "
        "Değiştirilmiş kodu doğrudan döndür; ne değiştirdiğini tek satırda özetle:\n\n"
        + kod_ve_talep
    )
    return _claude_calistir(prompt, timeout=120)


def claude_durum():
    """claude CLI'nin erişilebilir olup olmadığını kontrol et. Kullanım: CLAUDE_DURUM()"""
    if not _CLAUDE_EXE:
        return (
            "[Claude Code]: claude CLI PATH'te bulunamadı. "
            "https://claude.ai/code adresinden kurun."
        )
    p = Path(_CLAUDE_EXE)
    if not p.exists():
        return f"[Claude Code]: {_CLAUDE_EXE} dosyası mevcut değil."
    try:
        r = subprocess.run(
            [_CLAUDE_EXE, "--version"],
            capture_output=True, text=True, timeout=10
        )
        versiyon = (r.stdout or r.stderr or "").strip()
        return f"[Claude Code]: Hazır — {versiyon} | Yol: {_CLAUDE_EXE}"
    except Exception as e:
        return f"[Claude Code]: Erişim hatası — {e}"


# ── ToolRegistry Entegrasyonu ────────────────────────────────────────────

def motor_kaydet(motor):
    """Motor örneğine araçları kaydet (otomatik çağrılır)."""
    motor._plugin_arac_kaydet("CLAUDE_YARDIM",       claude_yardim,       "Claude Code'dan yardım iste")
    motor._plugin_arac_kaydet("CLAUDE_ANALIZ",       claude_analiz,       "Claude'a kod/metin analizi yaptır")
    motor._plugin_arac_kaydet("CLAUDE_KOD_YAZ",      claude_kod_yaz,      "Claude'a Python kodu yazdır")
    motor._plugin_arac_kaydet("CLAUDE_HATA_AYIKLA",  claude_hata_ayikla,  "Claude ile hata ayıkla")
    motor._plugin_arac_kaydet("CLAUDE_PLAN",         claude_plan,         "Claude'dan adım adım plan al")
    motor._plugin_arac_kaydet("CLAUDE_REVIZE",       claude_revize,       "Kodu Claude ile refactor et")
    motor._plugin_arac_kaydet("CLAUDE_DURUM",        claude_durum,        "Claude CLI durumunu kontrol et")


if __name__ == "__main__":
    print("=== Claude Code Tool Testi ===")
    print(claude_durum())
    print()
    print(claude_yardim("Python'da bir sayının asal olup olmadığını kontrol eden en kısa fonksiyonu yaz."))
