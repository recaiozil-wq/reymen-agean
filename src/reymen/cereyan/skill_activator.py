# -*- coding: utf-8 -*-
"""
skill_activator.py â€” Otomatik skill aktivasyon motoru.

Gelen sorguya göre ilgili skill'leri otomatik bulup aktif hale getirir.
SkillActivator sÄ±nÄ±fÄ±:
- aktif_et / devre_disina_al: Skill aktivasyon kontrolü
- sorgudan_aktif_et: Gelen sorgudaki kelimeleri skill etiketleriyle eÅŸleÅŸtir
- durum: Aktif skill listesi

KullanÄ±m:
    from skill_activator import SkillActivator
    act = SkillActivator()
    aktif_idler = act.sorgudan_aktif_et("ag izleme ve port tarama")
    print(act.durum())
"""

from __future__ import annotations

import logging
import re
import sqlite3
import threading
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any

from reymen.cereyan.skill_library import SkillLibrary, _yazma_kilit

logger = logging.getLogger(__name__)

# â”€â”€ VarsayÄ±lan yollar â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
ROOT = Path(__file__).parent.resolve()
DB_YOLU = ROOT / ".ReYMeN" / "skill_library.db"


@contextmanager
def _baglanti():
    con = sqlite3.connect(str(DB_YOLU), timeout=15, check_same_thread=False)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA journal_mode=WAL")
    con.execute("PRAGMA synchronous=NORMAL")
    try:
        yield con
        con.commit()
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()


# â”€â”€ YardÄ±mcÄ±: Anahtar Kelime Ã‡Ä±karma â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

TURKCE_KARAKTER_MAP = {
    "Ä±": "i",
    "Ä°": "i",
    "ÄŸ": "g",
    "Ä": "g",
    "ü": "u",
    "Ãœ": "u",
    "ÅŸ": "s",
    "Å": "s",
    "ö": "o",
    "Ã–": "o",
    "ç": "c",
    "Ã‡": "c",
}

STOP_KELIMELER: set[str] = {
    "bir",
    "bu",
    "ve",
    "veya",
    "ile",
    "için",
    "ile",
    "ama",
    "fakat",
    "lakin",
    "veya",
    "ya",
    "da",
    "de",
    "mi",
    "mu",
    "mÄ±",
    "mu",
    "nÄ±",
    "ni",
    "nu",
    "nü",
    "en",
    "çok",
    "daha",
    "biraz",
    "hiç",
    "tüm",
    "her",
    "olan",
    "olduÄŸu",
    "olacak",
    "yap",
    "yapma",
    "nasÄ±l",
    "ne",
    "nerede",
    "neden",
    "hangi",
    "kim",
    "ben",
    "sen",
    "o",
    "biz",
    "siz",
    "onlar",
    "beni",
    "seni",
    "bizi",
    "sizi",
    "onlarÄ±",
    "benim",
    "senin",
    "bizim",
    "sizin",
    "onun",
    "ÅŸu",
    "ÅŸunu",
    "ÅŸuna",
    "bunu",
    "buna",
}

