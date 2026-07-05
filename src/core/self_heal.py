"""
SelfHeal â€” Otonom hata Ã§Ã¶zÃ¼cÃ¼ (v2).

Hata al â†’ imza Ã¼ret â†’ hafÄ±zada ara â†’ bulursa uygula â†’ bulamazsa LLM'e sor
â†’ LLM'den Python kodu al â†’ Ã§alÄ±ÅŸtÄ±r (subprocess) â†’ doÄŸrula â†’ hafÄ±zaya kaydet â†’ dÃ¶ndÃ¼r.

Ä°yileÅŸtirmeler (v2):
- SUBPROCESS_MOD: exec() yerine subprocess (gerÃ§ek ortam testi)
- TTL temizlik: Her coz() Ã§aÄŸrÄ±sÄ±nda otomatik temizlik
- __init__.py export desteÄŸi
- motor.py script_calistir() ile tam entegrasyon

KullanÄ±m:
    from reymen.core.self_heal import SelfHeal
    heal = SelfHeal()
    sonuc = heal.coz(hedef="test.py", hata="ZeroDivisionError", kod="print(1/0)")

BaÄŸÄ±mlÄ±lÄ±klar:
    - ogrenme.py (imza, cozum_bul, cozum_kaydet)
    - orchestrator.py (coz_hata)
    - model_adapter.py (get_active_adapter)
"""

import sys
import logging
import time
import traceback
import hashlib
import re
import subprocess
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# â”€â”€ Deneme AyarlarÄ± â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
MAX_DENEME = 3
BACKOFF_TABAN = 1.0  # saniye
BACKOFF_CARPAN = 2.0

# â”€â”€ Ã‡alÄ±ÅŸtÄ±rma Modu â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# True  = subprocess (daha gÃ¼venli, gerÃ§ek ortam, tam Python izolasyonu)
# False = exec()     (hÄ±zlÄ±, hafif, modÃ¼l iÃ§i test)
SUBPROCESS_MOD = True


