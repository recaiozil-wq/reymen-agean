# -*- coding: utf-8 -*-
"""tools/osv_check.py — Python Paket Güvenlik Tarama Aracı.

ReYMeN: osv.dev API'sine bağlanarak Python paketlerinin
güvenlik açıklarını sorgular. requirements.txt veya doğrudan
paket adı ile çalışır.
"""

import json
import os
import re
import logging
logger = logging.getLogger(__name__)


def _paket_normalize(paket_adi: str) -> str:
    """Paket adını normalize et (büyük harf, boşluk, versiyon vs.)."""
    # Versiyon bilgisini ayır
    eslesme = re.match(r"^([a-zA-Z0-9_.-]+)\s*([><=!]+.*)?$", paket_adi.strip())
    if eslesme:
        return eslesme.group(1).strip().lower()
    return paket_adi.strip().lower()


def _requirements_parse(dosya_yolu: str) -> list:
    """requirements.txt dosyasını parse et, paket listesi döndür."""
    paketler = []
    try:
        with open(dosya_yolu, "r", encoding="utf-8") as f:
            for satir in f:
                satir = satir.strip()
                # Yorum ve boş satırları atla
                if not satir or satir.startswith("#") or satir.startswith("-"):
                    continue
                # Versiyon bilgisini temizle
                paket = re.sub(r"[><=!].*$", "", satir).strip()
                if paket and paket not in ("", "."):
                    paketler.append(paket.lower())
    except Exception as e:
        raise Exception(f"requirements.txt okunamadı: {e}")
    return paketler


def _osv_sorgula(paket_adi: str) -> dict:
    """Tek bir paketi osv.dev API'sinde sorgula."""
    try:
        import requests
        payload = {
            "package": {
                "name": paket_adi,
                "ecosystem": "PyPI"
            }
        }
        r = requests.post(
            "https://api.osv.dev/v1/query",
            json=payload,
            timeout=30,
            headers={"Content-Type": "application/json"}
        )
        if r.status_code == 200:
            return r.json()
        else:
            return {"hata": f"HTTP {r.status_code}: {r.text[:200]}"}
    except ImportError:
        return {"hata": "'requests' kütüphanesi gerekli. pip install requests"}
    except requests.exceptions.ConnectionError:
        return {"hata": "osv.dev API'sine bağlanılamadı."}
    except Exception as e:
        return {"hata": str(e)}


def run(**kwargs) -> str:
    """Python paket güvenlik taraması yap.

    Args:
        paket_adi (str, optional): Sorgulanacak paket adı (ör: "requests", "flask==2.0.0").
        requirements_yolu (str, optional): requirements.txt dosya yolu.

    Returns:
        str: JSON formatında güvenlik açığı raporu.
    """
    try:
        paket_adi = kwargs.get("paket_adi")
        requirements_yolu = kwargs.get("requirements_yolu")

        # Paket listesini belirle
        paketler = []
        kaynak = ""

        if paket_adi:
            paketler = [_paket_normalize(paket_adi)]
            kaynak = f"paket_adi: {paket_adi}"
        elif requirements_yolu:
            if not os.path.exists(requirements_yolu):
                return json.dumps({
                    "durum": "hata",
                    "hata": f"Dosya bulunamadı: {requirements_yolu}"
                }, ensure_ascii=False)
            paketler = _requirements_parse(requirements_yolu)
            if not paketler:
                return json.dumps({
                    "durum": "hata",
                    "hata": "requirements.txt'de paket bulunamadı."
                }, ensure_ascii=False)
            kaynak = f"requirements: {requirements_yolu} ({len(paketler)} paket)"
        else:
            return json.dumps({
                "durum": "hata",
                "hata": "'paket_adi' veya 'requirements_yolu' parametrelerinden biri zorunludur."
            }, ensure_ascii=False)

        # Her paketi sorgula
        sonuclar = {}
        toplam_acik = 0
        for p in paketler:
            osv_sonuc = _osv_sorgula(p)
            if "vulns" in osv_sonuc and osv_sonuc["vulns"]:
                sonuclar[p] = {
                    "guvenlik_acigi_sayisi": len(osv_sonuc["vulns"]),
                    "aciklar": []
                }
                for vuln in osv_sonuc["vulns"][:10]:  # İlk 10 açığı göster
                    acik = {
                        "id": vuln.get("id", "Bilinmiyor"),
                        "summary": vuln.get("summary", "Açıklama yok")[:200],
                    }
                    if "aliases" in vuln and vuln["aliases"]:
                        acik["aliases"] = vuln["aliases"][:3]
                    if "severity" in vuln and vuln["severity"]:
                        for s in vuln["severity"]:
                            if s.get("type") == "CVSS_V3":
                                acik["cvss"] = s.get("score")
                    sonuclar[p]["aciklar"].append(acik)
                toplam_acik += len(osv_sonuc["vulns"])
            elif "hata" in osv_sonuc:
                sonuclar[p] = {"hata": osv_sonuc["hata"]}
            else:
                sonuclar[p] = {"guvenlik_acigi_sayisi": 0, "durum": "temiz"}

        rapor = {
            "durum": "tamam",
            "kaynak": kaynak,
            "toplam_paket": len(paketler),
            "toplam_guvenlik_acigi": toplam_acik,
            "sonuclar": sonuclar
        }
        return json.dumps(rapor, ensure_ascii=False, indent=2)

    except Exception as e:
        return json.dumps({
            "durum": "hata",
            "hata": f"Beklenmeyen hata: {e}"
        }, ensure_ascii=False)


def ping() -> bool:
    return True


if __name__ == "__main__":
    print(run(paket_adi="requests"))
