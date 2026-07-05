# -*- coding: utf-8 -*-
"""prompt_builder.py â€” GeliÅŸmiÅŸ Prompt Ä°nÅŸa Motoru.

Sistem prompt'unu, kullanÄ±cÄ± mesajlarÄ±nÄ±, hafÄ±za, skill,
trajectory ve referanslarÄ± birleÅŸtirerek LLM'e gÃ¶nderilecek
eksiksiz prompt'u oluÅŸturur.

Ã–zellikler:
  - Ã‡oklu kaynak birleÅŸtirme (SOUL, MEMORY, USER, skills, trajectory)
  - Dinamik araÃ§ listesi (motor tarafÄ±ndan kayÄ±t)
  - Kanban durumu enjeksiyonu
  - Context references enjeksiyonu
  - GÃ¶rev tipine gÃ¶re prompt ÅŸablonu seÃ§imi
  - Context penceresi yÃ¶netimi (token bÃ¼tÃ§esi)
  - OpenAI uyumlu mesaj listesi Ã¼retimi (mesaj_listesi / tur_mesaj_listesi)
  - Token analizi raporu
  - Adaptif detay seviyesi
"""

import json
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# â”€â”€ Sabit yollar
PROJE_KOK = Path(__file__).parent.resolve()
SOUL_YOLU = PROJE_KOK / ".ReYMeN" / "SOUL.md"
MEMORY_YOLU = PROJE_KOK / ".ReYMeN" / "memories" / "MEMORY.md"
USER_YOLU = PROJE_KOK / ".ReYMeN" / "memories" / "USER.md"
SKILLS_KLASOR = PROJE_KOK / ".ReYMeN" / "skills"
KANBAN_YOLU = PROJE_KOK / ".ReYMeN" / "kanban" / "gorevler.json"

CTX_TOKEN_LIMITI = 8000

# â”€â”€ AraÃ§ listesi (statik varsayÄ±lan â€” motor dinamik olarak gÃ¼nceller) â”€â”€
VARSAYILAN_ARACLAR = [
    'KOMUT_CALISTIR("kabuk komutu")     â€” shell komutu Ã§alÄ±ÅŸtÄ±r',
    'PYTHON_CALISTIR("python kodu")     â€” python sandbox',
    'DOSYA_YAZ("dosya", "icerik")       â€” dosyaya yaz',
    'DOSYA_OKU("dosya")                 â€” dosyadan oku',
    'WEB_ARA("sorgu")                   â€” web aramasÄ±',
    'TARAYICI_AC("url")                 â€” sayfayÄ± aÃ§ ve oku',
    'EKRAN_TIKLA("yazi")                â€” ekranda bul ve tÄ±kla',
    "EKRAN_OKU()                        â€” ekran metnini oku",
    'HAFIZA_ARA("sorgu")                â€” geÃ§miÅŸ deneyimlerde ara',
    'TELEGRAM_GONDER("mesaj")           â€” telegram bildirimi',
    'MAKRO_OYNAT("makro_adi")           â€” kayÄ±tlÄ± makro oynat',
    'GOREV_BITTI("kullaniciya_yanit")    â€” gÃ¶revi bitir; argÃ¼man kullanÄ±cÄ±ya gÃ¶sterilir',
]

# â”€â”€ GÃ¶rev tipi ÅŸablonlarÄ± â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
TEMPLATELER = {
    "genel": {
        "aciklama": "Genel amaÃ§lÄ± gÃ¶rev",
        "vurgu": "Hedefe odaklan, adÄ±m adÄ±m ilerle.",
    },
    "dosya": {
        "aciklama": "Dosya iÅŸlemi",
        "vurgu": "Dosya yolunu doÄŸrula, iÃ§eriÄŸi kontrol et, hata varsa raporla.",
    },
    "kod": {
        "aciklama": "Kod yazma/Ã§alÄ±ÅŸtÄ±rma",
        "vurgu": "Ã–nce PYTHON_CALISTIR ile test et, hata yoksa DOSYA_YAZ ile kaydet. try/except kullan.",
    },
    "web": {
        "aciklama": "Web iÅŸlemi",
        "vurgu": "Ã–nce WEB_ARA ile bilgi topla, sonra TARAYICI_AC ile detaya in.",
    },
    "ekran": {
        "aciklama": "Ekran iÅŸlemi",
        "vurgu": "Ã–nce EKRAN_OKU ile ekranÄ± oku, sonra EKRAN_TIKLA ile iÅŸlem yap.",
    },
    "arastirma": {
        "aciklama": "AraÅŸtÄ±rma/analiz",
        "vurgu": "Ã–nce plan yap, sonra adÄ±m adÄ±m araÅŸtÄ±r, en son rapor haline getir.",
    },
}

