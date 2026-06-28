# -*- coding: utf-8 -*-
"""kanban_tools.py — Kanban Yonetim Araclari.

ReYMeN projesinde gorev takibi icin .ReYMeN/checkpoints/ klasorunde
JSON dosyalari ile calisan basit bir kanban sistemi.
"""

import json
import uuid
from datetime import datetime
from pathlib import Path

CHECKPOINT_DIR = Path(__file__).parent.parent / ".ReYMeN" / "checkpoints"
KANBAN_DOSYA = CHECKPOINT_DIR / "kanban.json"


def _kartlari_yukle() -> list:
    """Kanban JSON dosyasindan tum kartlari yukler.

    Returns:
        list: Kart listesi (yoksa bos liste)
    """
    if not KANBAN_DOSYA.exists():
        return []
    try:
        with open(KANBAN_DOSYA, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, Exception):
        return []


def _kartlari_kaydet(kartlar: list) -> None:
    """Kart listesini JSON dosyasina yazar.

    Args:
        kartlar: Kaydedilecek kart listesi
    """
    CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)
    with open(KANBAN_DOSYA, "w", encoding="utf-8") as f:
        json.dump(kartlar, f, ensure_ascii=False, indent=2)


def liste_goruntule(durum: str = None) -> str:
    """Kanban kartlarini listeler.

    Args:
        durum: Filtreleme icin durum (opsiyonel, orn: "pending", "active", "done")

    Returns:
        str: Kart listesi metni veya hata mesaji
    """
    try:
        kartlar = _kartlari_yukle()
        if not kartlar:
            return "[Kanban]: Henuz hic kart yok."

        if durum:
            kartlar = [k for k in kartlar if k.get("durum") == durum]
            if not kartlar:
                return f"[Kanban]: '{durum}' durumunda kart bulunamadi."

        sonuc = [f"[Kanban]: Toplam {len(kartlar)} kart:"]
        for kart in kartlar:
            kid = kart.get("id", "???")
            baslik = kart.get("baslik", "Basliksiz")
            kdurum = kart.get("durum", "bilinmiyor")
            tarih = kart.get("olusturma", "")
            sonuc.append(f"  [{kid}] {baslik} ({kdurum}) - {tarih}")
        return "\n".join(sonuc)

    except Exception as e:
        return f"[Kanban]: Liste hatasi - {e}"


def kart_ekle(baslik: str, icerik: str = "", durum: str = "pending") -> str:
    """Yeni bir kanban karti olusturur.

    Args:
        baslik: Kart basligi (zorunlu)
        icerik: Kart icerigi (opsiyonel)
        durum: Baslangic durumu (varsayilan: "pending")

    Returns:
        str: Durum mesaji
    """
    if not baslik:
        return "[Kanban]: Baslik zorunludur."

    try:
        kartlar = _kartlari_yukle()
        yeni_kart = {
            "id": str(uuid.uuid4())[:8],
            "baslik": baslik,
            "icerik": icerik,
            "durum": durum,
            "olusturma": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "guncelleme": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        kartlar.append(yeni_kart)
        _kartlari_kaydet(kartlar)
        return f"[Kanban]: Kart eklendi — [{yeni_kart['id']}] {baslik} ({durum})"

    except Exception as e:
        return f"[Kanban]: Ekleme hatasi - {e}"


def kart_guncelle(kart_id: str, alan: str, deger: str) -> str:
    """Var olan bir kanban kartini gunceller.

    Args:
        kart_id: Guncellenecek kartin ID'si
        alan: Guncellenecek alan adi (orn: "durum", "baslik", "icerik")
        deger: Alana atanacak yeni deger

    Returns:
        str: Durum mesaji
    """
    if not kart_id or not alan:
        return "[Kanban]: kart_id ve alan zorunludur."

    try:
        kartlar = _kartlari_yukle()
        for kart in kartlar:
            if kart.get("id") == kart_id:
                if alan in kart:
                    kart[alan] = deger
                    kart["guncelleme"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                    _kartlari_kaydet(kartlar)
                    return f"[Kanban]: Kart [{kart_id}] {alan} -> {deger} olarak guncellendi."
                else:
                    return f"[Kanban]: '{alan}' alani kartta bulunamadi."
        return f"[Kanban]: [{kart_id}] ID'li kart bulunamadi."

    except Exception as e:
        return f"[Kanban]: Guncelleme hatasi - {e}"


def kart_sil(kart_id: str) -> str:
    """Bir kanban kartini siler.

    Args:
        kart_id: Silinecek kartin ID'si

    Returns:
        str: Durum mesaji
    """
    if not kart_id:
        return "[Kanban]: kart_id zorunludur."

    try:
        kartlar = _kartlari_yukle()
        yeni_kartlar = [k for k in kartlar if k.get("id") != kart_id]
        if len(yeni_kartlar) == len(kartlar):
            return f"[Kanban]: [{kart_id}] ID'li kart bulunamadi."
        _kartlari_kaydet(yeni_kartlar)
        return f"[Kanban]: [{kart_id}] ID'li kart silindi."

    except Exception as e:
        return f"[Kanban]: Silme hatasi - {e}"


def run(**kwargs) -> str:
    """Kanban ana yonlendirme fonksiyonu.

    Desteklenen islemler: liste_goruntule, kart_ekle, kart_guncelle, kart_sil

    Args:
        islem (str): Yapilacak islem (zorunlu)
        durum (str): Filtreleme durumu (liste_goruntule icin)
        baslik (str): Kart basligi (kart_ekle icin)
        icerik (str): Kart icerigi (kart_ekle icin)
        kart_id (str): Kart ID'si (kart_guncelle, kart_sil icin)
        alan (str): Guncellenecek alan (kart_guncelle icin)
        deger (str): Yeni deger (kart_guncelle icin)

    Returns:
        str: Islem sonucu
    """
    islem = kwargs.get("islem", "")
    if not islem:
        return "[Kanban]: 'islem' parametresi zorunlu (liste_goruntule, kart_ekle, kart_guncelle, kart_sil)."

    try:
        if islem == "liste_goruntule":
            return liste_goruntule(kwargs.get("durum"))
        elif islem == "kart_ekle":
            return kart_ekle(
                kwargs.get("baslik", ""),
                kwargs.get("icerik", ""),
                kwargs.get("durum", "pending")
            )
        elif islem == "kart_guncelle":
            return kart_guncelle(
                kwargs.get("kart_id", ""),
                kwargs.get("alan", ""),
                kwargs.get("deger", "")
            )
        elif islem == "kart_sil":
            return kart_sil(kwargs.get("kart_id", ""))
        else:
            return f"[Kanban]: Bilinmeyen islem: {islem}"
    except Exception as e:
        return f"[Kanban]: Hata - {e}"


def ping() -> bool:
    return True


if __name__ == "__main__":
    print(run(islem="kart_ekle", baslik="Test gorevi", icerik="Deneme"))
    print(run(islem="liste_goruntule"))
