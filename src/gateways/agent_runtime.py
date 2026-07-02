# -*- coding: utf-8 -*-
"""
agent_runtime.py — ReYMeN Ajan Calisma Zamani (Agent Runtime).

Icerik:
  AgentRuntime    — Ajan yasamdongusunu yoneten sinif (init, calistir, durdur)
  RuntimeHelpers  — Yardimci metodlar (hedef analizi, tur yonetimi, hata siniflandirma)
  BackgroundReview— Arka planda hafiza/beceri gozden gecirme (daemon thread)

Kullanim:
    from agent_runtime import AgentRuntime
    rt = AgentRuntime(config)
    rt.calistir("Hedef")
"""
import json
import logging
import os
import threading
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

logger = logging.getLogger("ReYMeN.runtime")

ROOT = Path(__file__).parent.resolve()


# ── Hata Siniflandirici ───────────────────────────────────────────────────────

class HataSiniflandirici:
    """Gozlem stringlerini hata tiplerine gore siniflandirir."""

    KATEGORILER = {
        "ag":         r"(ConnectionError|Timeout|HTTPError|network|socket)",
        "dosya":      r"(FileNotFoundError|PermissionError|IsADirectory)",
        "modul":      r"(ModuleNotFoundError|ImportError|No module)",
        "python":     r"(SyntaxError|IndentationError|NameError|TypeError)",
        "izin":       r"(PermissionError|Access.denied|Unauthorized)",
        "zaman_asimi":r"(timeout|Timeout|timed out)",
    }

    @classmethod
    def siniflandir(cls, gozlem: str) -> str:
        import re
        for kategori, desen in cls.KATEGORILER.items():
            if re.search(desen, gozlem, re.IGNORECASE):
                return kategori
        if "[Hata]" in gozlem or "Error" in gozlem:
            return "genel"
        return "basarili"

    @classmethod
    def kurtarma_onerisi(cls, kategori: str) -> str:
        oneriler = {
            "ag":         "Ag baglantisini kontrol et veya WEB_ARA yerine DOSYA_OKU dene.",
            "dosya":      "Dosya yolunu ve izinleri kontrol et. KOMUT_CALISTIR ile ls/dir dene.",
            "modul":      "pip install ile eksik modulu yukle.",
            "python":     "Kodu once PYTHON_CALISTIR ile test et.",
            "izin":       "Yonetici olarak calistir veya farkli yol dene.",
            "zaman_asimi":"Islemi daha kucuk parcalara bol.",
            "genel":      "Farkli bir yaklasim dene.",
        }
        return oneriler.get(kategori, "Devam et.")


# ── Runtime Helpers ──────────────────────────────────────────────────────────