TURKCE_KOK_MAP = {
    # Fiil kökleri
    "izleme": "izle",
    "izler": "izle",
    "izledi": "izle",
    "tarama": "tara",
    "tarar": "tara",
    "taradÄ±": "tara",
    "yönetme": "yonet",
    "yönetir": "yonet",
    "yönetimi": "yonet",
    "kontrol": "kontrol",
    "kontrolü": "kontrol",
    "kontrol et": "kontrol",
    "güvenlik": "guvenlik",
    "güvenli": "guvenlik",
    "baÄŸlantÄ±": "baglanti",
    "baÄŸlan": "baglan",
    "baÄŸlantÄ±larÄ±": "baglanti",
    "analiz": "analiz",
    "analizi": "analiz",
    "analiz et": "analiz",
    "rapor": "rapor",
    "raporlama": "rapor",
    "log": "log",
    "loglama": "log",
    "loglarÄ±": "log",
    "kayÄ±t": "kayit",
    "kaydet": "kayit",
    "kayÄ±tlarÄ±": "kayit",
    "dosya": "dosya",
    "dosyalarÄ±": "dosya",
    "veri": "veri",
    "verileri": "veri",
    "sistem": "sistem",
    "sistemi": "sistem",
    "aÄŸ": "ag",
    "aÄŸÄ±": "ag",
    "port": "port",
    "portlarÄ±": "port",
    "servis": "servis",
    "servisleri": "servis",
    "bildirim": "bildirim",
    "bildirimi": "bildirim",
    "uyarÄ±": "uyari",
    "uyar": "uyari",
    "uyarÄ±larÄ±": "uyari",
    "otomatik": "otomatik",
    "oto": "otomatik",
    "zaman": "zaman",
    "zamanlÄ±": "zaman",
    "görev": "gorev",
    "görevi": "gorev",
    "plan": "plan",
    "planlama": "plan",
    "yedek": "yedek",
    "yedekleme": "yedek",
    "ÅŸifre": "sifre",
    "ÅŸifreleme": "sifre",
    "ÅŸifreli": "sifre",
    "kimlik": "kimlik",
    "kimlik doÄŸrulama": "kimlik",
    "yetki": "yetki",
    "yetkilendirme": "yetki",
    "izin": "izin",
    "izinler": "izin",
    "eriÅŸim": "erisim",
    "eriÅŸimi": "erisim",
    "proxy": "proxy",
    "proxy ayarlarÄ±": "proxy",
    "dns": "dns",
    "dns sorgu": "dns",
    "cache": "cache",
    "önbellek": "cache",
    "monitör": "monitor",
    "monitörü": "monitor",
    "performans": "performans",
    "optimizasyon": "optimizasyon",
}


def _anahtar_kelimeler(metin: str) -> list[str]:
    """
    Metni normalize et ve anlamlÄ± anahtar kelimelere ayÄ±r.

    - Türkçe karakterleri ASCII'ye çevir
    - Noktalama iÅŸaretlerini temizle
    - Stop kelimeleri çÄ±kar
    - Kök bulma uygula
    """
    if not metin or not metin.strip():
        return []

    temiz = metin.lower().strip()

    # Türkçe karakter normalize
    for tr, ascii_karsilik in TURKCE_KARAKTER_MAP.items():
        temiz = temiz.replace(tr, ascii_karsilik)

    # Noktalama iÅŸaretlerini kaldÄ±r
    for ch in '.,!?;:()[]{}"\'"`â€â€œâ€˜â€™â€¦â€“â€“/\\|@#$%^&*+=<>~':
        temiz = temiz.replace(ch, " ")

    # Kelimelere ayÄ±r, kÄ±sa ve stop kelimeleri çÄ±kar
    ham_kelimeler = [k for k in temiz.split() if len(k) > 1]

    # Stop kelimeleri çÄ±kar
    anlamli = [k for k in ham_kelimeler if k not in STOP_KELIMELER]

    # Kök bulma (eÄŸer varsa)
    kokler = []
    for k in anlamli:
        if k in TURKCE_KOK_MAP:
            kokler.append(TURKCE_KOK_MAP[k])
        else:
            kokler.append(k)

    # Benzersiz yap
    gorulen: set[str] = set()
    sonuc = []
    for k in kokler:
        if k not in gorulen:
            gorulen.add(k)
            sonuc.append(k)

    return sonuc


