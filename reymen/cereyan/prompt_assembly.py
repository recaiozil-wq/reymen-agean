# -*- coding: utf-8 -*-
"""
prompt_assembly.py — Prompt birlestirme ve yonetim modulu.

Template-based assembly ile prompt parcalarini birlestirir.
insa_et() ile SOUL.md + MEMORY.md + beceri baglami + ReAct kurallari
tek sistem promptuna donusturulur.
"""

import os
from pathlib import Path
import logging
logger = logging.getLogger(__name__)


class PromptAssembly:
    """Prompt parcalarini birlestirir ve eksiksiz sistem promptu olusturur."""

    def __init__(self, depo_yolu=None, bounded_memory=None, learning_loop=None, **kwargs):
        self._parcalar = {}
        self._sablonlar = {}
        self._bounded_memory = bounded_memory
        self._learning_loop = learning_loop

        if depo_yolu:
            self._depo_yolu = Path(depo_yolu)
        else:
            self._depo_yolu = Path.cwd() / ".ReYMeN" / "prompts"
        try:
            self._depo_yolu.mkdir(parents=True, exist_ok=True)
        except OSError as _prompt_a_e28:
            print(f"[UYARI] prompt_assembly.py:29 - {_prompt_a_e28}")

        # Context files yoneticisi
        self._context_loader = None
        try:
            from agent.context_files import ContextFileLoader
            self._context_loader = ContextFileLoader()
        except ImportError as _prompt_a_e36:
            print(f"[UYARI] prompt_assembly.py:37 - {_prompt_a_e36}")

    # ── Ana metot: eksiksiz sistem promptu ─────────────────────────────

    def insa_et(self, hedef, son_gozlem="", tur=1, toplam_tur=15,
                ic_gozlem_modu=False):
        """SOUL + MEMORY + beceri + ReAct kurallarindan sistem promptu olustur.

        Args:
            hedef:          Kullanicinin ana hedefi
            son_gozlem:     Onceki turdan gelen gozlem metni
            tur:            Mevcut tur numarasi
            toplam_tur:     Maksimum tur sayisi
            ic_gozlem_modu: True ise oz-degerlendirme talimatini ekle

        Returns:
            str: Birlestirilmis sistem promptu
        """
        parcalar = []

        # 1. Kimlik katmani (SOUL.md)
        soul = self._soul_oku()
        if soul:
            parcalar.append(f"## KIMLIK\n{soul}")

        # 2. Kalici hafiza (MEMORY.md)
        hafiza = self._memory_oku()
        if hafiza:
            parcalar.append(f"## KALICI HAFIZA\n{hafiza}")

        # 3. Beceri baglami (ClosedLearningLoop)
        beceri = self._beceri_baglamini_al(hedef)
        if beceri:
            parcalar.append(beceri)

        # 3.5. Proje baglam dosyalari (AGENTS.md, CLAUDE.md, .cursorrules)
        if self._context_loader:
            ctx = self._context_loader.kok_yukle()
            if ctx:
                parcalar.append(f"## PROJE BAGLAMI\n{ctx}")

        # 4. ReAct sistem talimati
        try:
            from sistem_talimati import sistem_talimatini_insa_et
            # Eski parametreleri ek_bilgi'ye donustur
            ek_bilgi_parcalari = []
            if tur and toplam_tur:
                ek_bilgi_parcalari.append(f"Tur {tur}/{toplam_tur}")
            if ic_gozlem_modu:
                ek_bilgi_parcalari.append("Ic gozlem modu aktif —"
                                          " onceki adimlari degerlendir, gerekiyorsa strateji degistir.")
            ek_bilgi = " | ".join(ek_bilgi_parcalari) if ek_bilgi_parcalari else ""

            react = sistem_talimatini_insa_et(
                hedef,
                son_gozlem=son_gozlem,
                ek_bilgi=ek_bilgi,
            )
        except ImportError:
            react = self._varsayilan_react_talimati(hedef, son_gozlem, tur, toplam_tur)
        parcalar.append(react)

        return "\n\n".join(p for p in parcalar if p)

    # ── Dosya okuma yardimcilari ───────────────────────────────────────

    def _soul_oku(self) -> str:
        """SOUL.md kimlik dosyasini oku."""
        for aday in [
            Path(".hermes") / "SOUL.md",
            Path(".ReYMeN") / "SOUL.md",
            Path("SOUL.md"),
        ]:
            try:
                if aday.exists():
                    return aday.read_text(encoding="utf-8").strip()
            except OSError as _prompt_a_e113:
                print(f"[UYARI] prompt_assembly.py:114 - {_prompt_a_e113}")
        return ""

    def _memory_oku(self) -> str:
        """MEMORY.md kalici bellek dosyasini oku (son 2000 karakter)."""
        ReYMeN_home = Path(os.environ.get("ReYMeN_HOME", ".ReYMeN"))
        adaylar = [
            ReYMeN_home / "memories" / "MEMORY.md",
            Path(".hermes") / "memories" / "MEMORY.md",
            Path("MEMORY.md"),
        ]
        for yol in adaylar:
            try:
                if yol.exists():
                    icerik = yol.read_text(encoding="utf-8").strip()
                    return icerik[-2000:] if len(icerik) > 2000 else icerik
            except OSError as _prompt_a_e130:
                print(f"[UYARI] prompt_assembly.py:131 - {_prompt_a_e130}")
        return ""

    def _beceri_baglamini_al(self, hedef: str) -> str:
        """ClosedLearningLoop'tan ilgili beceri baglami al."""
        if self._learning_loop is None:
            return ""
        try:
            return self._learning_loop.beceri_baglamini_al(hedef, adet=3) or ""
        except Exception:
            return ""

    def _varsayilan_react_talimati(self, hedef, son_gozlem, tur, toplam_tur) -> str:
        """sistem_talimati import edilemezse basit yedek talimat."""
        baz = (
            "Sen ReYMeN adinda otonom bir ajansin.\n"
            "ReAct dongusuyle calisirsin: Dusunce -> Eylem -> Gozlem -> Tekrar.\n"
            "Her turda sadece bir Eylem uret. Hedef tamamlandiysa GOREV_BITTI kullan.\n\n"
            "## YANIT FORMATI\n"
            "Yanitlarini su formatta ver:\n"
            "- Basliklari ## ile kullan\n"
            "- Bilgiyi tablo (| | |), liste (-) veya gorev listesi (- [x]) ile sun\n"
            "- Durum belirtmek icin emoji kullan: ✅ basarili, ❌ basarisiz, ⚠️ uyari, 🔴 kritik, 🟡 yuksek, 🟢 orta\n"
            "- Kod bloklarini ``` ile cevir\n"
            "- Karsilastirma gerekiyorsa tablo kullan\n"
            "- Ozet bilgiyi en sonda ver\n"
            "- Kisa ve oz ol: paragraf yerine liste/ tablo tercih et\n\n"
            f"## HEDEF\n{hedef}\n\n"
            f"## ILERLEME\nTur {tur}/{toplam_tur}"
        )
        if son_gozlem:
            baz += f"\n\n## SON GOZLEM\n{son_gozlem}"
        return baz

    # ── Parcacik yonetim API ───────────────────────────────────────────

    def ekle(self, ad, icerik):
        """Prompt deposuna yeni bir parcacik ekle."""
        if not ad or not isinstance(ad, str):
            return False
        if not icerik or not isinstance(icerik, str):
            return False
        self._parcalar[ad] = icerik.strip()
        return True

    def cikar(self, ad):
        """Prompt deposundan bir parcacik cikar."""
        if ad in self._parcalar:
            del self._parcalar[ad]
            return True
        return False

    def birlestir(self, parcalar, ayrac="\n\n", sablon=None):
        """Parcacik adlarini birlestir."""
        bolumler = []
        for ad in parcalar:
            if ad not in self._parcalar:
                raise KeyError(f"Parca bulunamadi: {ad}")
            bolumler.append(self._parcalar[ad])
        birlestirilmis = ayrac.join(bolumler)
        if sablon and sablon in self._sablonlar:
            birlestirilmis = self._sablonlar[sablon].replace("{icerik}", birlestirilmis)
        return birlestirilmis

    def kaydet(self, ad):
        """Parcacigi dosyaya kaydet."""
        if ad not in self._parcalar:
            return None
        try:
            dosya = self._depo_yolu / f"{ad}.txt"
            dosya.write_text(self._parcalar[ad], encoding="utf-8")
            return str(dosya)
        except OSError:
            return None

    def yukle(self, ad):
        """Parcacigi dosyadan yukle."""
        try:
            dosya = self._depo_yolu / f"{ad}.txt"
            if not dosya.exists():
                return None
            icerik = dosya.read_text(encoding="utf-8").strip()
            self._parcalar[ad] = icerik
            return icerik
        except OSError:
            return None

    def sabton_ekle(self, ad, sablon):
        """Sablon ekle ({icerik} degiskenini icermeli)."""
        if "{icerik}" not in sablon:
            return False
        self._sablonlar[ad] = sablon
        return True

    def liste(self):
        return list(self._parcalar.keys())

    def temizle(self):
        sayi = len(self._parcalar)
        self._parcalar.clear()
        return sayi

    def boyut(self, ad):
        return len(self._parcalar.get(ad, ""))

    def ara(self, kelime):
        return [ad for ad, ic in self._parcalar.items() if kelime.lower() in ic.lower()]


if __name__ == "__main__":
    pa = PromptAssembly()
    pa.ekle("giris", "Merhaba, ben ReYMeN asistaninim.")
    pa.ekle("talimat", "Kullaniciya yardimci ol.")
    print(f"Parcalar: {pa.liste()}")
    print(f"Birlestirilmis:\n{pa.birlestir(['giris', 'talimat'])}")
    print("\n--- insa_et testi ---")
    prompt = pa.insa_et("Test hedefi", son_gozlem="onceki cikti ok", tur=2, toplam_tur=10)
    print(prompt[:300])


# Eski ad uyumlulugu
PromptAssemblyEngine = PromptAssembly