class SelfHeal:
    """Ana self-heal sÄ±nÄ±fÄ±. Motor.py'den Ã§aÄŸrÄ±lÄ±r.

    AkÄ±ÅŸ:
        1. imza_uret(hata, dosya) â†’ SHA256
        2. cozum_bul(imza) â†’ hafÄ±zada varsa direkt dÃ¶ndÃ¼r
        3. LLM'e sor â†’ Python kodu Ã¼ret
        4. Kodu Ã§alÄ±ÅŸtÄ±r (subprocess veya exec)
        5. BaÅŸarÄ±lÄ± â†’ cozum_kaydet(imza, cozum)
        6. BaÅŸarÄ±sÄ±z â†’ 3 deneme, backoff, farklÄ± prompt
    """

    def __init__(self, max_deneme: int = MAX_DENEME):
        self.max_deneme = max_deneme
        self._toplam = 0
        self._basarili = 0
        self._hafiza_isabet = 0
        self._adapter = None

    # â”€â”€ Ana Metod â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def coz(self, hedef: str, hata: str, kod: str = "", dosya_yolu: str = "") -> dict:
        """Bir hatayÄ± otonom Ã§Ã¶z.

        Args:
            hedef: Ne Ã§Ã¶zÃ¼lmeye Ã§alÄ±ÅŸÄ±lÄ±yor (Ã¶rn: "test.py Ã§alÄ±ÅŸtÄ±r")
            hata: Hata mesajÄ± (str(e) veya traceback)
            kod: Hata veren Python kodu (opsiyonel)
            dosya_yolu: Hata hangi dosyada (opsiyonel, imza iÃ§in)

        Returns:
            {
                "basarili": bool,
                "cozum": str (dÃ¼zeltilmiÅŸ kod veya aÃ§Ä±klama),
                "kaynak": "hafiza" | "llm" | "basarisiz",
                "deneme_sayisi": int,
                "hata": str (sadece baÅŸarÄ±sÄ±zsa)
            }
        """
        self._toplam += 1

        # TTL temizlik (her 10 Ã§aÄŸrÄ±da bir)
        if self._toplam % 10 == 1:
            self._ttl_temizle()

        # 1. Ä°mza Ã¼ret + hafÄ±zada ara
        hata_imza = self._imza_uret(hata, dosya_yolu or hedef)
        logger.info("[SelfHeal] ğŸ” Hata: %s | imza: %s", hata[:80], hata_imza[:16])

        hafiza_cozum = self._hafizada_ara(hata_imza)
        if hafiza_cozum:
            self._hafiza_isabet += 1
            self._basarili += 1
            logger.info("[SelfHeal] âœ… HafÄ±zadan Ã§Ã¶zÃ¼m: %s", hafiza_cozum[:100])
            return {
                "basarili": True,
                "cozum": hafiza_cozum,
                "kaynak": "hafiza",
                "deneme_sayisi": 0,
                "hata": "",
            }

        # 2. LLM ile Ã§Ã¶z
        for deneme in range(1, self.max_deneme + 1):
            if deneme > 1:
                bekleme = BACKOFF_TABAN * (BACKOFF_CARPAN ** (deneme - 2))
                logger.info(
                    "[SelfHeal] â³ Bekleme: %.1fs (deneme %d/%d)",
                    bekleme,
                    deneme,
                    self.max_deneme,
                )
                time.sleep(bekleme)

            cozum_kodu = self._llm_coz(hedef, hata, kod, deneme)
            if not cozum_kodu:
                continue

            # 3. Ã‡Ã¶zÃ¼mÃ¼ dene
            basarili, cikti = self._cozumu_dene(cozum_kodu)
            if basarili:
                self._basarili += 1
                # HafÄ±zaya kaydet
                self._hafizaya_kaydet(hata_imza, hata, cozum_kodu, basarili=True)
                logger.info("[SelfHeal] âœ… Ã‡Ã¶zÃ¼m baÅŸarÄ±lÄ± (deneme %d)", deneme)
                return {
                    "basarili": True,
                    "cozum": cozum_kodu,
                    "kaynak": "llm",
                    "deneme_sayisi": deneme,
                    "hata": "",
                }

            # DÃ¼zelmedi â€” hatayÄ± LLM'e geri bildir
            logger.info("[SelfHeal] âŒ Deneme %d baÅŸarÄ±sÄ±z: %s", deneme, cikti[:120])
            hata = cikti  # yeni hata = Ã§alÄ±ÅŸtÄ±rma hatasÄ±
            kod = cozum_kodu  # mevcut kodu dÃ¼zeltmesi iÃ§in gÃ¶nder

        # 3 deneme de baÅŸarÄ±sÄ±z
        self._hafizaya_kaydet(hata_imza, hata, "", basarili=False)
        logger.warning("[SelfHeal] ğŸ’€ 3 denemede Ã§Ã¶zÃ¼lemedi: %s", hedef)
        return {
            "basarili": False,
            "cozum": "",
            "kaynak": "basarisiz",
            "deneme_sayisi": self.max_deneme,
            "hata": f"{self.max_deneme} denemede Ã§Ã¶zÃ¼lemedi: {hata[:200]}",
        }

    # â”€â”€ Motor Entegrasyonu â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def script_coz(self, script_path: str, hata_cikti: str) -> dict:
        """Motor.script_calistir() iÃ§inde Ã§aÄŸrÄ±lÄ±r.

        Args:
            script_path: Hata veren script'in tam yolu
            hata_cikti: stderr Ã§Ä±ktÄ±sÄ±

        Returns:
            {
                "basarili": bool,
                "fix_kodu": str (dÃ¼zeltilmiÅŸ kod),
                "kaynak": str
            }
        """
        path = Path(script_path)
        kod = path.read_text("utf-8", errors="replace") if path.exists() else ""
        hedef = str(path.name)

        sonuc = self.coz(hedef, hata_cikti, kod, dosya_yolu=str(path))

        # BaÅŸarÄ±lÄ±ysa fix'i diske yaz
        if sonuc["basarili"] and sonuc["cozum"]:
            fix_dir = path.parent / "fix"
            fix_dir.mkdir(exist_ok=True)
            fix_path = fix_dir / f"{path.stem}_fix_v{sonuc['deneme_sayisi'] or 1}.py"
            fix_path.write_text(sonuc["cozum"], "utf-8")
            sonuc["fix_path"] = str(fix_path)

        return sonuc

    # â”€â”€ Ä°mza â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    @staticmethod
    def _imza_uret(hata: str, dosya: str = "") -> str:
        """Hata mesajÄ± + dosya adÄ±ndan SHA256 imza Ã¼ret."""
        # Hata mesajÄ±nÄ± normalize et (sayÄ±larÄ±, adresleri soyutla)
        temiz = re.sub(r"0x[0-9a-fA-F]+", "0x...", hata)
        temiz = re.sub(r"\b\d+\b", "N", temiz)
        temiz = re.sub(r'File ".*?"', 'File "..."', temiz)
        kaynak = f"{dosya}|{temiz[:200]}"
        return hashlib.sha256(kaynak.encode()).hexdigest()

    # â”€â”€ HafÄ±za â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    @staticmethod
    def _hafizada_ara(imza: str) -> Optional[str]:
        """OnceHafiza/ogrenme'de Ã§Ã¶zÃ¼m ara."""
        try:
            from reymen.core.ogrenme import cozum_bul, tablo_olustur

            tablo_olustur()
            return cozum_bul(imza)
        except Exception as e:
            logger.debug("[SelfHeal] HafÄ±za arama hatasÄ±: %s", e)
            return None

    @staticmethod
    def _hafizaya_kaydet(imza: str, hata: str, cozum: str, basarili: bool):
        """Ã‡Ã¶zÃ¼mÃ¼ hafÄ±zaya kaydet."""
        try:
            from reymen.core.ogrenme import cozum_kaydet

            hata_tipi = hata.split(":")[0].split("\n")[0][:50]
            cozum_kaydet(
                imza, hata_tipi, hata[:500], cozum, "self_heal", basarili=basarili
            )
        except Exception as e:
            logger.debug("[SelfHeal] HafÄ±za kayÄ±t hatasÄ±: %s", e)

    @staticmethod
    def _ttl_temizle():
        """TTL sÃ¼resi dolmuÅŸ Ã§Ã¶zÃ¼mleri temizle."""
        try:
            from reymen.core.ogrenme import ttl_temizle

            ttl_temizle()
        except Exception:
            logger.warning("[fix_01_sessiz_except] Exception")

    # â”€â”€ LLM â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def _llm_coz(self, hedef: str, hata: str, kod: str, deneme: int) -> Optional[str]:
        """LLM'e sor ve dÃ¼zeltilmiÅŸ kod al."""
        adapter = self._adapter_al()
        if not adapter:
            return None

        kod_bolumu = ""
        if kod:
            kod_bolumu = f"KOD:\n{kod}\n"

        if deneme == 1:
            prompt = (
                "Bir Python betiÄŸi Ã§alÄ±ÅŸtÄ±rÄ±lÄ±rken hata alÄ±ndÄ±.\n\n"
                f"HEDEF: {hedef}\n"
                f"HATA: {hata}\n"
                f"{kod_bolumu}\n"
                "GÃ¶revin:\n"
                "1. HatanÄ±n kaynaÄŸÄ±nÄ± belirle\n"
                "2. DÃ¼zeltilmiÅŸ Python kodunu Ã¼ret\n"
                "3. Sadece KODU dÃ¶ndÃ¼r â€” aÃ§Ä±klama, yorum, markdown kullanma\n"
                "4. Kod doÄŸrudan exec() ile Ã§alÄ±ÅŸtÄ±rÄ±labilir olmalÄ±\n"
            )
        else:
            onceki_kod = ""
            if kod:
                onceki_kod = f"Ã–NCEKÄ° KOD:\n{kod[:500]}\n"

            prompt = (
                "Bir Ã¶nceki Ã§Ã¶zÃ¼m iÅŸe yaramadÄ±.\n\n"
                f"HEDEF: {hedef}\n"
                f"{onceki_kod}"
                f"YENÄ° HATA: {hata}\n\n"
                "FarklÄ± bir yaklaÅŸÄ±m dene.\n"
                "Sadece Ã§alÄ±ÅŸan Python kodunu dÃ¶ndÃ¼r.\n"
            )
        try:
            cevap = adapter.complete(prompt)
            return self._kod_ayikla(cevap)
        except Exception as e:
            logger.warning("[SelfHeal] LLM hatasÄ±: %s", e)
            return None

    @staticmethod
    def _kod_ayikla(cevap: str) -> Optional[str]:
        """LLM cevabÄ±ndan Python kodunu ayÄ±kla."""
        # ```python ... ``` bloklarÄ±nÄ± ayÄ±kla
        blok = re.search(r"```(?:python)?\n(.*?)```", cevap, re.DOTALL)
        if blok:
            return blok.group(1).strip()
        # HiÃ§bir blok yoksa kod satÄ±rlarÄ±nÄ± dene
        satirlar = []
        kod_bolgesi = False
        for satir in cevap.splitlines():
            if satir.strip().startswith(
                (
                    "import ",
                    "from ",
                    "def ",
                    "class ",
                    "print(",
                    "return ",
                    "if ",
                    "for ",
                    "while ",
                    "try:",
                    "with ",
                    "async ",
                )
            ):
                kod_bolgesi = True
            if kod_bolgesi:
                satirlar.append(satir)
        if satirlar:
            return "\n".join(satirlar)
        return None

    # â”€â”€ Ã‡alÄ±ÅŸtÄ±rma â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def _cozumu_dene(self, kod: str) -> tuple:
        """Kodu Ã§alÄ±ÅŸtÄ±r, baÅŸarÄ±lÄ± mÄ± dÃ¶ndÃ¼r.

        SUBPROCESS_MOD=True (varsayÄ±lan):
            Kodu geÃ§ici bir .py dosyasÄ±na yazar ve subprocess ile Ã§alÄ±ÅŸtÄ±rÄ±r.
            Daha gÃ¼venli, gerÃ§ek ortamÄ± test eder.

        SUBPROCESS_MOD=False:
            exec() ile Ã§alÄ±ÅŸtÄ±rÄ±r. HÄ±zlÄ± ama izole deÄŸil.
        """
        if not kod or not kod.strip():
            return False, "BoÅŸ kod"

        if SUBPROCESS_MOD:
            return self._subprocess_dene(kod)
        else:
            return self._exec_dene(kod)

    @staticmethod
    def _subprocess_dene(kod: str) -> tuple:
        """Kodu geÃ§ici dosyaya yaz, subprocess ile Ã§alÄ±ÅŸtÄ±r."""
        import tempfile
        import os

        tmp_path = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".py", delete=False, encoding="utf-8"
            ) as f:
                f.write(kod)
                tmp_path = f.name

            r = subprocess.run(
                [sys.executable, tmp_path], capture_output=True, text=True, timeout=30
            )

            if r.returncode == 0:
                return True, r.stdout[:500]
            else:
                return False, r.stderr[:500]

        except subprocess.TimeoutExpired:
            return False, "TIMEOUT: 30s aÅŸÄ±ldÄ±"
        except Exception as e:
            return False, f"{type(e).__name__}: {e}"
        finally:
            if tmp_path:
                try:
                    os.unlink(tmp_path)
                except Exception:
                    logger.warning("[fix_01_sessiz_except] Exception")

    @staticmethod
    def _exec_dene(kod: str) -> tuple:
        """Kodu exec ile Ã§alÄ±ÅŸtÄ±r."""
        try:
            local_ns = {}
            exec(kod, {"__builtins__": __builtins__}, local_ns)
            return True, str(local_ns.get("_cikti", ""))
        except SyntaxError as e:
            return False, f"SyntaxError: {e}"
        except Exception as e:
            return False, f"{type(e).__name__}: {e}"

    # â”€â”€ Adapter â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def _adapter_al(self):
        """ModelAdapter al (lazy init)."""
        if self._adapter is None:
            try:
                from reymen.core.model_adapter import get_active_adapter

                self._adapter = get_active_adapter()
            except Exception as e:
                logger.error("[SelfHeal] Model adapter hatasÄ±: %s", e)
                return None
        return self._adapter

    # â”€â”€ Motor Entegrasyon AracÄ± â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    @staticmethod
    def motor_calistir_icinde(motor_self, arac: str, ham_param: str) -> str:
        """Motor.calistir() iÃ§inde SELF_HEAL aracÄ± olarak Ã§aÄŸrÄ±lÄ±r.

        Parametre: hedef|hata|kod
        Ã–rnek: SELF_HEAL("test.py|ZeroDivisionError|print(1/0)")
        """
        try:
            parts = [p.strip() for p in ham_param.split("|", 2)]
            hedef = parts[0] if len(parts) > 0 else "bilinmeyen"
            hata = parts[1] if len(parts) > 1 else ""
            kod = parts[2] if len(parts) > 2 else ""

            if not hata:
                return "[SelfHeal] âŒ Hata mesajÄ± gerekli. Format: hedef|hata|kod"

            heal = SelfHeal()
            sonuc = heal.coz(hedef, hata, kod)

            if sonuc["basarili"]:
                return (
                    f"[SelfHeal] âœ… Ã‡Ã¶zÃ¼ldÃ¼ (kaynak: {sonuc['kaynak']}, "
                    f"deneme: {sonuc['deneme_sayisi']})\n"
                    f"Ã‡Ã¶zÃ¼m:\n{sonuc['cozum']}"
                )
            else:
                return (
                    f"[SelfHeal] âŒ Ã‡Ã¶zÃ¼lemedi "
                    f"({sonuc['deneme_sayisi']} deneme)\n"
                    f"Hata: {sonuc['hata']}"
                )
        except Exception as e:
            logger.exception("[SelfHeal] motor_calistir_icinde hatasÄ±")
            return f"[SelfHeal] âŒ Ä°Ã§ hata: {e}"

    @staticmethod
    def motor_hatadan_kurtul(
        motor_self, kod: str, hata: str, dosya_adi: str = ""
    ) -> str:
        """Motor.hatadan_kurtul() metoduna self_heal entegrasyonu.

        Mevcut hatadan_kurtul()'u geliÅŸtirir:
        OnceHafiza + OgrenmeDongusu + self_heal + orchestrator
        """
        # 1. Ã–nce mevcut motor.hatadan_kurtul() dene
        try:
            eski_cozum = motor_self.hatadan_kurtul(kod, hata, dosya_adi)
            if eski_cozum and not eski_cozum.startswith(
                ("Ã‡Ã¶zÃ¼m bulunamadÄ±", "Hata cozulemedi")
            ):
                return eski_cozum
        except Exception as e:
            logger.debug("[SelfHeal] Motor.hatadan_kurtul hatasÄ±: %s", e)

        # 2. SelfHeal ile dene
        heal = SelfHeal()
        sonuc = heal.coz(dosya_adi or "bilinmeyen", hata, kod)

        if sonuc["basarili"]:
            if sonuc["kaynak"] == "hafiza":
                return f"[SelfHeal HafÄ±za] {sonuc['cozum']}"
            return sonuc["cozum"]
        else:
            return f"Ã‡Ã¶zÃ¼m bulunamadÄ±. Hata: {hata[:200]}"

    # â”€â”€ Ä°statistik â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def istatistik(self) -> dict:
        """SelfHeal istatistikleri."""
        return {
            "toplam_hata": self._toplam,
            "basarili_cozum": self._basarili,
            "hafiza_isabet": self._hafiza_isabet,
            "basari_orani": round(
                (self._basarili / self._toplam * 100) if self._toplam > 0 else 0, 1
            ),
            "hafiza_orani": round(
                (self._hafiza_isabet / self._toplam * 100) if self._toplam > 0 else 0, 1
            ),
        }


# â”€â”€ DoÄŸrudan KullanÄ±m â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


def coz(hedef: str, hata: str, kod: str = "", dosya_yolu: str = "") -> dict:
    """Tek Ã§aÄŸrÄ±lÄ±k self-heal."""
    return SelfHeal().coz(hedef, hata, kod, dosya_yolu)


def script_coz(script_path: str, hata_cikti: str) -> dict:
    """Motor.script_calistir iÃ§in kolaylÄ±k fonksiyonu."""
    return SelfHeal().script_coz(script_path, hata_cikti)


def istatistik_al() -> dict:
    """KÃ¼resel istatistik (yoksa boÅŸ dÃ¶ndÃ¼r)."""
    try:
        return SelfHeal().istatistik()
    except Exception:
        return {"hata": "SelfHeal henÃ¼z Ã§alÄ±ÅŸmadÄ±"}