def _eslesme_skoru(
    sorgu_kelimeleri: list[str], skill_etiketleri: list[str], skill_baslik: str
) -> float:
    """
    Sorgu kelimeleri ile skill etiketleri arasÄ±ndaki eÅŸleÅŸme skorunu hesapla.

    3 faktör:
    1. DoÄŸrudan etiket eÅŸleÅŸmesi (en yüksek aÄŸÄ±rlÄ±k)
    2. BaÅŸlÄ±k eÅŸleÅŸmesi (orta aÄŸÄ±rlÄ±k)
    3. KÄ±smi eÅŸleÅŸme (düÅŸük aÄŸÄ±rlÄ±k)

    Returns:
        0.0 - 1.0 arasÄ± skor
    """
    if not sorgu_kelimeleri:
        return 0.0

    # Etiketleri normalize et
    etiket_normalized = []
    for et in skill_etiketleri:
        et_clean = et.lower().strip()
        for tr, ascii_karsilik in TURKCE_KARAKTER_MAP.items():
            et_clean = et_clean.replace(tr, ascii_karsilik)
        etiket_normalized.append(et_clean)

    # BaÅŸlÄ±ÄŸÄ± normalize et
    baslik_normalized = skill_baslik.lower().strip()
    for tr, ascii_karsilik in TURKCE_KARAKTER_MAP.items():
        baslik_normalized = baslik_normalized.replace(tr, ascii_karsilik)
    baslik_kelimeler = set(
        k for k in re.split(r"[\s\-_/]+", baslik_normalized) if len(k) > 1
    )

    toplam_kelime = len(sorgu_kelimeleri)
    if toplam_kelime == 0:
        return 0.0

    # 1) DoÄŸrudan etiket eÅŸleÅŸmesi (aÄŸÄ±rlÄ±k: 0.5)
    etiket_eslesen = 0
    for sk in sorgu_kelimeleri:
        for et in etiket_normalized:
            if sk == et or (len(sk) > 2 and sk in et) or (len(et) > 2 and et in sk):
                etiket_eslesen += 1
                break

    etiket_skor = etiket_eslesen / toplam_kelime if toplam_kelime > 0 else 0.0

    # 2) BaÅŸlÄ±k eÅŸleÅŸmesi (aÄŸÄ±rlÄ±k: 0.3)
    baslik_eslesen = 0
    for sk in sorgu_kelimeleri:
        if sk in baslik_kelimeler:
            baslik_eslesen += 1
        elif any(sk in bk or bk in sk for bk in baslik_kelimeler if len(sk) > 2):
            baslik_eslesen += 0.5

    baslik_skor = baslik_eslesen / toplam_kelime if toplam_kelime > 0 else 0.0

    # 3) KÄ±smi eÅŸleÅŸme (aÄŸÄ±rlÄ±k: 0.2)
    # Sorgudaki her kelimenin etiket veya baÅŸlÄ±kta bir kÄ±smÄ±nÄ±n geçip geçmediÄŸine bakar
    kismi_eslesen = 0
    for sk in sorgu_kelimeleri:
        # 3 karakterden kÄ±sa kelimeler için en az 2 karakter eÅŸleÅŸmeli
        min_eslesme = 2 if len(sk) <= 3 else 3
        for et in etiket_normalized + list(baslik_kelimeler):
            # En uzun ortak alt dize yaklaÅŸÄ±mÄ±
            if len(sk) >= min_eslesme and len(et) >= min_eslesme:
                # Karakter bazÄ±nda ortaklÄ±k
                ortak = sum(1 for c in sk if c in et)
                if ortak >= min_eslesme:
                    kismi_eslesen += 1
                    break

    kismi_skor = kismi_eslesen / toplam_kelime if toplam_kelime > 0 else 0.0

    # Toplam skor [0.0, 1.0]
    skor = etiket_skor * 0.5 + baslik_skor * 0.3 + kismi_skor * 0.2
    return min(skor, 1.0)


# â”€â”€ SkillActivator SÄ±nÄ±fÄ± â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


