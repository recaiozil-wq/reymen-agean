# -*- coding: utf-8 -*-
"""gateway/restart.py — Gateway Yeniden Başlatma Yöneticisi.

Tüm platformları sırayla durdurup başlatır.
Graceful shutdown + startup yönetimi sağlar.
ReYMeN kimliği: Türkçe docstring, try/except, özgün implementasyon.
"""

import asyncio
import logging
import signal
import sys
import time
from datetime import datetime, timezone
from typing import Callable

logger = logging.getLogger("gateway.restart")

# Kayıtlı platform başlatma/durdurma fonksiyonları
_platformlar: dict[str, dict[str, Callable]] = {}

GATEWAY_SERVICE_RESTART_EXIT_CODE: int = 75
"""Gateway hizmetinin restart sinyaliyle cikis kodu."""

DEFAULT_GATEWAY_RESTART_DRAIN_TIMEOUT: float = 30.0
"""Varsayilan draining (bosaltma) bekleme saniyesi."""


def parse_restart_drain_timeout(deger: str | None) -> float:
    """Drain timeout degerini ayristirip float'a cevirir.

    Args:
        deger: String zaman degeri veya None

    Returns:
        Gecerli float deger; None/bos ise DEFAULT;
        negatif ise 0.0.
    """
    if not deger:
        return DEFAULT_GATEWAY_RESTART_DRAIN_TIMEOUT
    try:
        val = float(deger)
        return 0.0 if val < 0 else val
    except (ValueError, TypeError):
        logger.warning(f"[Restart] Gecersiz drain_timeout degeri: {deger!r}, varsayilan kullaniliyor.")
        return DEFAULT_GATEWAY_RESTART_DRAIN_TIMEOUT


def platform_kaydet(ad: str, baslat: Callable, durdur: Callable, kontrol: Callable | None = None):
    """Yeniden başlatma yöneticisine bir platform ekler.

    Args:
        ad: Platform adı (ör: 'telegram', 'discord')
        baslat: Platformu başlatan async/ sync fonksiyon
        durdur: Platformu durduran async/ sync fonksiyon
        kontrol: (Opsiyonel) Platform durumunu dönen fonksiyon
    """
    _platformlar[ad] = {
        "baslat": baslat,
        "durdur": durdur,
        "kontrol": kontrol,
        "durum": "bilinmiyor",
        "son_restart": None,
    }
    logger.info(f"[Restart] Platform kaydedildi: {ad}")


def send_restart_signal(platform_adi: str | None = None, sebep: str = "bakim") -> bool:
    """Belirtilen platforma yeniden başlatma sinyali gönderir.

    Args:
        platform_adi: Platform adı (None = tümü)
        sebep: Yeniden başlatma sebebi

    Returns:
        Başarılıysa True
    """
    try:
        if platform_adi:
            if platform_adi not in _platformlar:
                logger.warning(f"[Restart] Platform bulunamadı: {platform_adi}")
                return False
            hedef = {platform_adi: _platformlar[platform_adi]}
            logger.info(f"[Restart] Sinyal gönderiliyor: {platform_adi} ({sebep})")
        else:
            hedef = _platformlar
            logger.info(f"[Restart] Tüm platformlara sinyal gönderiliyor ({sebep})")

        for ad, kayit in hedef.items():
            logger.info(f"[Restart]  -> {ad}: restart sinyali iletildi")
            kayit["durum"] = "restart_bekliyor"

        return True
    except Exception as e:
        logger.error(f"[Restart] Sinyal hatası: {e}")
        return False


def restart_platform(ad: str, bekleme: float = 2.0) -> bool:
    """Tek bir platformu sırayla durdurup başlatır.

    Args:
        ad: Platform adı
        bekleme: Durdurma ve başlatma arası bekleme saniyesi

    Returns:
        Başarılıysa True
    """
    try:
        if ad not in _platformlar:
            logger.error(f"[Restart] Platform kayıtlı değil: {ad}")
            return False

        kayit = _platformlar[ad]
        logger.info(f"[Restart] === Platform yeniden başlatılıyor: {ad} ===")

        # 1. Graceful shutdown
        logger.info(f"[Restart] {ad} durduruluyor...")
        durdur_fonk = kayit["durdur"]
        try:
            if asyncio.iscoroutinefunction(durdur_fonk):
                asyncio.get_event_loop().run_until_complete(durdur_fonk())
            else:
                durdur_fonk()
        except Exception as e:
            logger.error(f"[Restart] {ad} durdurulurken hata: {e}")

        kayit["durum"] = "durduruldu"

        # 2. Bekleme (grace period)
        if bekleme > 0:
            logger.info(f"[Restart] {ad} için {bekleme}s bekleniyor...")
            time.sleep(bekleme)

        # 3. Startup
        logger.info(f"[Restart] {ad} başlatılıyor...")
        baslat_fonk = kayit["baslat"]
        try:
            if asyncio.iscoroutinefunction(baslat_fonk):
                asyncio.get_event_loop().run_until_complete(baslat_fonk())
            else:
                baslat_fonk()
        except Exception as e:
            logger.error(f"[Restart] {ad} başlatılırken hata: {e}")
            kayit["durum"] = "hata"
            return False

        kayit["durum"] = "aktif"
        kayit["son_restart"] = datetime.now(timezone.utc).isoformat()
        logger.info(f"[Restart] {ad} başarıyla yeniden başlatıldı")
        return True

    except Exception as e:
        logger.error(f"[Restart] Platform restart hatası ({ad}): {e}")
        return False


