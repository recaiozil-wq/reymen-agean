# -*- coding: utf-8 -*-
"""
reflexion_motoru.py — Reflexion Pattern (Shinn et al. 2023).

ToolRegistry'e kayit icin:
    TOOL_META = {...}
    def run(...)
    def check_fn(...)

Kullanim (agent):
    REFLEXION_MOTORU(hedef="...", adim_gecmisi=[...], hata_mesaji="...")
        -> Hata/basarisizlik sonrasi yansima uretir ve kaydeder.
    REFLEXION_MOTORU(hedef="...", ders_al=True, adet=3)
        -> Benzer hatalardan ders getirir.
"""

import os
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Optional
import logging
logger = logging.getLogger(__name__)

TOOL_META = {
    "ad": "reflexion_motoru",
    "versiyon": "1.0.0",
    "aciklama": (
        "Reflexion Pattern (Shinn et al. 2023) uygulamasi. "
        "Basarisizliklardan sozel yansima uretir, hafizaya kaydeder "
        "ve benzer gorevlerde onceki dersleri getirir."
    ),
    "kategori": "ogrenme",
    "parametreler": {
        "hedef": {
            "tip": "str",
            "aciklama": "Basarisiz olan kullanici hedefi",
            "zorunlu": True,
        },
        "adim_gecmisi": {
            "tip": "list",
            "aciklama": "Gerceklestirilen adimlar listesi (yansima kaydi icin)",
            "zorunlu": False,
        },
        "hata_mesaji": {
            "tip": "str",
            "aciklama": "Son hata veya basarisizlik ozeti (yansima kaydi icin)",
            "zorunlu": False,
        },
        "ders_al": {
            "tip": "bool",
            "aciklama": "True ise benzer hatalardan ders getirir",
            "zorunlu": False,
        },
        "adet": {
            "tip": "int",
            "aciklama": "Getirilecek ders sayisi (varsayilan: 3)",
            "zorunlu": False,
        },
    },
    "ornek": (
        "REFLEXION_MOTORU(hedef='Webden haber cek', "
        "adim_gecmisi=['WEB_ARA(python news)'], "
        "hata_mesaji='[Hata]: timeout')  -> yansima kaydeder\\n"
        "REFLEXION_MOTORU(hedef='Internetten veri cek', "
        "ders_al=True, adet=3)  -> ders getirir"
    ),
}

ROOT = Path(__file__).parent.parent.resolve()
YANSIMA_LOG = ROOT / ".ReYMeN" / "reflexion_log.jsonl"
MAKS_YANSIMA = 200

# ── Prompt sablon ─────────────────────────────────────────────────────
_YANSIMA_SISTEM = """Sen deneyimli bir yapay zeka sistemi analisti ve ogretmenisin.
Sana basarisiz bir ajan gorevi sunulacak.
Gorevine gore NEDEN basarisiz oldugunu analiz et ve ne yapmasi gerektigini ac.

Yaniti TAM OLARAK su formatta ver (baska sey yazma):
NEDEN_BASARISIZ: [Tek cumle - kok neden]
KACINILACAK: [Tek cumle - tekrar yapilmamasi gereken eylem]
DAHA_IYI_YAKLASIM: [Tek cumle - bir dahaki seferde nasil yapilmali]
ANAHTAR_KELIMELER: [virgul,ile,ayrilmis,kelimeler]"""

_DERS_ENJEKSIYON_SABLON = """\n== REFLEXION: ONCEKI DERSLER ==
{dersler}
== /REFLEXION =="""

# ── Global state ─────────────────────────────────────────────────────
_reflexion_motoru = None
_reflexion_kilit = threading_lock = None


def _get_lock():
    """Thread lock tekil ornegini al."""
    global _reflexion_kilit
    if _reflexion_kilit is None:
        import threading
        _reflexion_kilit = threading.Lock()
    return _reflexion_kilit


def _get_or_create_motor():
    """Tekil ReflexionMotoru ornegini al/yarat."""
    global _reflexion_motoru
    with _get_lock():
        if _reflexion_motoru is None:
            _reflexion_motoru = _ReflexionMotoruDahili()
        return _reflexion_motoru