class SkillActivator:
    """
    Otomatik skill aktivasyon motoru.

    Gelen sorguya göre ilgili skill'leri otomatik bulup aktif eder.
    SkillLibrary ile birlikte çalÄ±ÅŸÄ±r; tüm skill verileri ortak DB'de saklanÄ±r.
    """

    def __init__(self, db_yolu: str | Path | None = None):
        """
        Args:
            db_yolu: VeritabanÄ± yolu (None = varsayÄ±lan)
        """
        self._db_yolu = Path(db_yolu) if db_yolu else DB_YOLU
        self._lib = SkillLibrary(str(self._db_yolu))
        self._aktif_cache: dict[str, dict[str, Any]] | None = None

    # â”€â”€ Dahili â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def _temizle_cache(self):
        """Aktif skill önbelleÄŸini temizle."""
        self._aktif_cache = None

    def _aktif_liste(self) -> dict[str, dict[str, Any]]:
        """Aktif skill'leri cache'li ÅŸekilde döndür."""
        if self._aktif_cache is None:
            aktifler = self._lib.tumu(aktif_mi=True, limit=500)
            self._aktif_cache = {s["id"]: s for s in aktifler}
        return self._aktif_cache

    # â”€â”€ Aktif Et â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def aktif_et(self, skill_id: str) -> bool:
        """
        Skill'i aktif moda geçir (OnceHafiza'ya ekle).

        Skill'in 'aktif' alanÄ±nÄ± 1 yapar.

        Args:
            skill_id: Aktif edilecek skill ID'si

        Returns:
            True (baÅŸarÄ±lÄ±) / False (skill bulunamadÄ±)
        """
        if not skill_id:
            return False

        # Skill var mÄ± kontrol et
        skill = self._lib.get(skill_id)
        if not skill:
            logger.warning("[Activator] Skill bulunamadi: %s", skill_id)
            return False

        if skill["aktif"]:
            logger.debug("[Activator] Zaten aktif: %s", skill_id)
            return True

        # Aktif yap
        with _yazma_kilit:
            con = sqlite3.connect(str(self._db_yolu), timeout=15)
            con.execute("PRAGMA journal_mode=WAL")
            try:
                con.execute(
                    "UPDATE skills SET aktif = 1, son_guncelleme = datetime('now') WHERE id = ?",
                    (skill_id,),
                )
                con.commit()
                self._temizle_cache()
                logger.info(
                    "[Activator] Aktif edildi: %s (%s)", skill_id, skill["baslik"][:40]
                )
                return True
            except Exception as e:
                con.rollback()
                logger.warning("[Activator] Aktif etme hatasi [%s]: %s", skill_id, e)
                return False
            finally:
                con.close()

    # â”€â”€ Devre DÄ±ÅŸÄ±na Al â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def devre_disina_al(self, skill_id: str) -> bool:
        """
        Skill'i pasif yap (devre dÄ±ÅŸÄ±).

        Skill'in 'aktif' alanÄ±nÄ± 0 yapar.

        Args:
            skill_id: Pasif edilecek skill ID'si

        Returns:
            True (baÅŸarÄ±lÄ±) / False (skill bulunamadÄ±)
        """
        if not skill_id:
            return False

        skill = self._lib.get(skill_id)
        if not skill:
            logger.warning("[Activator] Skill bulunamadi: %s", skill_id)
            return False

        if not skill["aktif"]:
            logger.debug("[Activator] Zaten pasif: %s", skill_id)
            return True

        with _yazma_kilit:
            con = sqlite3.connect(str(self._db_yolu), timeout=15)
            con.execute("PRAGMA journal_mode=WAL")
            try:
                con.execute(
                    "UPDATE skills SET aktif = 0, son_guncelleme = datetime('now') WHERE id = ?",
                    (skill_id,),
                )
                con.commit()
                self._temizle_cache()
                logger.info(
                    "[Activator] Devre disi: %s (%s)", skill_id, skill["baslik"][:40]
                )
                return True
            except Exception as e:
                con.rollback()
                logger.warning("[Activator] Devre disi hatasi [%s]: %s", skill_id, e)
                return False
            finally:
                con.close()

    # â”€â”€ Sorgudan Otomatik Aktif Et â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def sorgudan_aktif_et(
        self, sorgu: str, max_aktif: int = 3, min_skor: float = 0.15
    ) -> list[str]:
        """
        Gelen sorguya göre ilgili skill'leri otomatik bul ve aktif et.

        AkÄ±ÅŸ:
        1. Sorguyu anahtar kelimelere ayÄ±r
        2. Tüm skill'lerle eÅŸleÅŸme skoru hesapla
        3. En çok eÅŸleÅŸen max_aktif skill'i aktif et
        4. Ã–nceden aktif olup eÅŸleÅŸmeyenleri pasif yapma (sadece ekle)

        Args:
            sorgu: KullanÄ±cÄ± sorgusu (örn. "ag izleme ve port tarama")
            max_aktif: Maksimum aktif edilecek skill sayÄ±sÄ±
            min_skor: Minimum eÅŸleÅŸme skoru eÅŸiÄŸi

        Returns:
            Aktif edilen skill ID'lerinin listesi
        """
        if not sorgu or not sorgu.strip():
            logger.debug("[Activator] Bos sorgu, islem yapilmadi.")
            return []

        # Sorguyu anahtar kelimelere ayÄ±r
        kelimeler = _anahtar_kelimeler(sorgu)
        if not kelimeler:
            logger.debug("[Activator] Sorgudan anlamli kelime cikmadi: %s", sorgu[:40])
            return []

        logger.debug("[Activator] Sorgu kelimeleri: %s", kelimeler)

        # Tüm skill'leri getir (aktif/pasif fark etmez)
        tum_skills = self._lib.tumu(aktif_mi=None, limit=1000)
        if not tum_skills:
            logger.debug("[Activator] Kutuphanede skill yok.")
            return []

        # Her skill için eÅŸleÅŸme skoru hesapla
        skorlu: list[tuple[float, dict[str, Any]]] = []
        for skill in tum_skills:
            skor = _eslesme_skoru(kelimeler, skill["etiketler"], skill["baslik"])
            if skor >= min_skor:
                skorlu.append((skor, skill))

        # Skora göre sÄ±rala (en yüksekten düÅŸüÄŸe)
        skorlu.sort(key=lambda x: x[0], reverse=True)

        if not skorlu:
            logger.debug(
                "[Activator] Eslesen skill bulunamadi (min_skor=%.2f).", min_skor
            )
            return []

        # En iyi sonuçlarÄ± logla
        logger.info(
            "[Activator] En iyi eslesmeler: %s",
            ", ".join(f"{s['id']}({skor:.2f})" for skor, s in skorlu[:5]),
        )

        # En çok eÅŸleÅŸenleri aktif et (zaten aktif olanlarÄ± atla)
        aktif_edilen: list[str] = []
        for skor, skill in skorlu[:max_aktif]:
            if not skill["aktif"]:
                if self.aktif_et(skill["id"]):
                    aktif_edilen.append(skill["id"])
                    logger.info(
                        "[Activator] Sorgudan aktif: %s (skor=%.2f, etiket=%s)",
                        skill["id"],
                        skor,
                        skill["etiketler"],
                    )
            else:
                logger.debug(
                    "[Activator] Zaten aktif, atla: %s (skor=%.2f)", skill["id"], skor
                )

        return aktif_edilen

    # â”€â”€ Durum â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def durum(self) -> list[dict[str, Any]]:
        """
        Aktif skill listesini döndür.

        Returns:
            [{"id", "baslik", "icerik_ozeti", "etiketler", "kaynak", ...}, ...]
        """
        aktifler = self._lib.tumu(aktif_mi=True, limit=500)
        return aktifler

    # â”€â”€ Tüm Skill'leri Aktif/Pasif Yap â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def tumunu_aktif_et(self) -> int:
        """Tüm skill'leri aktif yap. Kaç tane aktif edildiÄŸini döndür."""
        pasifler = self._lib.tumu(aktif_mi=False, limit=1000)
        sayac = 0
        for skill in pasifler:
            if self.aktif_et(skill["id"]):
                sayac += 1
        logger.info("[Activator] Toplu aktif: %d skill aktif edildi.", sayac)
        return sayac

    def tumunu_pasif_yap(self) -> int:
        """Tüm skill'leri pasif yap. Kaç tane pasif edildiÄŸini döndür."""
        aktifler = self._lib.tumu(aktif_mi=True, limit=1000)
        sayac = 0
        for skill in aktifler:
            if self.devre_disina_al(skill["id"]):
                sayac += 1
        logger.info("[Activator] Toplu pasif: %d skill pasif edildi.", sayac)
        return sayac

    # â”€â”€ Sorgu Ã–nerisi / Tahmin â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def sorgu_tahmin(self, sorgu: str, limit: int = 5) -> list[dict[str, Any]]:
        """
        Sorguya en çok benzeyen skill'leri tahmin et (aktif etmeden).

        Args:
            sorgu: KullanÄ±cÄ± sorgusu
            limit: Maksimum tahmin sayÄ±sÄ±

        Returns:
            [{"id", "baslik", "etiketler", "skor", ...}, ...]
        """
        kelimeler = _anahtar_kelimeler(sorgu)
        if not kelimeler:
            return []

        tum_skills = self._lib.tumu(aktif_mi=None, limit=1000)

        skorlu: list[tuple[float, dict[str, Any]]] = []
        for skill in tum_skills:
            skor = _eslesme_skoru(kelimeler, skill["etiketler"], skill["baslik"])
            if skor > 0:
                skorlu.append((skor, skill))

        skorlu.sort(key=lambda x: x[0], reverse=True)

        return [
            {
                "id": s["id"],
                "baslik": s["baslik"],
                "etiketler": s["etiketler"],
                "kaynak": s["kaynak"],
                "skor": round(skor, 2),
                "aktif": s["aktif"],
            }
            for skor, s in skorlu[:limit]
        ]

    # â”€â”€ Ä°statistik â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def istatistik(self) -> dict[str, Any]:
        """Aktivasyon istatistikleri."""
        lib_stat = self._lib.istatistik()
        aktifler = self._lib.tumu(aktif_mi=True, limit=500)

        # Aktif skill'lerin etiket daÄŸÄ±lÄ±mÄ±
        etiket_sayaci: dict[str, int] = {}
        for s in aktifler:
            for et in s["etiketler"]:
                etiket_sayaci[et] = etiket_sayaci.get(et, 0) + 1

        en_cok_etiket = sorted(etiket_sayaci.items(), key=lambda x: x[1], reverse=True)[
            :10
        ]

        return {
            "toplam_skill": lib_stat["toplam"],
            "aktif_skill": lib_stat["aktif"],
            "pasif_skill": lib_stat["pasif"],
            "en_cok_kullanilan_etiketler": dict(en_cok_etiket),
        }


