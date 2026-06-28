# -*- coding: utf-8 -*-
"""
plugins/memory/oturum_hafiza/__init__.py — Oturum Hafızası Plugin'i.

ReYMeN Memory Provider Plugin standardına uygun ReYMeN implementasyonu.
Her oturumu JSON olarak diske yazar; oturumlar arası özet çeker.

Özellikler:
  - Her oturum ayrı bir .ReYMeN/oturumlar/<id>.json dosyasına kaydedilir
  - on_session_end(): LLM ile oturum özeti oluşturur (opsiyonel)
  - prefetch(): son N oturumun başlarını bağlama ekler
  - Araçlar: OTURUM_LISTELE, OTURUM_OKU, OTURUM_OZET
  - Harici bağımlılık yok — sadece stdlib JSON
"""


__all__ = ['AbstraktHafizaSaglayici', 'Any', 'Dict', 'HafizaPluginKayit', 'List', 'Optional', 'OturumHafizasi', 'Path', 'ad', 'arac_cagri_isle', 'arac_sema_al', 'baslat', 'kapat', 'kaydet', 'konfig_sema_al', 'musait_mi', 'onceden_getir', 'oturum_bitti', 'sistem_prompt_bloku']
import json
import logging
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from memory_provider import AbstraktHafizaSaglayici, HafizaPluginKayit

logger = logging.getLogger(__name__)

PLUGIN_ADI = "oturum_hafiza"
PLUGIN_ACIKLAMA = "JSON tabanlı oturum hafızası — her konuşma ayrı dosyaya kaydedilir"

OTURUM_BASINA_MAKS_MESAJ = 500
PREFETCH_OTURUM_SAYISI = 3
OZET_MAKS_KARAKTER = 800