# â”€â”€ ReAct format talimatÄ± â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
REACT_TALIMATI = ""


# â”€â”€ Token yÃ¶netimi â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def _token_say(metin: str) -> int:
    """4 karakter â‰ˆ 1 token yaklaÅŸÄ±mÄ±."""
    return max(1, len(metin) // 4)


def _kes(metin: str, max_token: int, taraf: str = "bas") -> str:
    """Metni max_token sÄ±nÄ±rÄ±na kÄ±rp."""
    if _token_say(metin) <= max_token:
        return metin
    max_char = max_token * 4
    if taraf == "son":
        return "...\n" + metin[-max_char:]
    return metin[:max_char] + "\n...[kesildi]"


class PromptBuilder:
    """GeliÅŸmiÅŸ prompt inÅŸa motoru.

    KullanÄ±m:
        pb = PromptBuilder()
        pb.araclar_kaydet(["DOSYA_OKU(...)", "WEB_ARA(...)"])
        sistem, mesajlar = pb.insa("hedef", gorev_tipi="dosya")

        # veya OpenAI uyumlu:
        mesaj_listesi = pb.mesaj_listesi("hedef")
    """

    def __init__(
        self,
        soul_dosyasi: Optional[Path] = None,
        max_token: int = CTX_TOKEN_LIMITI,
    ):
        self.soul_dosyasi = soul_dosyasi or SOUL_YOLU
        self.max_token = max_token
        self._araclar: list[str] = []  # motor tarafÄ±ndan doldurulur

    # â”€â”€ AraÃ§ kaydÄ± â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def araclar_kaydet(self, araclar: list[str]):
        """Motor mevcut araÃ§ listesini bildirir."""
        self._araclar = list(araclar)

    def _araclar_metni(self) -> str:
        liste = self._araclar or VARSAYILAN_ARACLAR
        satirlar = ["## KullanÄ±labilir AraÃ§lar"]
        for a in liste:
            satirlar.append(f"  â€¢ {a}")
        return "\n".join(satirlar)

    # â”€â”€ Kaynak okuyucular â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def _soul_oku(self) -> str:
        if self.soul_dosyasi and self.soul_dosyasi.exists():
            return self.soul_dosyasi.read_text(encoding="utf-8").strip()
        return "Ben ReYMeN, otonom bir yazÄ±lÄ±m ajanÄ±yÄ±m."

    def _memory_oku(self, max_satir: int = 20) -> str:
        if not MEMORY_YOLU.exists():
            return ""
        satirlar = MEMORY_YOLU.read_text(encoding="utf-8").strip().split("\n")
        return "\n".join(satirlar[-max_satir:])

    def _user_oku(self, max_satir: int = 10) -> str:
        if not USER_YOLU.exists():
            return ""
        satirlar = USER_YOLU.read_text(encoding="utf-8").strip().split("\n")
        return "\n".join(satirlar[:max_satir])

    def _kanban_ozeti(self) -> str:
        if not KANBAN_YOLU.exists():
            return ""
        try:
            gorevler = json.loads(KANBAN_YOLU.read_text(encoding="utf-8"))
            aktif = [
                g
                for g in gorevler
                if g.get("durum") in ("devam", "yapiliyor", "bekliyor")
            ]
            if not aktif:
                return ""
            satirlar = ["[Kanban Aktif GÃ¶revler]"]
            for g in aktif[:4]:
                durum = g.get("durum", "?").upper()
                baslik = g.get("baslik", g.get("hedef", "?"))[:55]
                satirlar.append(f"  [{durum}] {baslik}")
            return "\n".join(satirlar)
        except Exception:
            return ""

    def _skills_ozeti(self, limit: int = 6) -> str:
        if not SKILLS_KLASOR.exists():
            return ""
        dosyalar = list(SKILLS_KLASOR.rglob("SKILL.md"))[:limit]
        if not dosyalar:
            return ""
        satirlar = ["[KullanÄ±labilir Yetenekler]"]
        for s in dosyalar:
            ad = s.parent.name
            kat = s.parent.parent.name
            satirlar.append(f"  - {kat}/{ad}")
        return "\n".join(satirlar)

    def _trajectory_gecmis(
        self,
        adimlar: Optional[list] = None,
        son_n: int = 4,
    ) -> str:
        """DoÄŸrudan adÄ±mlar listesinden ya da dosyadan Ã¶zet al."""
        if adimlar:
            son = adimlar[-son_n:]
            satirlar = ["[Son AdÄ±mlar]"]
            for a in son:
                t = a.get("tur", "?")
                e = str(a.get("eylem", ""))[:65]
                g = str(a.get("gozlem", ""))[:65]
                satirlar.append(f"  [T{t}] {e} â†’ {g}")
            return "\n".join(satirlar)

        # Dosya tabanlÄ± fallback
        traj_dir = PROJE_KOK / ".ReYMeN" / "trajectories"
        if not traj_dir.exists():
            return ""
        dosyalar = sorted(traj_dir.glob("*.json"))[-3:]
        satirlar = []
        for d in dosyalar:
            try:
                veri = json.loads(d.read_text(encoding="utf-8"))
                satirlar.append(f"  {veri['hedef'][:45]}: {veri['adim_sayisi']} adÄ±m")
            except Exception as _e:
                logger.warning("[Trajectory gecmis] JSON: %s", _e)

        if satirlar:
            return "[GeÃ§miÅŸ GÃ¶revler]\n" + "\n".join(satirlar)
        return ""

    def _referanslar_metni(self, referanslar: Optional[list] = None) -> str:
        if not referanslar:
            return ""
        satirlar = ["[BaÄŸlam ReferanslarÄ±]"]
        for r in referanslar[-3:]:
            etiket = r.get("etiket", "?")
            icerik = r.get("icerik", "")[:80]
            satirlar.append(f"  â€¢ {etiket}: {icerik}")
        return "\n".join(satirlar)

    # â”€â”€ Ana prompt inÅŸasÄ± â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def insa(
        self,
        hedef: str,
        gorev_tipi: str = "genel",
        ek_bilgi: str = "",
        gecmis_konusma: Optional[list] = None,
        onceki_gozlem: str = "",
        tur: int = 1,
        adimlar: Optional[list] = None,
        referanslar: Optional[list] = None,
        max_token: Optional[int] = None,
    ) -> tuple[str, list]:
        """Tam prompt oluÅŸtur.

        Args:
            hedef:           KullanÄ±cÄ± hedefi
            gorev_tipi:      "genel" | "dosya" | "kod" | "web" | "ekran" | "arastirma"
            ek_bilgi:        Ek baÄŸlam
            gecmis_konusma:  Ã–nceki mesajlar listesi
            onceki_gozlem:   Bir Ã¶nceki turun gÃ¶zlemi
            tur:             Mevcut tur numarasÄ±
            adimlar:         trajectory.adimlar (doÄŸrudan enjeksiyon)
            referanslar:     context_references listesi
            max_token:       Context token sÄ±nÄ±rÄ± (None = self.max_token)

        Returns:
            (sistem_prompt_str, openai_mesajlar_listesi)
        """
        limit = max_token or self.max_token
        template = TEMPLATELER.get(gorev_tipi, TEMPLATELER["genel"])

        # BileÅŸenleri topla
        soul = self._soul_oku()
        memory = self._memory_oku()
        user_bilgi = self._user_oku()
        skills = self._skills_ozeti()
        kanban = self._kanban_ozeti()
        traj = self._trajectory_gecmis(adimlar)
        ref = self._referanslar_metni(referanslar)

        parcalar: list[str] = [soul]

        if user_bilgi:
            parcalar.append(f"## KullanÄ±cÄ± Profili\n{user_bilgi}")
        if memory:
            parcalar.append(f"## GeÃ§miÅŸ Deneyimler\n{memory}")
        if kanban:
            parcalar.append(kanban)
        if skills:
            parcalar.append(skills)
        if traj:
            parcalar.append(traj)
        if ref:
            parcalar.append(ref)

        parcalar.append(f"## Hedef\n{hedef}")

        if ek_bilgi:
            parcalar.append(f"## Ek Bilgi\n{ek_bilgi}")

        parcalar.append(f"## YaklaÅŸÄ±m ({template['aciklama']})\n{template['vurgu']}")
        parcalar.append(self._araclar_metni())
        parcalar.append(REACT_TALIMATI)

        if tur > 1 and onceki_gozlem:
            parcalar.append(
                f"## Mevcut Durum\nTur: {tur}\nGÃ¶zlem: {_kes(onceki_gozlem, 150)}"
            )

        sistem_prompt = _kes("\n\n".join(p for p in parcalar if p), limit)

        # Mesaj listesi oluÅŸtur
        mesajlar: list[dict] = []
        if gecmis_konusma:
            harcanan = _token_say(sistem_prompt)
            for m in gecmis_konusma:
                m_token = _token_say(m.get("content", ""))
                if harcanan + m_token > limit:
                    break
                mesajlar.append(m)
                harcanan += m_token

        mesajlar.append({"role": "user", "content": hedef})
        return sistem_prompt, mesajlar

    # â”€â”€ OpenAI uyumlu kÄ±sayollar â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def sistem_prompt(
        self,
        hedef: str = "",
        gorev_tipi: str = "genel",
        adimlar: Optional[list] = None,
        referanslar: Optional[list] = None,
        ek_bilgi: str = "",
    ) -> str:
        """YalnÄ±zca sistem promptunu dÃ¶ndÃ¼r."""
        sistem, _ = self.insa(
            hedef=hedef,
            gorev_tipi=gorev_tipi,
            adimlar=adimlar,
            referanslar=referanslar,
            ek_bilgi=ek_bilgi,
        )
        return sistem

    def mesaj_listesi(
        self,
        hedef: str,
        gorev_tipi: str = "genel",
        adimlar: Optional[list] = None,
        referanslar: Optional[list] = None,
    ) -> list[dict]:
        """OpenAI/LM Studio uyumlu [system, user] mesaj listesi."""
        sistem = self.sistem_prompt(
            hedef=hedef,
            gorev_tipi=gorev_tipi,
            adimlar=adimlar,
            referanslar=referanslar,
        )
        return [
            {"role": "system", "content": sistem},
            {"role": "user", "content": hedef},
        ]

    def tur_mesaj_listesi(
        self,
        hedef: str,
        tur: int,
        adimlar: Optional[list] = None,
        onceki_gozlem: str = "",
        gorev_tipi: str = "genel",
        referanslar: Optional[list] = None,
    ) -> list[dict]:
        """Devam eden tur iÃ§in tam konuÅŸma geÃ§miÅŸli mesaj listesi."""
        sistem = self.sistem_prompt(
            hedef=hedef,
            gorev_tipi=gorev_tipi,
            adimlar=adimlar,
            referanslar=referanslar,
        )
        mesajlar: list[dict] = [{"role": "system", "content": sistem}]

        # Son 6 adÄ±mÄ± konuÅŸma geÃ§miÅŸi olarak ekle
        if adimlar:
            for a in adimlar[-6:]:
                eylem = str(a.get("eylem", "")).strip()
                gozlem = str(a.get("gozlem", "")).strip()
                if eylem:
                    mesajlar.append({"role": "assistant", "content": eylem})
                if gozlem:
                    mesajlar.append(
                        {
                            "role": "user",
                            "content": f"GÃ¶zlem: {_kes(gozlem, 150)}",
                        }
                    )

        mesajlar.append(
            {
                "role": "user",
                "content": self.tur_promptu(
                    tur, onceki_gozlem=onceki_gozlem, hedef=hedef
                ),
            }
        )
        return mesajlar

    def tur_promptu(
        self,
        tur: int,
        dusunce: str = "",
        onceki_gozlem: str = "",
        hedef: str = "",
    ) -> str:
        """Ara tur kullanÄ±cÄ± mesajÄ±."""
        satirlar = [f"## Tur {tur}"]
        if hedef:
            satirlar.append(f"Hedef: {hedef}")
        if onceki_gozlem:
            satirlar.append(f"GÃ¶zlem: {_kes(onceki_gozlem, 200)}")
        if dusunce:
            satirlar.append(f"DÃ¼ÅŸÃ¼nce: {dusunce}")
        satirlar.append("\nÅimdi: DoÄŸrudan yanÄ±t ver veya uygun aracÄ± kullan.")
        return "\n".join(satirlar)

    # â”€â”€ Token analizi â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def token_analizi(
        self,
        hedef: str = "",
        adimlar: Optional[list] = None,
    ) -> dict:
        """Prompt bileÅŸenlerinin tahmini token maliyeti."""
        bilesenler = {
            "soul": _token_say(self._soul_oku()),
            "memory": _token_say(self._memory_oku()),
            "user_profil": _token_say(self._user_oku()),
            "kanban": _token_say(self._kanban_ozeti()),
            "skills": _token_say(self._skills_ozeti()),
            "trajectory": _token_say(self._trajectory_gecmis(adimlar)),
            "araclar": _token_say(self._araclar_metni()),
            "react_talimati": _token_say(REACT_TALIMATI),
            "hedef": _token_say(hedef),
        }
        bilesenler["toplam"] = sum(bilesenler.values())
        bilesenler["limit"] = self.max_token
        bilesenler["asim"] = max(0, bilesenler["toplam"] - self.max_token)
        return bilesenler