# â”€â”€ Modül seviyesinde singleton â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
_activator: SkillActivator | None = None


def get_activator(db_yolu: str | Path | None = None) -> SkillActivator:
    """Singleton SkillActivator örneÄŸi al."""
    global _activator
    if _activator is None:
        _activator = SkillActivator(db_yolu)
    return _activator


# â”€â”€ Kolay kullanÄ±m fonksiyonlarÄ± â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


def aktif_et(skill_id: str) -> bool:
    """Skill aktif et (kolay kullanÄ±m)."""
    return get_activator().aktif_et(skill_id)


def devre_disina_al(skill_id: str) -> bool:
    """Skill pasif et (kolay kullanÄ±m)."""
    return get_activator().devre_disina_al(skill_id)


def sorgudan_aktif_et(
    sorgu: str, max_aktif: int = 3, min_skor: float = 0.15
) -> list[str]:
    """Sorgudan otomatik aktif et (kolay kullanÄ±m)."""
    return get_activator().sorgudan_aktif_et(sorgu, max_aktif, min_skor)


def durum() -> list[dict[str, Any]]:
    """Aktif skill listesi (kolay kullanÄ±m)."""
    return get_activator().durum()


def sorgu_tahmin(sorgu: str, limit: int = 5) -> list[dict[str, Any]]:
    """Sorgu tahmini (kolay kullanÄ±m)."""
    return get_activator().sorgu_tahmin(sorgu, limit)


def motor_kaydet(motor) -> None:
    """Motor'a skill aktivasyon araclarini kaydet."""
    if hasattr(motor, "_plugin_arac_kaydet"):
        motor._plugin_arac_kaydet(
            "SKILL_AKTIF_ET",
            lambda sorgu="": sorgudan_aktif_et(sorgu) if sorgu else [],
            "Sorguya gore skill'leri otomatik aktif et. Parametre: sorgu",
        )
        motor._plugin_arac_kaydet(
            "SKILL_AKTIF_DURUM",
            lambda: durum(),
            "Aktif skill listesi",
        )
        motor._plugin_arac_kaydet(
            "SKILL_PASIF_YAP",
            lambda skill_id="": devre_disina_al(skill_id) if skill_id else False,
            "Skill'i devre disi birak. Parametre: skill_id",
        )
