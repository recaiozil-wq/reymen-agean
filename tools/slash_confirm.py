# -*- coding: utf-8 -*-
"""tools/slash_confirm.py — Slash Onay Mekanizmasi.

Onemli islemler icin / ile baslayan onay komutlarini yonetir.
Kullanici /onayla veya /reddet gibi komutlarla islemi onaylar veya reddeder.
"""
import time
import uuid
from pathlib import Path


def _pending_klasoru() -> Path:
    """.ReYMeN/pending/ klasorunun yolunu dondurur."""
    tool_path = Path(__file__).resolve().parent
    proje_kok = tool_path.parent
    pending_dir = proje_kok / ".ReYMeN" / "pending"
    pending_dir.mkdir(parents=True, exist_ok=True)
    return pending_dir


def run(islem='onay_iste', **kwargs) -> str:
    """Slash onay mekanizmasi.

    Parametreler:
        islem (str): 'onay_iste', 'onay_ver' veya 'onay_reddet'
        komut (str): Onaylanacak komut
        aciklama (str): Komutun aciklamasi
        onay_id (str): Onay ID'si (onay_ver/onay_reddet icin)

    Returns:
        str: Islem sonucu.
    """
    try:
        pending_dir = _pending_klasoru()

        if islem == 'onay_iste':
            komut = kwargs.get('komut', '')
            aciklama = kwargs.get('aciklama', '')

            if not komut:
                return "Hata: 'komut' parametresi zorunludur."

            onay_id = str(uuid.uuid4())[:8]
            zaman = time.time()

            # Bekleyen onayi dosyaya kaydet
            onay_verisi = {
                "id": onay_id,
                "komut": komut,
                "aciklama": aciklama,
                "zaman": zaman,
                "durum": "bekliyor",
            }

            dosya = pending_dir / f"onay_{onay_id}.json"
            import json
            dosya.write_text(
                json.dumps(onay_verisi, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

            satirlar = [
                f"Onay gerekiyor!",
                f"  Onay ID: /{onay_id}",
                f"  Komut: {komut}",
            ]
            if aciklama:
                satirlar.append(f"  Aciklama: {aciklama}")
            satirlar.append("")
            satirlar.append(f"Onaylamak icin: /{onay_id} onayla")
            satirlar.append(f"Reddetmek icin: /{onay_id} reddet")
            return "\n".join(satirlar)

        elif islem == 'onay_ver':
            onay_id = kwargs.get('onay_id', '')

            if not onay_id:
                return "Hata: 'onay_id' parametresi zorunludur."

            # ID'den basindaki / temizle
            onay_id = onay_id.lstrip("/")

            dosya = pending_dir / f"onay_{onay_id}.json"
            if not dosya.exists():
                return f"Onay bulunamadi veya suresi dolmus: {onay_id}"

            import json
            try:
                veri = json.loads(dosya.read_text(encoding="utf-8"))
            except Exception:
                return f"Onay dosyasi bozuk: {onay_id}"

            if veri.get("durum") != "bekliyor":
                return f"Onay zaten {veri.get('durum', 'bilinmeyen')}: {onay_id}"

            veri["durum"] = "onaylandi"
            veri["islem_zamani"] = time.time()
            dosya.write_text(
                json.dumps(veri, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

            return (
                f"Onaylandi: /{onay_id}\n"
                f"  Komut: {veri['komut']}\n"
                f"  Islem baslatiliyor..."
            )

        elif islem == 'onay_reddet':
            onay_id = kwargs.get('onay_id', '')

            if not onay_id:
                return "Hata: 'onay_id' parametresi zorunludur."

            # ID'den basindaki / temizle
            onay_id = onay_id.lstrip("/")

            dosya = pending_dir / f"onay_{onay_id}.json"
            if not dosya.exists():
                return f"Onay bulunamadi veya suresi dolmus: {onay_id}"

            import json
            try:
                veri = json.loads(dosya.read_text(encoding="utf-8"))
            except Exception:
                return f"Onay dosyasi bozuk: {onay_id}"

            if veri.get("durum") != "bekliyor":
                return f"Onay zaten {veri.get('durum', 'bilinmeyen')}: {onay_id}"

            veri["durum"] = "reddedildi"
            veri["islem_zamani"] = time.time()
            dosya.write_text(
                json.dumps(veri, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

            return (
                f"Reddedildi: /{onay_id}\n"
                f"  Komut: {veri['komut']}\n"
                f"  Islem iptal edildi."
            )

        else:
            return f"Hata: Gecersiz islem '{islem}'."

    except Exception as e:
        return f"Slash onay hatasi: {e}"
