# -*- coding: utf-8 -*-
"""
credential_pool.py — ReYMeN Kimlik Havuzu (CredentialPool).

Provider adina gore API anahtari havuzu yonetir.
Kaynak sirasi (sonraki oncekini ezer):
  1. .env dosyasi (python-dotenv ile otomatik yukleme)
  2. os.environ (sistem ortam degiskenleri)
  3. CredentialPersistence (Windows Credential Manager / sifrelenmis dosya)

Her provider icin birden fazla API key destegi:
  - <PROVIDER>_API_KEY           -> 1. key
  - <PROVIDER>_API_KEY_2         -> 2. key
  - <PROVIDER>_API_KEY_3         -> 3. key (devam eder)

HTTP 401/402/403 hatalarinda mark_invalid() cagrilir,
havuzdaki sonraki gecerli key'e otomatik gecilir.

Thread-safe: tum kritik metodlar threading.Lock ile korunur.
Kalicilik: ~/.ReYMeN/credential_pool.json dosyasinda hangi
key'lerin gecersiz oldugu saklanir.
"""

from __future__ import annotations

import json
import logging
import os
import threading
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

# ── Sabitler ────────────────────────────────────────────────────────
_PROJE_KOKU = Path(__file__).resolve().parent.parent.parent  # reymen/core/ -> reymen/ -> proje
_POOL_DOSYASI = _PROJE_KOKU / ".ReYMeN" / "credential_pool.json"
_MAX_KEY_INDEX = 10  # provider basina en fazla bu kadar key tara

# Env var adi olusturma sabiti
_API_KEY_SUFFIX = "API_KEY"


def _env_adi(provider: str, index: int = 1) -> str:
    """Provider ve index'e gore environment variable adi olusturur.

    Ornek:
        _env_adi("deepseek")       -> "DEEPSEEK_API_KEY"
        _env_adi("deepseek", 2)    -> "DEEPSEEK_API_KEY_2"
        _env_adi("openai-api")     -> "OPENAI_API_KEY"
    """
    normalized = provider.upper().replace("-", "_").replace(" ", "_")
    if index <= 1:
        return f"{normalized}_{_API_KEY_SUFFIX}"
    return f"{normalized}_{_API_KEY_SUFFIX}_{index}"


# ═══════════════════════════════════════════════════════════════════
# CredentialPool — Kimlik Havuzu Yoneticisi
# ═══════════════════════════════════════════════════════════════════

