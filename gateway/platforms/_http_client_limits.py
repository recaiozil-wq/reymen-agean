# -*- coding: utf-8 -*-
"""gateway/platforms/_http_client_limits.py — HTTP Istemci Limitleri.

Rate limit, timeout, retry paylasimli helper.
requests.Session kullanir.
"""

import os
import time
import logging
from typing import Optional

try:
    import requests
    _REQUESTS_OK = True
except ImportError:
    _REQUESTS_OK = False

try:
    import httpx
    _HTTPX_OK = True
except ImportError:
    _HTTPX_OK = False

logger = logging.getLogger(__name__)

# Varsayilan session (paylasilan)
_session: Optional[requests.Session] = None


def _get_session() -> Optional[requests.Session]:
    """Paylasilan requests.Session ornegini dondurur.

    Returns:
        requests.Session veya None (requests yoksa)
    """
    global _session
    if not _REQUESTS_OK:
        return None
    if _session is None:
        _session = requests.Session()
        # Varsayilan adapter ayarlari
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=10,
            pool_maxsize=20,
            max_retries=0,  # Kendi retry mekanizmamizi kullan
        )
        _session.mount("https://", adapter)
        _session.mount("http://", adapter)
    return _session


def limitli_istek(
    url: str,
    max_retry: int = 3,
    timeout: int = 30,
    method: str = "GET",
    **kwargs,
) -> dict:
    """Rate limit ve retry ile HTTP istegi yapar.

    requests.Session kullanarak, belirtilen sayida tekrar deneme
    ve timeout ile guvenli HTTP istegi.

    Args:
        url: Istek URL'si
        max_retry: Maksimum tekrar deneme sayisi (varsayilan: 3)
        timeout: Istek timeout suresi (saniye, varsayilan: 30)
        method: HTTP method (GET, POST, PUT, DELETE, PATCH; varsayilan: GET)

    Keyword Args:
        json: JSON body (POST/PUT/PATCH icin)
        data: Form body (POST/PUT/PATCH icin)
        headers: Ozel header'lar
        params: URL parametreleri
        stream: Stream modu (indirme icin)
        retry_delay: Tekrar denemeler arasi bekleme (saniye, varsayilan: 1)
        retry_backoff: Her denemede bekleme suresini carpan katsayi (varsayilan: 2)

    Returns:
        dict: {
            "basarili": bool,
            "durum_kodu": int,
            "veri": dict | list | str | None,  # JSON yaniti veya text
            "hata": str | None,
            "deneme_sayisi": int,
        }
    """
    if not _REQUESTS_OK:
        return {
            "basarili": False,
            "durum_kodu": 0,
            "veri": None,
            "hata": "requests kutuphanesi yok.",
            "deneme_sayisi": 0,
        }

    session = _get_session()
    method = method.upper()
    retry_delay = kwargs.pop("retry_delay", 1)
    retry_backoff = kwargs.pop("retry_backoff", 2)

    # URL'den headers, json, data, params, stream'i ayir
    req_kwargs = {}
    for key in ("json", "data", "headers", "params", "stream", "cookies", "auth"):
        if key in kwargs:
            req_kwargs[key] = kwargs.pop(key)

    son_hata = None
    for deneme in range(1, max_retry + 1):
        try:
            r = session.request(
                method=method,
                url=url,
                timeout=timeout,
                **req_kwargs,
            )

            # Rate limit kontrol (429 Too Many Requests)
            if r.status_code == 429:
                retry_after = int(r.headers.get("Retry-After", retry_delay * (retry_backoff ** (deneme - 1))))
                logger.warning(
                    "Rate limit (429) - Deneme %d/%d, %d sn bekleniyor...",
                    deneme, max_retry, retry_after,
                )
                if deneme < max_retry:
                    time.sleep(min(retry_after, 30))  # En fazla 30 sn bekle
                    continue
                return {
                    "basarili": False,
                    "durum_kodu": 429,
                    "veri": _parse_yanit(r),
                    "hata": f"Rate limit asildi ({max_retry} deneme).",
                    "deneme_sayisi": deneme,
                }

            # 5xx hatalarinda tekrar dene
            if 500 <= r.status_code < 600:
                if deneme < max_retry:
                    bekle = retry_delay * (retry_backoff ** (deneme - 1))
                    logger.warning(
                        "Sunucu hatasi %d - Deneme %d/%d, %d sn bekleniyor...",
                        r.status_code, deneme, max_retry, bekle,
                    )
                    time.sleep(min(bekle, 30))
                    continue

            return {
                "basarili": 200 <= r.status_code < 300,
                "durum_kodu": r.status_code,
                "veri": _parse_yanit(r),
                "hata": None if r.ok else f"HTTP {r.status_code}",
                "deneme_sayisi": deneme,
            }

        except requests.exceptions.Timeout:
            son_hata = f"Timeout ({timeout}s) - Deneme {deneme}/{max_retry}"
            logger.warning(son_hata)
            if deneme < max_retry:
                bekle = retry_delay * (retry_backoff ** (deneme - 1))
                time.sleep(min(bekle, 10))
                continue
        except requests.exceptions.ConnectionError as e:
            son_hata = f"Baglanti hatasi: {e}"
            logger.warning(son_hata)
            if deneme < max_retry:
                bekle = retry_delay * (retry_backoff ** (deneme - 1))
                time.sleep(min(bekle, 10))
                continue
        except Exception as e:
            son_hata = str(e)
            logger.error("Beklenmeyen hata: %s", e)
            break  # Bilinmeyen hatalarda tekrar deneme

    return {
        "basarili": False,
        "durum_kodu": 0,
        "veri": None,
        "hata": son_hata or "Maksimum deneme sayisi asildi.",
        "deneme_sayisi": max_retry,
    }