class _ReflexionMotoruDahili:
    """Basarisizliklardan sozel yansima ureten ve hafizaya kaydeden sinif (dahili)."""

    def __init__(self):
        self._log = YANSIMA_LOG
        self._log.parent.mkdir(parents=True, exist_ok=True)

    def yansima_kaydet(
        self,
        hedef: str,
        adim_gecmisi: list[str],
        hata_mesaji: str,
    ) -> Optional[dict]:
        """Basarisiz gorev icin yansima uret ve kaydet."""
        return self._kural_tabanli_yansima(hedef, adim_gecmisi, hata_mesaji)

    def ilgili_dersleri_al(self, hedef: str, adet: int = 3) -> str:
        """Benzer gecmis basarisizliklarin derslerini getir."""
        dersler = self._dosyadan_benzer_bul(hedef, adet)
        if not dersler:
            return ""

        satirlar = []
        for d in dersler:
            satirlar.append(
                f"- Hedef: {d.get('hedef', '?')[:60]}\n"
                f"  Neden: {d.get('neden_basarisiz', '?')}\n"
                f"  Cozum: {d.get('daha_iyi_yaklasim', '?')}"
            )

        return _DERS_ENJEKSIYON_SABLON.format(dersler="\n".join(satirlar))

    def _kural_tabanli_yansima(self, hedef: str, adimlar: list, hata: str) -> dict:
        """LLM olmadan kural tabanli yansima."""
        neden = "Bilinmeyen hata"
        cozum = "Farkli bir yaklasim dene"
        kacinilacak = "Ayni adimi tekrarlama"

        hata_lower = hata.lower()
        if "timeout" in hata_lower or "zaman asimi" in hata_lower:
            neden = "Islem zaman asimina ugradi"
            cozum = "Daha kisa sorgu veya islem parcalara bol"
            kacinilacak = "Uzun sure bekleyen ayni araci tekrar cagirma"
        elif "modul" in hata_lower or "import" in hata_lower:
            neden = "Gerekli Python modulu yuklu degil"
            cozum = "try/except ile modulu kontrol et ve alternatif kullan"
            kacinilacak = "Yuklu olmayan modulu import etme"
        elif "izin" in hata_lower or "permission" in hata_lower:
            neden = "Dosya/sistem izin hatasi"
            cozum = "Farkli dizin veya kullanici izinlerini kontrol et"
            kacinilacak = "Kisitlanmis alanlara yazma deneme"
        elif "baglanti" in hata_lower or "connection" in hata_lower:
            neden = "Network baglantisi kurulamadi"
            cozum = "Internet baglantisin varsa tekrar dene, yoksa cevrimici arac kullanma"
            kacinilacak = "Cevrimdisi ortamda ag gerektiren arac cagirma"

        anahtar = " ".join(hedef.lower().split()[:4])
        yansima = {
            "neden_basarisiz": neden,
            "kacinilacak": kacinilacak,
            "daha_iyi_yaklasim": cozum,
            "anahtar_kelimeler": anahtar,
            "hedef": hedef[:100],
            "zaman": datetime.now().isoformat(),
            "hata": hata[:200],
        }

        self._dosyaya_kaydet(yansima)
        return yansima

    def _dosyaya_kaydet(self, yansima: dict):
        """JSONL dosyasina satir olarak ekle; siniri asarsa en eskiyi sil."""
        try:
            satirlar = []
            if self._log.exists():
                satirlar = self._log.read_text(encoding="utf-8").splitlines()

            if len(satirlar) >= MAKS_YANSIMA:
                satirlar = satirlar[-(MAKS_YANSIMA - 1):]

            satirlar.append(json.dumps(yansima, ensure_ascii=False))
            self._log.write_text("\n".join(satirlar) + "\n", encoding="utf-8")
        except OSError as e:
            print(f"[Reflexion] Dosya yazma hatasi: {e}")

    def _dosyadan_benzer_bul(self, hedef: str, adet: int) -> list:
        """JSONL'den anahtar kelime ile benzer yansimalari bul."""
        if not self._log.exists():
            return []
        hedef_kelimeler = set(hedef.lower().split())
        sonuclar = []
        try:
            for satir in self._log.read_text(encoding="utf-8").splitlines():
                if not satir.strip():
                    continue
                try:
                    d = json.loads(satir)
                except json.JSONDecodeError:
                    continue
                anahtar = set((d.get("anahtar_kelimeler", "")).replace(",", " ").lower().split())
                eski_hedef = set(d.get("hedef", "").lower().split())
                toplam = anahtar | eski_hedef
                eslesme = len(hedef_kelimeler & toplam)
                if eslesme > 0:
                    sonuclar.append((eslesme, d))
            sonuclar.sort(key=lambda x: x[0], reverse=True)
            return [d for _, d in sonuclar[:adet]]
        except OSError:
            return []


def run(
    hedef: str = "",
    adim_gecmisi: list = None,
    hata_mesaji: str = "",
    ders_al: bool = False,
    adet: int = 3,
) -> str:
    """Reflexion motorunu calistir.

    Iki kullanim mode:
    1. Yansima kaydet: hedef + adim_gecmisi + hata_mesaji verilir.
    2. Ders getir: hedef + ders_al=True verilir.

    Args:
        hedef: Basarisiz olan kullanici hedefi.
        adim_gecmisi: Gerceklestirilen adimlar listesi.
        hata_mesaji: Son hata veya basarisizlik ozeti.
        ders_al: True ise benzer hatalardan ders getirir.
        adet: Getirilecek ders sayisi.

    Returns:
        str: Yansima sonucu veya ders metni.
    """
    if not hedef:
        return (
            "[REFLEXION] Kullanim: REFLEXION_MOTORU(hedef='...', ...) "
            "ile yansima kaydi veya REFLEXION_MOTORU(hedef='...', ders_al=True) "
            "ile ders getirme."
        )

    motor = _get_or_create_motor()

    # Ders getirme modu
    if ders_al:
        dersler = motor.ilgili_dersleri_al(hedef, adet=adet)
        if dersler:
            return dersler
        return f"[REFLEXION] '{hedef}' icin benzer ders bulunamadi."

    # Yansima kaydetme modu
    if adim_gecmisi is None:
        adim_gecmisi = []
    if not hata_mesaji:
        return "[REFLEXION] Yansima kaydi icin 'hata_mesaji' parametresi zorunludur."

    yansima = motor.yansima_kaydet(hedef, adim_gecmisi, hata_mesaji)

    if not yansima:
        return "[REFLEXION] Yansima olusturulamadi."

    return (
        f"[REFLEXION] Yansima kaydedildi:\n"
        f"  Neden: {yansima.get('neden_basarisiz', '?')}\n"
        f"  Kacinilacak: {yansima.get('kacinilacak', '?')}\n"
        f"  Daha iyi yaklasim: {yansima.get('daha_iyi_yaklasim', '?')}"
    )


def check_fn() -> bool:
    """Kullanilabilirlik kontrolu: her zaman kullanilabilir."""
    return True