class RuntimeHelpers:
    """Ajan dongusunu destekleyen yardimci metodlar."""

    @staticmethod
    def hedef_analiz_et(hedef: str) -> dict:
        """Hedefin karmasikligini ve turunu tahmin et (1-5).

        Kategori bazli hesaplama:
          1 = selamlasma/sosyal/basit soru
          2 = tek kategorili basit islem
          3 = iki kategorili veya cok adimli islem
          4 = 3+ kategori veya toplu gorev (swarm esigi)
          5 = toplu + islem (swarm)
        """
        hedef_lower = hedef.lower().strip()

        # ── 0. Selamlasma/sosyal → direkt 1 ─────────────────────────
        _selam = any(k in hedef_lower for k in [
            "merhaba", "selam", "naber", "nasılsın", "nasilsin",
            "iyi misin", "teşekkür", "tesekkur", "sağol", "sagol",
            "günaydın", "gunaydin", "iyi günler", "iyi gunler",
            "iyi akşamlar", "iyi aksamlar", "iyi geceler",
            "ne yapıyorsun", "ne yapiyorsun", "napıyorsun", "napiyorsun",
            "kolay gelsin", "hayırlı", "hayirli",
        ])
        if _selam:
            _ek_islem = any(k in hedef_lower for k in [
                "yap", "ara", "oku", "yaz", "sil", "bul",
                "calistir", "çalıştır", "indir", "yukle", "yükle",
                "kur", "gönder", "gonder", "tara", "kontrol",
                "düzelt", "duzelt", "temizle", "düzenle", "duzenle",
                "raporla", "analiz", "incele", "güncelle", "guncelle",
                "aç", "ac", "kapat", "kes",
            ])
            if not _ek_islem:
                return {
                    "hedef_tur": "selam",
                    "karmasiklik": 1,
                    "onerilen_max_tur": 6,
                    "ipuclari": [],
                }

        # ── 1. Toplu gorev tespiti ─────────────────────────────────
        _toplu = any(k in hedef_lower for k in [
            "hepsini", "hepsin", "hepsi",
            "tümünü", "tümü", "tüm", "tumu", "tumunu",
            "bütün", "butun", "toplu",
        ])
        _islem = any(k in hedef_lower for k in [
            "kontrol", "gider", "düzelt", "duzelt", "onar", "temizle",
            "tara", "düzenle", "duzenle", "yap", "calistir", "çalıştır",
            "incele", "dönüştür", "donustur", "güncelle", "guncelle",
        ])

        # ── 2. Cok adimli gorev tespiti ────────────────────────────
        _cok_adim_baglac = any(k in hedef_lower for k in [
            "ve", "sonra", "ardindan", "ardından", "daha sonra",
            "once", "önce", "daha önce", "daha once",
        ])
        _cok_adim_virgul = hedef_lower.count(",") >= 2
        _cok_adim = _cok_adim_baglac or _cok_adim_virgul

        # ── 3. Kategori bazli ipucu tespiti ─────────────────────────
        kategoriler = {
            "dosya_islemi": ["dosya", "klasör", "klasor", "dizin", "belge",
                            "uzanti"],
            "web_islemi":   ["web", "arama", "internet", "url", "site", "sayfa",
                            "link", "indir", "yukle", "yükle", "gönder", "gonder"],
            "kod_islemi":   ["kod", "python", "script", "calistir", "çalıştır",
                            "analiz", "derle", "debug", "test"],
            "yazma_islem":  ["yaz", "oluştur", "olustur", "kaydet", "ekle",
                            "güncelle", "guncelle", "sil", "düzenle", "duzenle",
                            "temizle", "dönüştür", "donustur", "düzelt", "duzelt",
                            "onar"],
            "hafiza_islemi":["hatirla", "hatırla", "unutma", "not"],
            "sistem_islemi":["komut", "terminal", "powershell", "sistem",
                            "servis", "port", "ağ", "ag", "islem", "işlem",
                            "durdur"],
            "arama_islem":  ["ara", "bul", "tara", "sorgula", "keşfet", "kesfet",
                            "listele", "getir", "incele"],
            "guvenlik":     ["güvenlik", "guvenlik", "şifre", "sifre", "izin",
                            "yetki", "erişim", "erisim"],
            "github_islem": ["git", "github", "repo", "commit", "push", "pull",
                            "clone", "branch", "merge"],
        }

        # Ekstra puan veren kelimeler (kategori disi kapsam artirici)
        _ekstra_kelimeler = ["raporla", "özet", "ozet", "karşılaştır", "karsilastir",
                            "birleştir", "birlestir", "görsel", "gorsel", "grafik"]

        aktif = []
        _bulunan_kategori = 0
        for kat_adi, kw_list in kategoriler.items():
            if any(kw in hedef_lower for kw in kw_list):
                aktif.append(kat_adi)
                _bulunan_kategori += 1

        if _toplu and _islem:
            return {
                "hedef_tur": aktif[0] if aktif else "toplu",
                "karmasiklik": 5,
                "onerilen_max_tur": 30,
                "ipuclari": aktif,
            }
        if _toplu:
            return {
                "hedef_tur": aktif[0] if aktif else "toplu",
                "karmasiklik": 4,
                "onerilen_max_tur": 24,
                "ipuclari": aktif,
            }

        # ── 4. Skor hesaplama ──────────────────────────────────────
        skor = _bulunan_kategori
        if _cok_adim:
            skor += 1

        # Ekstra kelime puani
        for k in _ekstra_kelimeler:
            if k in hedef_lower:
                skor += 1
                break

        karmasiklik = max(1, min(skor, 5))
        return {
            "hedef_tur": aktif[0] if aktif else "genel",
            "karmasiklik": karmasiklik,
            "onerilen_max_tur": karmasiklik * 6,
            "ipuclari": aktif,
        }

    @staticmethod
    def tur_ilerleme_goster(tur: int, max_tur: int, arac: str = ""):
        """Konsola ilerleme cubugu goster."""
        dolu = int((tur / max_tur) * 20)
        bos = 20 - dolu
        cubuk = "█" * dolu + "░" * bos
        arac_k = f" [{arac}]" if arac else ""
        print(f"\r  [{cubuk}] {tur}/{max_tur}{arac_k}", end="", flush=True)

    @staticmethod
    def gecmis_ozet(adim_gecmisi: list[str], limit: int = 5) -> str:
        if not adim_gecmisi:
            return "(henuz adim atilmadi)"
        son = adim_gecmisi[-limit:]
        return "\n".join(f"  {i+1}. {a}" for i, a in enumerate(son))