class OturumHafizasi(AbstraktHafizaSaglayici):
    """
    Her konuşma oturumunu ayrı JSON dosyasına kaydeden hafıza.
    prefetch() son oturumların özetini sistem bağlamına ekler.
    """

    def __init__(self):
        self._oturum_id: str = "varsayilan"
        self._oturum_dizin: Optional[Path] = None
        self._aktif_mesajlar: List[Dict[str, Any]] = []
        self._ozet_saglayici = None  # LLM provider referansı (opsiyonel)

    @property
    def ad(self) -> str:
        return PLUGIN_ADI

    def musait_mi(self) -> bool:
        # JSON + stdlib — her zaman mevcut
        return True

    def baslat(self, oturum_id: str, **kwargs) -> None:
        self._oturum_id = oturum_id
        reymen_dizin = Path(
            kwargs.get("reymen_dizin",
                       Path(__file__).parent.parent.parent.parent / ".ReYMeN")
        )
        self._oturum_dizin = reymen_dizin / "oturumlar"
        self._oturum_dizin.mkdir(parents=True, exist_ok=True)
        self._ozet_saglayici = kwargs.get("ozet_saglayici", None)
        self._aktif_mesajlar = []
        logger.info(f"[oturum_hafiza] Baslatildi — {self._oturum_dizin / oturum_id}")

    def _oturum_dosyasi(self, oturum_id: Optional[str] = None) -> Path:
        oid = oturum_id or self._oturum_id
        return self._oturum_dizin / f"{oid}.json"

    # ── Araç şemaları ──────────────────────────────────────────────────────

    def arac_sema_al(self) -> List[Dict[str, Any]]:
        return [
            {
                "ad": "OTURUM_LISTELE",
                "aciklama": "Kaydedilmiş oturumları listele",
                "parametreler": {
                    "limit": {"tur": "int", "varsayilan": 10},
                },
            },
            {
                "ad": "OTURUM_OKU",
                "aciklama": "Belirli bir oturumun içeriğini oku",
                "parametreler": {
                    "oturum_id": {"tur": "str", "aciklama": "Oturum kimliği"},
                    "son_n": {"tur": "int", "varsayilan": 20},
                },
            },
            {
                "ad": "OTURUM_OZET",
                "aciklama": "Belirli bir oturumun özetini getir",
                "parametreler": {
                    "oturum_id": {"tur": "str", "aciklama": "Oturum kimliği (boş = aktif)"},
                },
            },
        ]

    def arac_cagri_isle(self, arac_adi: str, args: Dict[str, Any], **kwargs) -> str:
        if arac_adi == "OTURUM_LISTELE":
            return self._listele(int(args.get("limit", 10)))
        if arac_adi == "OTURUM_OKU":
            return self._oku(args.get("oturum_id", self._oturum_id), int(args.get("son_n", 20)))
        if arac_adi == "OTURUM_OZET":
            oid = args.get("oturum_id", "") or self._oturum_id
            return self._ozet_oku(oid)
        return f"Bilinmeyen araç: {arac_adi}"

    # ── Lifecycle hooks ────────────────────────────────────────────────────

    def sistem_prompt_bloku(self) -> str:
        return (
            f"[Hafıza: Oturum Hafızası aktif — Oturum: {self._oturum_id}]\n"
            "Geçmiş oturumları görmek için OTURUM_LISTELE, okumak için OTURUM_OKU kullan."
        )

    def onceden_getir(self, sorgu: str) -> str:
        """Son PREFETCH_OTURUM_SAYISI oturumun son mesajını bağlama ekle."""
        if not self._oturum_dizin:
            return ""
        dosyalar = sorted(
            self._oturum_dizin.glob("*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )[:PREFETCH_OTURUM_SAYISI]

        satirlar = []
        for dosya in dosyalar:
            if dosya.stem == self._oturum_id:
                continue
            try:
                with open(dosya, "r", encoding="utf-8") as f:
                    veri = json.load(f)
                ozet = veri.get("ozet", "")
                son_mesaj = ""
                mesajlar = veri.get("mesajlar", [])
                if mesajlar:
                    son_mesaj = mesajlar[-1].get("content", "")[:200]
                if ozet:
                    satirlar.append(f"[{dosya.stem}] ÖZET: {ozet[:300]}")
                elif son_mesaj:
                    satirlar.append(f"[{dosya.stem}] SON: {son_mesaj}")
            except Exception:
                logger.warning("[fix_01_sessiz_except] Exception")

        if not satirlar:
            return ""
        return "Önceki oturumlar:\n" + "\n".join(satirlar)

    def _tur_senkronize_impl(self, mesajlar: List[Dict[str, Any]]) -> None:
        """Aktif oturumun mesajlarını JSON dosyasına ekle (arka plan)."""
        if not self._oturum_dizin or not mesajlar:
            return
        dosya = self._oturum_dosyasi()
        try:
            # Mevcut veriyi yükle
            veri: Dict[str, Any] = {"oturum_id": self._oturum_id, "mesajlar": [], "ozet": ""}
            if dosya.exists():
                with open(dosya, "r", encoding="utf-8") as f:
                    veri = json.load(f)

            # Yeni mesajları ekle (tekrar engelleyici)
            mevcut_sayı = len(veri.get("mesajlar", []))
            yeni = mesajlar[mevcut_sayı:]
            veri.setdefault("mesajlar", []).extend(yeni)
            veri["son_guncelleme"] = time.time()

            # Sınır aşımı — en eski mesajları at
            if len(veri["mesajlar"]) > OTURUM_BASINA_MAKS_MESAJ:
                veri["mesajlar"] = veri["mesajlar"][-OTURUM_BASINA_MAKS_MESAJ:]

            with open(dosya, "w", encoding="utf-8") as f:
                json.dump(veri, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.debug(f"[oturum_hafiza] tur_senkronize_impl hata: {e}")

    def oturum_bitti(self) -> None:
        """Oturum kapanırken özet oluştur (LLM varsa)."""
        dosya = self._oturum_dosyasi()
        if not dosya.exists():
            return
        if self._ozet_saglayici:
            try:
                with open(dosya, "r", encoding="utf-8") as f:
                    veri = json.load(f)
                mesajlar = veri.get("mesajlar", [])
                if len(mesajlar) < 4:
                    return
                birlesik = " ".join(
                    m.get("content", "")[:100]
                    for m in mesajlar[-10:]
                    if isinstance(m.get("content"), str)
                )
                ozet = self._ozet_saglayici.uret(
                    f"Bu konuşmayı {OZET_MAKS_KARAKTER} karakterde özetle:\n{birlesik}",
                    model=None,
                )
                veri["ozet"] = ozet[:OZET_MAKS_KARAKTER]
                with open(dosya, "w", encoding="utf-8") as f:
                    json.dump(veri, f, ensure_ascii=False, indent=2)
                logger.debug(f"[oturum_hafiza] Oturum özeti kaydedildi: {self._oturum_id}")
            except Exception as e:
                logger.debug(f"[oturum_hafiza] Ozet olusturulamadi: {e}")

    def kapat(self) -> None:
        self._aktif_mesajlar = []
        logger.debug("[oturum_hafiza] Kapatildi.")

    # ── Konfigurasyon ───────────────────────────────────────────────────────

    def konfig_sema_al(self) -> List[Dict[str, Any]]:
        return [
            {
                "key": "ozet_etkin",
                "label": "Oturum bitişinde LLM özeti oluştur",
                "secret": False,
                "required": False,
                "choices": ["evet", "hayir"],
                "default": "hayir",
            },
            {
                "key": "maks_oturum",
                "label": "Maksimum kayıtlı oturum sayısı",
                "secret": False,
                "required": False,
                "default": "1000",
            },
        ]

    # ── İç metodlar ────────────────────────────────────────────────────────

    def _listele(self, limit: int = 10) -> str:
        if not self._oturum_dizin:
            return "Oturum dizini başlatılmadı."
        dosyalar = sorted(
            self._oturum_dizin.glob("*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )[:limit]
        if not dosyalar:
            return "Kayıtlı oturum yok."
        satirlar = []
        for d in dosyalar:
            aktif = " [AKTİF]" if d.stem == self._oturum_id else ""
            try:
                boyut = d.stat().st_size
                satirlar.append(f"{d.stem}{aktif} ({boyut} byte)")
            except Exception:
                satirlar.append(d.stem + aktif)
        return "\n".join(satirlar)

    def _oku(self, oturum_id: str, son_n: int = 20) -> str:
        dosya = self._oturum_dosyasi(oturum_id)
        if not dosya.exists():
            return f"Oturum bulunamadı: {oturum_id}"
        try:
            with open(dosya, "r", encoding="utf-8") as f:
                veri = json.load(f)
            mesajlar = veri.get("mesajlar", [])[-son_n:]
            if not mesajlar:
                return "Oturum boş."
            return "\n".join(
                f"[{m.get('role','?')}] {str(m.get('content',''))[:300]}"
                for m in mesajlar
            )
        except Exception as e:
            return f"Okuma hatası: {e}"

    def _ozet_oku(self, oturum_id: str) -> str:
        dosya = self._oturum_dosyasi(oturum_id)
        if not dosya.exists():
            return f"Oturum bulunamadı: {oturum_id}"
        try:
            with open(dosya, "r", encoding="utf-8") as f:
                veri = json.load(f)
            ozet = veri.get("ozet", "")
            mesaj_sayisi = len(veri.get("mesajlar", []))
            if ozet:
                return f"Oturum {oturum_id} ({mesaj_sayisi} mesaj):\n{ozet}"
            return f"Oturum {oturum_id} — özet yok ({mesaj_sayisi} mesaj kaydedildi)."
        except Exception as e:
            return f"Özet okuma hatası: {e}"


# ── Plugin kayıt giriş noktası ────────────────────────────────────────────

def kaydet(ctx: HafizaPluginKayit) -> None:
    """ReYMeN Memory Provider Plugin standardı — kayıt giriş noktası."""
    ctx.hafiza_saglayici_kaydet(OturumHafizasi())


if __name__ == "__main__":
    from memory_provider import HafizaPluginKayit
    ctx = HafizaPluginKayit()
    kaydet(ctx)
    ctx.aktif_saglayici_sec("oturum_hafiza", "test-ses-001")
    s = ctx.aktif_al()
    if s:
        print(s.sistem_prompt_bloku())
        s.tur_senkronize([
            {"role": "user", "content": "Merhaba, nasılsın?"},
            {"role": "assistant", "content": "İyiyim, teşekkürler!"},
        ])
        import time; time.sleep(0.2)
        print(s.arac_cagri_isle("OTURUM_LISTELE", {"limit": 5}))
        print(s.arac_cagri_isle("OTURUM_OKU", {"oturum_id": "test-ses-001"}))