class CredentialPool:
    """Provider adina gore API anahtari havuzu.

    Havuz su kaynaklardan beslenir (oncelik sirasiyla):
      1. .env dosyasi (python-dotenv ile yuklenir)
      2. os.environ (sistem ortam degiskenleri)
      3. CredentialPersistence (WCM / sifrelenmis dosya)

    Her provider icin <PROVIDER>_API_KEY, <PROVIDER>_API_KEY_2, ...
    seklinde birden fazla anahtar taranir. Gecersiz key'ler
    JSON dosyasinda kalici olarak saklanir.

    Kullanim:
        pool = CredentialPool()

        # Mevcut aktif key
        api_key = pool.get("deepseek")

        # Sonraki key'e gec
        pool.rotate("deepseek")

        # Key gecersiz (401/402/403) -> otomatik rotate
        pool.mark_invalid("deepseek")

    Thread-safe: tum public metodlar Lock ile korunur.
    """

    def __init__(
        self,
        pool_dosyasi: Optional[Path] = None,
        dotenv_yukle: bool = True,
        credential_persistence: Optional[Any] = None,
    ):
        """
        Args:
            pool_dosyasi:   Gecersiz key kaydi icin JSON dosya yolu.
                            Varsayilan: <.ReYMeN/credential_pool.json>
            dotenv_yukle:   .env dosyasini python-dotenv ile otomatik
                            yukle (varsayilan: True)
            credential_persistence:
                            CredentialPersistence ornegi (None = kullanma)
        """
        self._lock = threading.Lock()
        self._pool_dosyasi = pool_dosyasi or _POOL_DOSYASI
        self._cred_persistence = credential_persistence

        # provider -> { "keys": [...], "aktif_index": int, "invalid_set": set(...) }
        self._havuz: dict[str, dict[str, Any]] = {}

        # .env dosyasini yukle
        if dotenv_yukle:
            self._dotenv_yukle()

        # Gecersiz key kayitlarini yukle
        self._gecersizleri_yukle()

        logger.debug(
            "[CredentialPool] Baslatildi (dosya: %s)",
            self._pool_dosyasi,
        )

    # ── .env Yukleme ─────────────────────────────────────────────

    @staticmethod
    def _dotenv_yukle() -> None:
        """Proje kokundeki .env dosyasini python-dotenv ile yukler."""
        env_yolu = _PROJE_KOKU / ".env"
        if not env_yolu.exists():
            logger.debug("[CredentialPool] .env dosyasi bulunamadi: %s", env_yolu)
            return
        try:
            from dotenv import load_dotenv

            load_dotenv(dotenv_path=env_yolu, override=False)
            logger.debug("[CredentialPool] .env yuklendi: %s", env_yolu)
        except ImportError:
            logger.warning(
                "[CredentialPool] python-dotenv yuklu degil, .env atlaniyor."
            )
        except Exception as exc:
            logger.warning(
                "[CredentialPool] .env yuklenemedi: %s", exc
            )

    # ── Gecersiz Key Kaliciligi ─────────────────────────────────

    def _gecersizleri_yukle(self) -> None:
        """JSON dosyasindan gecersiz key kayitlarini yukler."""
        if not self._pool_dosyasi.exists():
            return
        try:
            veri = json.loads(self._pool_dosyasi.read_text(encoding="utf-8"))
            for provider, kayit in veri.items():
                invalid_keys = set(kayit.get("invalid_keys", []))
                if invalid_keys:
                    # Havuzda varsa invalid_set'i guncelle
                    if provider in self._havuz:
                        self._havuz[provider]["invalid_set"].update(invalid_keys)
                    else:
                        # Henuz yuklenmemis; dummy bir kayit olustur
                        self._havuz[provider] = {
                            "keys": [],
                            "aktif_index": 0,
                            "invalid_set": invalid_keys,
                        }
            logger.debug(
                "[CredentialPool] Gecersiz key kayitlari yuklendi: %s",
                self._pool_dosyasi,
            )
        except Exception as exc:
            logger.warning(
                "[CredentialPool] Gecersiz key dosyasi okunamadi: %s", exc
            )

    def _gecersizleri_kaydet(self) -> None:
        """Gecersiz key kumesini JSON dosyasina yazar."""
        try:
            veri: dict[str, Any] = {}
            for provider, kayit in self._havuz.items():
                invalid_keys = list(kayit["invalid_set"])
                if invalid_keys:
                    veri[provider] = {"invalid_keys": invalid_keys}

            self._pool_dosyasi.parent.mkdir(parents=True, exist_ok=True)
            self._pool_dosyasi.write_text(
                json.dumps(veri, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except Exception as exc:
            logger.warning(
                "[CredentialPool] Gecersiz key dosyasi yazilamadi: %s", exc
            )

    # ── Key Tarama ──────────────────────────────────────────────

    def _provider_keyleri_tara(self, provider: str) -> list[str]:
        """Bir provider icin tum kaynaklardan key'leri toplar.

        Kaynak sirasi (sonraki oncekini ezer):
          1. os.environ (onceden .env yuklenmisse o da burada gorunur)
          2. CredentialPersistence (WCM)

        <PROVIDER>_API_KEY, <PROVIDER>_API_KEY_2, ... seklinde
        _MAX_KEY_INDEX'e kadar taranir.

        Returns:
            Benzersiz anahtar listesi (bossuz, sirali)
        """
        gorulen: set[str] = set()
        keys: list[str] = []

        for i in range(1, _MAX_KEY_INDEX + 1):
            env_adi = _env_adi(provider, i)

            # 1. os.environ
            env_val = os.environ.get(env_adi, "")
            if env_val and env_val not in gorulen:
                gorulen.add(env_val)
                keys.append(env_val)
                continue

            # 2. CredentialPersistence (WCM)
            if self._cred_persistence is not None:
                try:
                    wcm_val = self._cred_persistence.wcm_oku(env_adi)
                    if wcm_val and wcm_val not in gorulen:
                        gorulen.add(wcm_val)
                        keys.append(wcm_val)
                except Exception:
                    pass

        if not keys:
            logger.debug(
                "[CredentialPool] '%s' icin hicbir API anahtari bulunamadi.",
                provider,
            )
        else:
            logger.debug(
                "[CredentialPool] '%s' icin %d anahtar bulundu.",
                provider,
                len(keys),
            )

        return keys

    def _havuzu_hazirla(self, provider: str) -> dict[str, Any]:
        """Provider icin havuz kaydini hazirla (yoksa olustur).

        Thread-safe degildir; cagri oncesinde lock alinmalidir.
        """
        if provider not in self._havuz:
            keys = self._provider_keyleri_tara(provider)
            self._havuz[provider] = {
                "keys": keys,
                "aktif_index": 0,
                "invalid_set": set(),
            }

        kayit = self._havuz[provider]

        # Keys henuz taranmamissa veya bossa tekrar dene
        if not kayit["keys"]:
            keys = self._provider_keyleri_tara(provider)
            kayit["keys"] = keys
            kayit["aktif_index"] = 0

        return kayit

    def _gecerli_anahtari_bul(self, kayit: dict[str, Any]) -> Optional[str]:
        """Kayittaki gecerli ilk aktif key'i bulur.

        Gecersiz key'leri atlayarak siradaki gecerli key'i doner.
        Eger hic gecerli key yoksa None doner.

        Thread-safe degildir; cagri oncesinde lock alinmalidir.
        """
        keys = kayit["keys"]
        invalid = kayit["invalid_set"]
        baslangic = kayit["aktif_index"]

        for offset in range(len(keys)):
            idx = (baslangic + offset) % len(keys)
            key = keys[idx]
            if key not in invalid:
                kayit["aktif_index"] = idx
                return key

        # Tum key'ler gecersiz
        return None

    # ── Public API ──────────────────────────────────────────────

    def get(self, provider: str) -> Optional[str]:
        """Provider icin mevcut aktif API anahtarini dondurur.

        Havuz henuz olusturulmamissa otomatik taranir.
        Gecersiz key'ler atlanir; hic gecerli key yoksa None doner.

        Args:
            provider: Provider adi (ornek: "deepseek", "openai-api")

        Returns:
            API anahtari (string) veya None
        """
        with self._lock:
            kayit = self._havuzu_hazirla(provider)
            return self._gecerli_anahtari_bul(kayit)

    def rotate(self, provider: str) -> Optional[str]:
        """Sonraki API anahtarina gecer.

        Mevcut aktif index bir ileri alinir, ardindan gecerli
        key bulunup dondurulur.

        Args:
            provider: Provider adi

        Returns:
            Yeni aktif API anahtari veya None (hic gecerli key yoksa)
        """
        with self._lock:
            kayit = self._havuzu_hazirla(provider)

            if not kayit["keys"]:
                logger.warning(
                    "[CredentialPool] '%s' icin rotate imkansiz (key yok).",
                    provider,
                )
                return None

            # Bir sonraki index'e gec
            kayit["aktif_index"] = (kayit["aktif_index"] + 1) % len(kayit["keys"])
            anahtar = self._gecerli_anahtari_bul(kayit)

            if anahtar is None:
                logger.warning(
                    "[CredentialPool] '%s' icin tum key'ler gecersiz, rotate basarisiz.",
                    provider,
                )
            else:
                logger.info(
                    "[CredentialPool] '%s' rotate -> index %d",
                    provider,
                    kayit["aktif_index"],
                )

            return anahtar

    def mark_invalid(self, provider: str) -> Optional[str]:
        """Mevcut aktif API anahtarini gecersiz isaretler ve rotate yapar.

    401/402/403 hata alindiginda cagrilmalidir.

        Args:
            provider: Provider adi

        Returns:
            Yeni gecerli API anahtari veya None
            (yeni key yoksa veya tumu gecersizse)
        """
        with self._lock:
            kayit = self._havuzu_hazirla(provider)

            if not kayit["keys"]:
                logger.warning(
                    "[CredentialPool] '%s' mark_invalid imkansiz (key yok).",
                    provider,
                )
                return None

            mevcut_idx = kayit["aktif_index"]
            if mevcut_idx < len(kayit["keys"]):
                eski_key = kayit["keys"][mevcut_idx]
                kayit["invalid_set"].add(eski_key)
                logger.info(
                    "[CredentialPool] '%s' key gecersiz isaretlendi: ...%s",
                    provider,
                    eski_key[-8:] if len(eski_key) > 8 else eski_key,
                )

                # Kalici kaydet
                self._gecersizleri_kaydet()

            # Rotate yap (gecersiz olmayan sonraki key'e gec)
            kayit["aktif_index"] = (mevcut_idx + 1) % len(kayit["keys"])
            yeni_key = self._gecerli_anahtari_bul(kayit)

            if yeni_key is None:
                logger.warning(
                    "[CredentialPool] '%s' tum key'ler gecersiz!",
                    provider,
                )
            else:
                logger.info(
                    "[CredentialPool] '%s' yeni aktif key index: %d",
                    provider,
                    kayit["aktif_index"],
                )

            return yeni_key

    def list_keys(self, provider: str) -> list[str]:
        """Provider icin havuzdaki tum anahtarlari listeler (sadece okuma).

        Hangi key'lerin gecerli/gecersiz oldugunu gormek icin kullanilir.

        Args:
            provider: Provider adi

        Returns:
            API anahtarlari listesi (maskelenmemis)
        """
        with self._lock:
            kayit = self._havuzu_hazirla(provider)
            return list(kayit["keys"])

    def durum(self, provider: Optional[str] = None) -> str:
        """Havuzun su anki durumunu raporlar.

        Args:
            provider: Belli bir provider'a ozgu durum (None = tumu)

        Returns:
            Okunabilir durum metni
        """
        with self._lock:
            satirlar: list[str] = []
            if provider:
                providers = [provider] if provider in self._havuz else []
            else:
                providers = list(self._havuz.keys())

            if not providers:
                return "[CredentialPool] Havuzda kayitli provider yok."

            for p in providers:
                kayit = self._havuz.get(p)
                if not kayit:
                    satirlar.append(f"  {p}: (henuz taranmadi)")
                    continue
                toplam = len(kayit["keys"])
                gecersiz = len(kayit["invalid_set"])
                gecerli = toplam - gecersiz
                aktif_idx = kayit["aktif_index"]
                aktif_key = self._gecerli_anahtari_bul(
                    kayit
                )  # lock icindeyiz, sorun yok

                aktif_mask = (
                    f"...{aktif_key[-8:]}"
                    if aktif_key and len(aktif_key) > 8
                    else str(aktif_key)
                )

                satirlar.append(
                    f"  {p}: {toplam} key ({gecerli} gecerli, "
                    f"{gecersiz} gecersiz) | aktif index={aktif_idx} | "
                    f"aktif={aktif_mask}"
                )

            return "[CredentialPool] Havuz Durumu:\n" + "\n".join(satirlar)

    def reload(self, provider: Optional[str] = None) -> None:
        """Provider key'lerini yeniden tara (ornegin .env degistiğinde).

        Args:
            provider: Belli bir provider (None = tumunu yeniden yukle)
        """
        with self._lock:
            if provider:
                keys = self._provider_keyleri_tara(provider)
                if provider in self._havuz:
                    self._havuz[provider]["keys"] = keys
                    self._havuz[provider]["aktif_index"] = 0
                else:
                    self._havuz[provider] = {
                        "keys": keys,
                        "aktif_index": 0,
                        "invalid_set": set(),
                    }
                logger.info(
                    "[CredentialPool] '%s' yeniden tarandi: %d key",
                    provider,
                    len(keys),
                )
            else:
                # Tum provider'lari yeniden tara
                for p in list(self._havuz.keys()):
                    keys = self._provider_keyleri_tara(p)
                    self._havuz[p]["keys"] = keys
                    self._havuz[p]["aktif_index"] = 0
                logger.info(
                    "[CredentialPool] Tum provider'lar yeniden tarandi."
                )


# ── Modul seviyesinde yardimci ──────────────────────────────────────

_global_pool: Optional[CredentialPool] = None
_global_pool_lock = threading.Lock()


def get_credential_pool(
    dotenv_yukle: bool = True,
    credential_persistence: Optional[Any] = None,
) -> CredentialPool:
    """Modul seviyesinde tekil (singleton) CredentialPool ornegi doner.

    Args:
        dotenv_yukle:   .env dosyasini yukle (varsayilan: True)
        credential_persistence:
                        CredentialPersistence ornegi

    Returns:
        CredentialPool ornegi
    """
    global _global_pool
    if _global_pool is None:
        with _global_pool_lock:
            if _global_pool is None:
                _global_pool = CredentialPool(
                    dotenv_yukle=dotenv_yukle,
                    credential_persistence=credential_persistence,
                )
    return _global_pool