# ── Background Review (Arka Plan Gozden Gecirme) ─────────────────────────────

class BackgroundReview:
    """
    Gorev bittikten sonra arka planda calisir:
      1. Konusmayi analiz et
      2. Hafizaya yazilmaya deger bir sey var mi?
      3. Yeni beceri karti cikarilabilir mi?

    ReYMeN agent'in background_review'indan ilham alindi.
    Ana donguya dokunmaz — sadece storage'a yazar.
    """

    HAFIZA_GOZDEN_GECIRME = (
        "Yukaridaki konusmayi gozden gecir.\n"
        "Kullanicinin tercihleri, is tarzi veya proje hakkinda "
        "SONU KONUSMALARDA da isine yarayacak bir bilgi var mi?\n"
        "Varsa kisaca yaz. Yoksa 'Kaydedilecek bir sey yok.' de."
    )

    BECERI_GOZDEN_GECIRME = (
        "Yukaridaki konusmayi gozden gecir.\n"
        "Tekrar kullanilabilecek bir strateji, yaklasim veya cozum patti var mi?\n"
        "Varsa: BECERI_ADI: ..., ACIKLAMA: ..., ADIMLAR: ... formatinda yaz.\n"
        "Yoksa 'Beceri yok.' de."
    )

    def __init__(self, provider=None, learning_loop=None, session=None):
        self.provider = provider
        self.learning_loop = learning_loop
        self.session = session

    def spawn(self, hedef: str, mesajlar: list, adim_gecmisi: list):
        """Arka plan thread'i baslat."""
        if not self.provider:
            return
        t = threading.Thread(
            target=self._calistir,
            args=(hedef, list(mesajlar), list(adim_gecmisi)),
            daemon=True,
        )
        t.start()

    def _calistir(self, hedef: str, mesajlar: list, adim_gecmisi: list):
        try:
            time.sleep(1)  # Ana dongunun bitmesini bekle
            self._hafiza_gozden_gecir(hedef, mesajlar)
            self._beceri_gozden_gecir(hedef, adim_gecmisi)
        except Exception as e:
            logger.debug(f"[BackgroundReview] Hata: {e}")

    def _hafiza_gozden_gecir(self, hedef: str, mesajlar: list):
        parcalar = [f"Hedef: {hedef}"]
        for m in mesajlar[-20:]:
            rol = m.get("role", "?")
            icerik = m.get("content", "")[:200]
            parcalar.append(f"[{rol}]: {icerik}")
        gecmis = "\n".join(parcalar)
        try:
            cevap = self.provider.uret(
                self.HAFIZA_GOZDEN_GECIRME,
                [{"role": "user", "content": gecmis}],
            )
            if "Kaydedilecek bir sey yok" not in cevap and len(cevap) > 20:
                self._hafizaya_kaydet(hedef, cevap)
        except Exception as e:
            logger.debug(f"[BackgroundReview.hafiza] {e}")

    def _beceri_gozden_gecir(self, hedef: str, adim_gecmisi: list):
        if not self.learning_loop or not adim_gecmisi:
            return
        gecmis = f"Hedef: {hedef}\n\nAdimlar:\n" + "\n".join(adim_gecmisi[-15:])
        try:
            cevap = self.provider.uret(
                self.BECERI_GOZDEN_GECIRME,
                [{"role": "user", "content": gecmis}],
            )
            if "Beceri yok" in cevap:
                return
            # BECERI_ADI: ..., ACIKLAMA: ..., ADIMLAR: ... parse et
            import re
            ad = re.search(r"BECERI_ADI:\s*(.+)", cevap)
            acik = re.search(r"ACIKLAMA:\s*(.+)", cevap)
            adimlar = re.search(r"ADIMLAR:\s*(.+)", cevap, re.DOTALL)
            if ad and acik:
                self.learning_loop.beceri_kristallestir(
                    ad.group(1).strip()[:40],
                    acik.group(1).strip(),
                    adimlar.group(1).strip() if adimlar else "\n".join(adim_gecmisi),
                )
        except Exception as e:
            logger.debug(f"[BackgroundReview.beceri] {e}")

    def _hafizaya_kaydet(self, hedef: str, icerik: str):
        """MEMORY.md'ye ekle."""
        memory_yolu = ROOT / ".ReYMeN" / "MEMORY.md"
        try:
            mevcut = memory_yolu.read_text(encoding="utf-8") if memory_yolu.exists() else ""
            zaman = datetime.now().strftime("%Y-%m-%d")
            ek = f"\n\n## [{zaman}] {hedef[:50]}\n{icerik}\n"
            memory_yolu.write_text(mevcut + ek, encoding="utf-8")
            logger.debug(f"[BackgroundReview] Hafizaya kaydedildi: {hedef[:30]}")
        except Exception as e:
            logger.debug(f"[BackgroundReview.hafiza.kaydet] {e}")