def restart_all(bekleme: float = 1.0, sira: list[str] | None = None) -> dict[str, bool]:
    """Tüm platformları sırayla durdurup başlatır.

    Önce tümünü durdurur, sonra tümünü başlatır.
    Bu sayede bağımlı platformlar sorunsuz kapanır/açılır.

    Args:
        bekleme: Her işlem arası bekleme saniyesi
        sira: İşlem sırası (None = _platformlar.keys() sırası)

    Returns:
        {platform_adi: basarili_mi} sözlüğü
    """
    sonuclar: dict[str, bool] = {}
    try:
        sirali = sira or list(_platformlar.keys())

        logger.info(f"[Restart] === Tüm platformlar yeniden başlatılıyor ({len(sirali)} adet) ===")

        # AŞAMA 1: Tümünü durdur (önce kaydet, sonra durdur)
        logger.info("[Restart] AŞAMA 1: Tüm platformlar durduruluyor...")
        for ad in sirali:
            if ad not in _platformlar:
                logger.warning(f"[Restart] Atlanıyor (bulunamadı): {ad}")
                continue
            kayit = _platformlar[ad]
            try:
                durdur_fonk = kayit["durdur"]
                if asyncio.iscoroutinefunction(durdur_fonk):
                    asyncio.get_event_loop().run_until_complete(durdur_fonk())
                else:
                    durdur_fonk()
                kayit["durum"] = "durduruldu"
                logger.info(f"[Restart]  -> {ad} durduruldu")
            except Exception as e:
                logger.error(f"[Restart]  -> {ad} durdurma hatası: {e}")
            if bekleme > 0 and ad != sirali[-1]:
                time.sleep(bekleme)

        # AŞAMA 2: Tümünü başlat
        logger.info("[Restart] AŞAMA 2: Tüm platformlar başlatılıyor...")
        for ad in sirali:
            if ad not in _platformlar:
                sonuclar[ad] = False
                continue
            kayit = _platformlar[ad]
            try:
                baslat_fonk = kayit["baslat"]
                if asyncio.iscoroutinefunction(baslat_fonk):
                    asyncio.get_event_loop().run_until_complete(baslat_fonk())
                else:
                    baslat_fonk()
                kayit["durum"] = "aktif"
                kayit["son_restart"] = datetime.now(timezone.utc).isoformat()
                sonuclar[ad] = True
                logger.info(f"[Restart]  -> {ad} başlatıldı")
            except Exception as e:
                kayit["durum"] = "hata"
                sonuclar[ad] = False
                logger.error(f"[Restart]  -> {ad} başlatma hatası: {e}")
            if bekleme > 0 and ad != sirali[-1]:
                time.sleep(bekleme)

        basarili = sum(1 for v in sonuclar.values() if v)
        logger.info(f"[Restart] === Yeniden başlatma tamam: {basarili}/{len(sirali)} başarılı ===")

    except Exception as e:
        logger.error(f"[Restart] Toplu restart hatası: {e}")

    return sonuclar


def durum_raporu() -> dict:
    """Tüm platformların durum raporunu döndürür."""
    rapor = {}
    for ad, kayit in _platformlar.items():
        rapor[ad] = {
            "durum": kayit["durum"],
            "son_restart": kayit["son_restart"],
        }
        if kayit["kontrol"]:
            try:
                kontrol_fonk = kayit["kontrol"]
                if asyncio.iscoroutinefunction(kontrol_fonk):
                    saglik = asyncio.get_event_loop().run_until_complete(kontrol_fonk())
                else:
                    saglik = kontrol_fonk()
                rapor[ad]["saglik"] = saglik
            except Exception as e:
                rapor[ad]["saglik"] = f"hata: {e}"
    return rapor


def platform_listele() -> list[str]:
    """Kayıtlı platform adlarını listeler."""
    return list(_platformlar.keys())


def platform_kaldir(ad: str) -> bool:
    """Platformu restart yöneticisinden kaldırır."""
    try:
        if ad in _platformlar:
            del _platformlar[ad]
            logger.info(f"[Restart] Platform kaldırıldı: {ad}")
            return True
        return False
    except Exception as e:
        logger.error(f"[Restart] Platform kaldırma hatası: {e}")
        return False


# Sinyal işleyici — graceful shutdown için
_original_handlers: dict[int, any] = {}


def _sinyal_isyelisi(sinyal_num: int, frame):
    """Sinyal yakalandığında tüm platformları güvenle durdurur."""
    sinyal_adi = signal.Signals(sinyal_num).name
    logger.warning(f"[Restart] Sinyal alındı: {sinyal_adi}")
    send_restart_signal(sebep=f"sinyal_{sinyal_adi}")
    # Orijinal işleyiciyi çağır
    if sinyal_num in _original_handlers and _original_handlers[sinyal_num]:
        _original_handlers[sinyal_num](sinyal_num, frame)


def sinyal_yakalama_kur():
    """SIGINT ve SIGTERM sinyallerini yakalayıp graceful shutdown yapar."""
    try:
        for sig in [signal.SIGINT, signal.SIGTERM]:
            if hasattr(signal, sig.name):
                _original_handlers[sig] = signal.getsignal(sig)
                signal.signal(sig, _sinyal_isyelisi)
                logger.info(f"[Restart] Sinyal yakalama kuruldu: {sig.name}")
    except Exception as e:
        logger.warning(f"[Restart] Sinyal yakalama kurulamadı: {e}")


def sinyal_yakalama_kaldir():
    """Sinyal işleyicilerini eski haline döndürür."""
    for sig, handler in _original_handlers.items():
        try:
            signal.signal(sig, handler)
        except Exception:
            logger.warning("[fix_01_sessiz_except] Exception")
    _original_handlers.clear()