def _parse_yanit(response: requests.Response):
    """HTTP yanitini JSON veya text olarak ayristirir."""
    content_type = response.headers.get("Content-Type", "").lower()
    if "application/json" in content_type:
        try:
            return response.json()
        except Exception:
            return response.text[:10000]
    return response.text[:10000]


def ping() -> bool:
    """HTTP istemci limitleri modulunun kullanilabilir oldugunu kontrol eder.

    Returns:
        bool: requests kutuphanesi varsa True
    """
    return _REQUESTS_OK


def platform_httpx_limits():
    """Platform-agnostik httpx.Limits nesnesi dondurur.

    Ortam degiskenlerinden okur:
      - HERMES_GATEWAY_HTTPX_KEEPALIVE_EXPIRY (varsayilan: 2.0)
      - HERMES_GATEWAY_HTTPX_MAX_KEEPALIVE   (varsayilan: 10)

    Gecersiz / negatif degerlerde varsayilana doner.
    httpx yoksa None doner.

    Returns:
        httpx.Limits veya None
    """
    if not _HTTPX_OK:
        return None

    # Varsayilanlar
    keepalive_expiry = 2.0
    max_keepalive = 10

    # Ortam degiskenlerinden dene
    raw_expiry = os.environ.get("HERMES_GATEWAY_HTTPX_KEEPALIVE_EXPIRY", "")
    raw_keepalive = os.environ.get("HERMES_GATEWAY_HTTPX_MAX_KEEPALIVE", "")

    if raw_expiry:
        try:
            val = float(raw_expiry)
            if val > 0:
                keepalive_expiry = val
        except (ValueError, TypeError):
            logger.warning("[fix_01_sessiz_except] Exception")

    if raw_keepalive:
        try:
            val = int(raw_keepalive)
            if val > 0:
                max_keepalive = val
        except (ValueError, TypeError):
            logger.warning("[fix_01_sessiz_except] Exception")

    return httpx.Limits(
        keepalive_expiry=keepalive_expiry,
        max_keepalive_connections=max_keepalive,
    )


def rate_limit_kontrol(son_istekler_listesi: list, limit: int = 30, sure: int = 60) -> bool:
    """Rate limit kontrolu yapar.

    Belirtilen sure icinde belirtilen limit kadar istek yapilmis mi kontrol eder.

    Args:
        son_istekler_listesi: Zaman damgasi listesi (epoch seconds)
        limit: Maksimum istek sayisi (varsayilan: 30)
        sure: Kontrol penceresi (saniye, varsayilan: 60)

    Returns:
        bool: Istek yapilabilir ise True, limit asildiysa False

    Ornek:
        >>> istekler = []
        >>> if rate_limit_kontrol(istekler, limit=10, sure=60):
        ...     istekler.append(time.time())
        ...     # istegi yap
    """
    simdi = time.time()
    pencere_baslangici = simdi - sure

    # Eski kayitlari temizle
    guncel_istekler = [t for t in son_istekler_listesi if t > pencere_baslangici]

    # Listeyi guncelle (referansla)
    son_istekler_listesi.clear()
    son_istekler_listesi.extend(guncel_istekler)

    return len(guncel_istekler) < limit