# â”€â”€ Global singleton â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
_BUILDER: Optional[PromptBuilder] = None


def varsayilan_builder() -> PromptBuilder:
    global _BUILDER
    if _BUILDER is None:
        _BUILDER = PromptBuilder()
    return _BUILDER


def hizli_sistem_promptu(
    hedef: str,
    araclar: Optional[list[str]] = None,
    adimlar: Optional[list] = None,
) -> str:
    """Tek satÄ±rda sistem promptu oluÅŸtur."""
    b = varsayilan_builder()
    if araclar:
        b.araclar_kaydet(araclar)
    return b.sistem_prompt(hedef=hedef, adimlar=adimlar)


if __name__ == "__main__":
    pb = PromptBuilder()
    pb.araclar_kaydet(
        [
            'DOSYA_OKU("yol")          â€” dosya iÃ§eriÄŸini oku',
            'DOSYA_YAZ("yol","icerik") â€” dosyaya yaz',
            'WEB_ARA("sorgu")          â€” web aramasÄ±',
            'KOMUT("cmd")              â€” shell komutu',
            'GOREV_BITTI("ozet")       â€” bitir',
        ]
    )

    hedef = "Proje klasÃ¶rÃ¼ndeki Python dosyalarÄ±nÄ± analiz et, Ã¶zet rapor yaz"

    print("=== TOKEN ANALÄ°ZÄ° ===")
    for k, v in pb.token_analizi(hedef).items():
        print(f"  {k:<22} {v}")

    print("\n=== MESAJ LÄ°STESÄ° ===")
    for m in pb.mesaj_listesi(hedef, gorev_tipi="kod"):
        print(f"[{m['role']}] {m['content'][:120]}...\n")

    print("=== TUR MESAJ LÄ°STESÄ° (tur=3) ===")
    tur_mesajlari = pb.tur_mesaj_listesi(
        hedef,
        tur=3,
        adimlar=[
            {"tur": 1, "eylem": 'KOMUT("ls")', "gozlem": "3 dosya"},
            {"tur": 2, "eylem": 'DOSYA_OKU("a.py")', "gozlem": "200 satir"},
        ],
    )
    print(f"{len(tur_mesajlari)} mesaj uretildi")
    for m in tur_mesajlari:
        print(f"  [{m['role']}] {m['content'][:80]}...")
