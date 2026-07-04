"""
SelfHeal — Otonom hata çözücü (v2).

Hata al → imza üret → hafızada ara → bulursa uygula → bulamazsa LLM'e sor
→ LLM'den Python kodu al → çalıştır (subprocess) → doğrula → hafızaya kaydet → döndür.

İyileştirmeler (v2):
- SUBPROCESS_MOD: exec() yerine subprocess (gerçek ortam testi)
- TTL temizlik: Her coz() çağrısında otomatik temizlik
- __init__.py export desteği
- motor.py script_calistir() ile tam entegrasyon

Kullanım:
    from reymen.core.self_heal import SelfHeal
    heal = SelfHeal()
    sonuc = heal.coz(hedef="test.py", hata="ZeroDivisionError", kod="print(1/0)")

Bağımlılıklar:
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

# ── Deneme Ayarları ──────────────────────────────────────────────
MAX_DENEME = 3
BACKOFF_TABAN = 1.0  # saniye
BACKOFF_CARPAN = 2.0

# ── Çalıştırma Modu ─────────────────────────────────────────────
# True  = subprocess (daha güvenli, gerçek ortam, tam Python izolasyonu)
# False = exec()     (hızlı, hafif, modül içi test)
SUBPROCESS_MOD = True


class SelfHeal:
    """Ana self-heal sınıfı. Motor.py'den çağrılır.

    Akış:
        1. imza_uret(hata, dosya) → SHA256
        2. cozum_bul(imza) → hafızada varsa direkt döndür
        3. LLM'e sor → Python kodu üret
        4. Kodu çalıştır (subprocess veya exec)
        5. Başarılı → cozum_kaydet(imza, cozum)
        6. Başarısız → 3 deneme, backoff, farklı prompt
    """

    def __init__(self, max_deneme: int = MAX_DENEME):
        self.max_deneme = max_deneme
        self._toplam = 0
        self._basarili = 0
        self._hafiza_isabet = 0
        self._adapter = None

    # ── Ana Metod ────────────────────────────────────────────────

    def coz(self, hedef: str, hata: str, kod: str = "", dosya_yolu: str = "") -> dict:
        """Bir hatayı otonom çöz.

        Args:
            hedef: Ne çözülmeye çalışılıyor (örn: "test.py çalıştır")
            hata: Hata mesajı (str(e) veya traceback)
            kod: Hata veren Python kodu (opsiyonel)
            dosya_yolu: Hata hangi dosyada (opsiyonel, imza için)

        Returns:
            {
                "basarili": bool,
                "cozum": str (düzeltilmiş kod veya açıklama),
                "kaynak": "hafiza" | "llm" | "basarisiz",
                "deneme_sayisi": int,
                "hata": str (sadece başarısızsa)
            }
        """
        self._toplam += 1

        # TTL temizlik (her 10 çağrıda bir)
        if self._toplam % 10 == 1:
            self._ttl_temizle()

        # 1. İmza üret + hafızada ara
        hata_imza = self._imza_uret(hata, dosya_yolu or hedef)
        logger.info("[SelfHeal] 🔍 Hata: %s | imza: %s", hata[:80], hata_imza[:16])

        hafiza_cozum = self._hafizada_ara(hata_imza)
        if hafiza_cozum:
            self._hafiza_isabet += 1
            self._basarili += 1
            logger.info("[SelfHeal] ✅ Hafızadan çözüm: %s", hafiza_cozum[:100])
            return {
                "basarili": True,
                "cozum": hafiza_cozum,
                "kaynak": "hafiza",
                "deneme_sayisi": 0,
                "hata": "",
            }

        # 2. LLM ile çöz
        for deneme in range(1, self.max_deneme + 1):
            if deneme > 1:
                bekleme = BACKOFF_TABAN * (BACKOFF_CARPAN ** (deneme - 2))
                logger.info(
                    "[SelfHeal] ⏳ Bekleme: %.1fs (deneme %d/%d)",
                    bekleme,
                    deneme,
                    self.max_deneme,
                )
                time.sleep(bekleme)

            cozum_kodu = self._llm_coz(hedef, hata, kod, deneme)
            if not cozum_kodu:
                continue

            # 3. Çözümü dene
            basarili, cikti = self._cozumu_dene(cozum_kodu)
            if basarili:
                self._basarili += 1
                # Hafızaya kaydet
                self._hafizaya_kaydet(hata_imza, hata, cozum_kodu, basarili=True)
                logger.info("[SelfHeal] ✅ Çözüm başarılı (deneme %d)", deneme)
                return {
                    "basarili": True,
                    "cozum": cozum_kodu,
                    "kaynak": "llm",
                    "deneme_sayisi": deneme,
                    "hata": "",
                }

            # Düzelmedi — hatayı LLM'e geri bildir
            logger.info("[SelfHeal] ❌ Deneme %d başarısız: %s", deneme, cikti[:120])
            hata = cikti  # yeni hata = çalıştırma hatası
            kod = cozum_kodu  # mevcut kodu düzeltmesi için gönder

        # 3 deneme de başarısız
        self._hafizaya_kaydet(hata_imza, hata, "", basarili=False)
        logger.warning("[SelfHeal] 💀 3 denemede çözülemedi: %s", hedef)
        return {
            "basarili": False,
            "cozum": "",
            "kaynak": "basarisiz",
            "deneme_sayisi": self.max_deneme,
            "hata": f"{self.max_deneme} denemede çözülemedi: {hata[:200]}",
        }

    # ── Motor Entegrasyonu ───────────────────────────────────────

    def script_coz(self, script_path: str, hata_cikti: str) -> dict:
        """Motor.script_calistir() içinde çağrılır.

        Args:
            script_path: Hata veren script'in tam yolu
            hata_cikti: stderr çıktısı

        Returns:
            {
                "basarili": bool,
                "fix_kodu": str (düzeltilmiş kod),
                "kaynak": str
            }
        """
        path = Path(script_path)
        kod = path.read_text("utf-8", errors="replace") if path.exists() else ""
        hedef = str(path.name)

        sonuc = self.coz(hedef, hata_cikti, kod, dosya_yolu=str(path))

        # Başarılıysa fix'i diske yaz
        if sonuc["basarili"] and sonuc["cozum"]:
            fix_dir = path.parent / "fix"
            fix_dir.mkdir(exist_ok=True)
            fix_path = fix_dir / f"{path.stem}_fix_v{sonuc['deneme_sayisi'] or 1}.py"
            fix_path.write_text(sonuc["cozum"], "utf-8")
            sonuc["fix_path"] = str(fix_path)

        return sonuc

    # ── İmza ─────────────────────────────────────────────────────

    @staticmethod
    def _imza_uret(hata: str, dosya: str = "") -> str:
        """Hata mesajı + dosya adından SHA256 imza üret."""
        # Hata mesajını normalize et (sayıları, adresleri soyutla)
        temiz = re.sub(r"0x[0-9a-fA-F]+", "0x...", hata)
        temiz = re.sub(r"\b\d+\b", "N", temiz)
        temiz = re.sub(r'File ".*?"', 'File "..."', temiz)
        kaynak = f"{dosya}|{temiz[:200]}"
        return hashlib.sha256(kaynak.encode()).hexdigest()

    # ── Hafıza ───────────────────────────────────────────────────

    @staticmethod
    def _hafizada_ara(imza: str) -> Optional[str]:
        """OnceHafiza/ogrenme'de çözüm ara."""
        try:
            from reymen.core.ogrenme import cozum_bul, tablo_olustur

            tablo_olustur()
            return cozum_bul(imza)
        except Exception as e:
            logger.debug("[SelfHeal] Hafıza arama hatası: %s", e)
            return None

    @staticmethod
    def _hafizaya_kaydet(imza: str, hata: str, cozum: str, basarili: bool):
        """Çözümü hafızaya kaydet."""
        try:
            from reymen.core.ogrenme import cozum_kaydet

            hata_tipi = hata.split(":")[0].split("\n")[0][:50]
            cozum_kaydet(
                imza, hata_tipi, hata[:500], cozum, "self_heal", basarili=basarili
            )
        except Exception as e:
            logger.debug("[SelfHeal] Hafıza kayıt hatası: %s", e)

    @staticmethod
    def _ttl_temizle():
        """TTL süresi dolmuş çözümleri temizle."""
        try:
            from reymen.core.ogrenme import ttl_temizle

            ttl_temizle()
        except Exception:
            logger.warning("[fix_01_sessiz_except] Exception")

    # ── LLM ──────────────────────────────────────────────────────

    def _llm_coz(self, hedef: str, hata: str, kod: str, deneme: int) -> Optional[str]:
        """LLM'e sor ve düzeltilmiş kod al."""
        adapter = self._adapter_al()
        if not adapter:
            return None

        kod_bolumu = ""
        if kod:
            kod_bolumu = f"KOD:\n{kod}\n"

        if deneme == 1:
            prompt = (
                "Bir Python betiği çalıştırılırken hata alındı.\n\n"
                f"HEDEF: {hedef}\n"
                f"HATA: {hata}\n"
                f"{kod_bolumu}\n"
                "Görevin:\n"
                "1. Hatanın kaynağını belirle\n"
                "2. Düzeltilmiş Python kodunu üret\n"
                "3. Sadece KODU döndür — açıklama, yorum, markdown kullanma\n"
                "4. Kod doğrudan exec() ile çalıştırılabilir olmalı\n"
            )
        else:
            onceki_kod = ""
            if kod:
                onceki_kod = f"ÖNCEKİ KOD:\n{kod[:500]}\n"

            prompt = (
                "Bir önceki çözüm işe yaramadı.\n\n"
                f"HEDEF: {hedef}\n"
                f"{onceki_kod}"
                f"YENİ HATA: {hata}\n\n"
                "Farklı bir yaklaşım dene.\n"
                "Sadece çalışan Python kodunu döndür.\n"
            )
        try:
            cevap = adapter.complete(prompt)
            return self._kod_ayikla(cevap)
        except Exception as e:
            logger.warning("[SelfHeal] LLM hatası: %s", e)
            return None

    @staticmethod
    def _kod_ayikla(cevap: str) -> Optional[str]:
        """LLM cevabından Python kodunu ayıkla."""
        # ```python ... ``` bloklarını ayıkla
        blok = re.search(r"```(?:python)?\n(.*?)```", cevap, re.DOTALL)
        if blok:
            return blok.group(1).strip()
        # Hiçbir blok yoksa kod satırlarını dene
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

    # ── Çalıştırma ───────────────────────────────────────────────

    def _cozumu_dene(self, kod: str) -> tuple:
        """Kodu çalıştır, başarılı mı döndür.

        SUBPROCESS_MOD=True (varsayılan):
            Kodu geçici bir .py dosyasına yazar ve subprocess ile çalıştırır.
            Daha güvenli, gerçek ortamı test eder.

        SUBPROCESS_MOD=False:
            exec() ile çalıştırır. Hızlı ama izole değil.
        """
        if not kod or not kod.strip():
            return False, "Boş kod"

        if SUBPROCESS_MOD:
            return self._subprocess_dene(kod)
        else:
            return self._exec_dene(kod)

    @staticmethod
    def _subprocess_dene(kod: str) -> tuple:
        """Kodu geçici dosyaya yaz, subprocess ile çalıştır."""
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
            return False, "TIMEOUT: 30s aşıldı"
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
        """Kodu exec ile çalıştır."""
        try:
            local_ns = {}
            exec(kod, {"__builtins__": __builtins__}, local_ns)
            return True, str(local_ns.get("_cikti", ""))
        except SyntaxError as e:
            return False, f"SyntaxError: {e}"
        except Exception as e:
            return False, f"{type(e).__name__}: {e}"

    # ── Adapter ──────────────────────────────────────────────────

    def _adapter_al(self):
        """ModelAdapter al (lazy init)."""
        if self._adapter is None:
            try:
                from reymen.core.model_adapter import get_active_adapter

                self._adapter = get_active_adapter()
            except Exception as e:
                logger.error("[SelfHeal] Model adapter hatası: %s", e)
                return None
        return self._adapter

    # ── Motor Entegrasyon Aracı ──────────────────────────────────

    @staticmethod
    def motor_calistir_icinde(motor_self, arac: str, ham_param: str) -> str:
        """Motor.calistir() içinde SELF_HEAL aracı olarak çağrılır.

        Parametre: hedef|hata|kod
        Örnek: SELF_HEAL("test.py|ZeroDivisionError|print(1/0)")
        """
        try:
            parts = [p.strip() for p in ham_param.split("|", 2)]
            hedef = parts[0] if len(parts) > 0 else "bilinmeyen"
            hata = parts[1] if len(parts) > 1 else ""
            kod = parts[2] if len(parts) > 2 else ""

            if not hata:
                return "[SelfHeal] ❌ Hata mesajı gerekli. Format: hedef|hata|kod"

            heal = SelfHeal()
            sonuc = heal.coz(hedef, hata, kod)

            if sonuc["basarili"]:
                return (
                    f"[SelfHeal] ✅ Çözüldü (kaynak: {sonuc['kaynak']}, "
                    f"deneme: {sonuc['deneme_sayisi']})\n"
                    f"Çözüm:\n{sonuc['cozum']}"
                )
            else:
                return (
                    f"[SelfHeal] ❌ Çözülemedi "
                    f"({sonuc['deneme_sayisi']} deneme)\n"
                    f"Hata: {sonuc['hata']}"
                )
        except Exception as e:
            logger.exception("[SelfHeal] motor_calistir_icinde hatası")
            return f"[SelfHeal] ❌ İç hata: {e}"

    @staticmethod
    def motor_hatadan_kurtul(
        motor_self, kod: str, hata: str, dosya_adi: str = ""
    ) -> str:
        """Motor.hatadan_kurtul() metoduna self_heal entegrasyonu.

        Mevcut hatadan_kurtul()'u geliştirir:
        OnceHafiza + OgrenmeDongusu + self_heal + orchestrator
        """
        # 1. Önce mevcut motor.hatadan_kurtul() dene
        try:
            eski_cozum = motor_self.hatadan_kurtul(kod, hata, dosya_adi)
            if eski_cozum and not eski_cozum.startswith(
                ("Çözüm bulunamadı", "Hata cozulemedi")
            ):
                return eski_cozum
        except Exception as e:
            logger.debug("[SelfHeal] Motor.hatadan_kurtul hatası: %s", e)

        # 2. SelfHeal ile dene
        heal = SelfHeal()
        sonuc = heal.coz(dosya_adi or "bilinmeyen", hata, kod)

        if sonuc["basarili"]:
            if sonuc["kaynak"] == "hafiza":
                return f"[SelfHeal Hafıza] {sonuc['cozum']}"
            return sonuc["cozum"]
        else:
            return f"Çözüm bulunamadı. Hata: {hata[:200]}"

    # ── İstatistik ───────────────────────────────────────────────

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


# ── Doğrudan Kullanım ──────────────────────────────────────────


def coz(hedef: str, hata: str, kod: str = "", dosya_yolu: str = "") -> dict:
    """Tek çağrılık self-heal."""
    return SelfHeal().coz(hedef, hata, kod, dosya_yolu)


def script_coz(script_path: str, hata_cikti: str) -> dict:
    """Motor.script_calistir için kolaylık fonksiyonu."""
    return SelfHeal().script_coz(script_path, hata_cikti)


def istatistik_al() -> dict:
    """Küresel istatistik (yoksa boş döndür)."""
    try:
        return SelfHeal().istatistik()
    except Exception:
        return {"hata": "SelfHeal henüz çalışmadı"}