# ── Agent Runtime ─────────────────────────────────────────────────────────────

class AgentRuntime:
    """
    ReYMeN ajan calisma zamani.
    main.py'deki AIAgentOrchestrator'a ince bir kabuk saglar.
    Dogrudan kullanilabilir veya entegrasyon noktasi olarak kullanilir.
    """

    VERSION = "1.0.0"

    def __init__(self, config: dict):
        self.config = config
        self._calisma_id: Optional[str] = None
        self._baslangic: Optional[float] = None
        self._durum = "bosta"
        self._kilit = threading.Lock()
        self._agent = None
        self._background = None

    def _agent_olustur(self):
        from reymen.sistem.main import AIAgentOrchestrator
        max_tur = int(self.config.get("max_tur", 15))
        onay = self.config.get("onay_iste", False)
        mod = self.config.get("backend_mode", "local")
        self._agent = AIAgentOrchestrator(
            config=self.config, backend_mode=mod,
            max_tur=max_tur, onay_iste=onay,
        )
        self._background = BackgroundReview(
            provider=self._agent.provider,
            learning_loop=self._agent.learning,
            session=self._agent.session,
        )

    def calistir(self, hedef: str) -> dict:
        """Hedefi calistir ve sonuc sozlugu dondur."""
        with self._kilit:
            if self._durum == "calisiyor":
                return {"hata": "Ajan zaten calisiyor", "calisma_id": self._calisma_id}
            self._calisma_id = uuid.uuid4().hex[:8]
            self._durum = "calisiyor"
            self._baslangic = time.time()

        analiz = RuntimeHelpers.hedef_analiz_et(hedef)
        logger.info(f"[Runtime] Calisma {self._calisma_id}: {hedef[:60]} "
                    f"(karmasiklik:{analiz['karmasiklik']})")

        try:
            if not self._agent:
                self._agent_olustur()

            # Karmasikliga gore max_tur ayarla
            if analiz["karmasiklik"] > 3:
                self._agent.max_tur = max(self._agent.max_tur,
                                          analiz["onerilen_max_tur"])

            sonuc = self._agent.run_conversation(hedef)
            sure = round(time.time() - self._baslangic, 2)

            # Arka plan gozden gecirme
            if self._background:
                self._background.spawn(
                    hedef,
                    self._agent.motor.config.get("_son_mesajlar", []),
                    [],
                )

            return {
                "calisma_id": self._calisma_id,
                "hedef": hedef,
                "sonuc": sonuc,
                "sure": sure,
                "basarili": sonuc is not None,
                "analiz": analiz,
            }
        except Exception as e:
            logger.error(f"[Runtime] Calisma hatasi: {e}")
            return {
                "calisma_id": self._calisma_id,
                "hedef": hedef,
                "sonuc": None,
                "hata": str(e),
                "basarili": False,
            }
        finally:
            with self._kilit:
                self._durum = "bosta"

    def durum(self) -> dict:
        return {
            "durum": self._durum,
            "calisma_id": self._calisma_id,
            "sure": round(time.time() - self._baslangic, 1) if self._baslangic else 0,
            "versiyon": self.VERSION,
        }

    def sifirla(self):
        """Agent'i ve compressor'u sifirla (yeni oturum)."""
        if self._agent:
            self._agent.compressor.sifirla()
            self._agent.planlayici.sifirla()
        self._calisma_id = None
        self._baslangic = None


if __name__ == "__main__":
    import sys
    from pathlib import Path
    sys.path.insert(0, str(ROOT))
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env", override=True)

    from reymen.sistem.main import CONFIG
    rt = AgentRuntime(CONFIG)
    print(f"[Runtime] Durum: {rt.durum()}")
    print(f"[Hedef Analizi]: {RuntimeHelpers.hedef_analiz_et('Python dosyasi olustur ve test et')}")
