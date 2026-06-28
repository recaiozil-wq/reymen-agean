# -*- coding: utf-8 -*-
"""tools/todo_tool.py — Yapılacaklar Listesi Yönetim Aracı.

ReYMeN: .ReYMeN/todos.json dosyasında görevleri saklar.
Ekleme, listeleme, tamamlama ve silme işlemlerini destekler.
"""

import json
import os
import time
from pathlib import Path


def _todos_yolu() -> str:
    """todos.json dosyasının yolunu döndür."""
    # Önce proje köküne bak
    # tools/ altından proje köküne çık
    tool_path = Path(__file__).resolve().parent
    proje_kok = tool_path.parent

    # .ReYMeN klasörü proje kökünde mi?
    ReYMeN_dir = proje_kok / ".ReYMeN"
    if not ReYMeN_dir.exists():
        ReYMeN_dir.mkdir(parents=True, exist_ok=True)

    return str(ReYMeN_dir / "todos.json")


def _todos_yukle() -> list:
    """todos.json'dan görevleri yükle."""
    dosya_yolu = _todos_yolu()
    if not os.path.exists(dosya_yolu):
        return []
    try:
        with open(dosya_yolu, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            return []
    except (json.JSONDecodeError, Exception):
        return []


def _todos_kaydet(todos: list) -> None:
    """Görev listesini todos.json'a kaydet."""
    dosya_yolu = _todos_yolu()
    with open(dosya_yolu, "w", encoding="utf-8") as f:
        json.dump(todos, f, ensure_ascii=False, indent=2)


def _yeni_id(todos: list) -> int:
    """Yeni görev için benzersiz ID üret."""
    if not todos:
        return 1
    return max(t["id"] for t in todos) + 1


def _ekle(baslik: str, aciklama: str = "", oncelik: str = "normal") -> str:
    """Yeni görev ekle."""
    if not baslik or not baslik.strip():
        return json.dumps({
            "durum": "hata",
            "hata": "Görev başlığı boş olamaz."
        }, ensure_ascii=False)

    # Öncelik doğrulama
    gecerli_oncelikler = ["dusuk", "low", "normal", "orta", "high", "yuksek", "urgent", "acil"]
    if oncelik.lower() not in gecerli_oncelikler:
        oncelik = "normal"

    # Öncelik normalizasyonu
    oncelik_map = {
        "dusuk": "dusuk", "low": "dusuk",
        "normal": "normal", "orta": "normal",
        "yuksek": "yuksek", "high": "yuksek",
        "acil": "acil", "urgent": "acil"
    }
    oncelik = oncelik_map.get(oncelik.lower(), "normal")

    todos = _todos_yukle()
    yeni_gorev = {
        "id": _yeni_id(todos),
        "baslik": baslik.strip(),
        "aciklama": aciklama,
        "oncelik": oncelik,
        "durum": "bekliyor",
        "olusturma": time.strftime("%Y-%m-%d %H:%M:%S"),
        "tamamlanma": None
    }
    todos.append(yeni_gorev)
    _todos_kaydet(todos)

    return json.dumps({
        "durum": "basarili",
        "mesaj": f"Görev eklendi: {baslik}",
        "gorev": yeni_gorev
    }, ensure_ascii=False)


def _listele(durum: str = None) -> str:
    """Görevleri listele."""
    todos = _todos_yukle()
    if not todos:
        return json.dumps({
            "durum": "basarili",
            "mesaj": "Hiç görev yok.",
            "gorevler": []
        }, ensure_ascii=False)

    if durum:
        gecerli_durumlar = {
            "bekliyor": "bekliyor", "pending": "bekliyor",
            "devam": "devam", "in_progress": "devam", "active": "devam",
            "tamam": "tamamlandi", "done": "tamamlandi", "completed": "tamamlandi",
            "tamamlandi": "tamamlandi"
        }
        filtre_durum = gecerli_durumlar.get(durum.lower())
        if filtre_durum:
            todos = [t for t in todos if t.get("durum") == filtre_durum]
        else:
            # Doğrudan dene
            todos = [t for t in todos if t.get("durum") == durum.lower()]

    # Öncelik sırasına göre sırala
    oncelik_sira = {"acil": 0, "yuksek": 1, "normal": 2, "dusuk": 3}
    todos.sort(key=lambda t: oncelik_sira.get(t.get("oncelik", "normal"), 99))

    return json.dumps({
        "durum": "basarili",
        "toplam": len(todos),
        "gorevler": todos
    }, ensure_ascii=False)


def _tamamla(gorev_id: int) -> str:
    """Görevi tamamlandı olarak işaretle."""
    todos = _todos_yukle()
    for t in todos:
        if t["id"] == gorev_id:
            t["durum"] = "tamamlandi"
            t["tamamlanma"] = time.strftime("%Y-%m-%d %H:%M:%S")
            _todos_kaydet(todos)
            return json.dumps({
                "durum": "basarili",
                "mesaj": f"Görev tamamlandı: {t['baslik']}",
                "gorev": t
            }, ensure_ascii=False)

    return json.dumps({
        "durum": "hata",
        "hata": f"Görev bulunamadı (ID: {gorev_id})"
    }, ensure_ascii=False)


def _sil(gorev_id: int) -> str:
    """Görevi listeden sil."""
    todos = _todos_yukle()
    for i, t in enumerate(todos):
        if t["id"] == gorev_id:
            silinen = todos.pop(i)
            _todos_kaydet(todos)
            return json.dumps({
                "durum": "basarili",
                "mesaj": f"Görev silindi: {silinen['baslik']}",
                "gorev": silinen
            }, ensure_ascii=False)

    return json.dumps({
        "durum": "hata",
        "hata": f"Görev bulunamadı (ID: {gorev_id})"
    }, ensure_ascii=False)


def run(islem=None, **kwargs) -> str:
    """Yapılacaklar listesi işlemlerini yönet.

    Kullanım:
        İşlemler:
        - "ekle": Yeni görev ekle. Parametreler: baslik(zorunlu), aciklama(""), oncelik("normal")
        - "listele": Görevleri listele. Parametre: durum(None) -> "bekliyor"/"tamamlandi"
        - "tamamla": Görevi tamamla. Parametre: id(zorunlu)
        - "sil": Görevi sil. Parametre: id(zorunlu)

    Args:
        islem (str): Yapılacak işlem (ekle/listele/liste/tamamla/sil).
        baslik (str, optional): Görev başlığı (ekle için zorunlu).
        aciklama (str, optional): Görev açıklaması.
        oncelik (str, optional): Öncelik (dusuk/normal/yuksek/acil). Varsayılan: "normal".
        durum (str, optional): Filtre durumu (listele için).
        id (int, optional): Görev ID'si (tamamla/sil için).
        icerik (str, optional): Görev başlığı için alias parametre.

    Returns:
        str: JSON formatında işlem sonucu.
    """
    try:
        islem = islem if islem is not None else kwargs.get("islem", "")
        islem = islem.lower().strip()
        if not islem:
            return json.dumps({
                "durum": "hata",
                "hata": "'islem' parametresi zorunludur (ekle/listele/tamamla/sil)."
            }, ensure_ascii=False)

        if islem == "ekle":
            baslik = kwargs.get("baslik", "") or kwargs.get("icerik", "")
            return _ekle(
                baslik=baslik,
                aciklama=kwargs.get("aciklama", ""),
                oncelik=kwargs.get("oncelik", "normal")
            )
        elif islem in ("listele", "liste"):
            return _listele(durum=kwargs.get("durum"))
        elif islem == "tamamla":
            gorev_id = kwargs.get("id")
            if gorev_id is None:
                return json.dumps({
                    "durum": "hata",
                    "hata": "'id' parametresi zorunludur."
                }, ensure_ascii=False)
            return _tamamla(int(gorev_id))
        elif islem == "sil":
            gorev_id = kwargs.get("id")
            if gorev_id is None:
                return json.dumps({
                    "durum": "hata",
                    "hata": "'id' parametresi zorunludur."
                }, ensure_ascii=False)
            return _sil(int(gorev_id))
        else:
            return json.dumps({
                "durum": "hata",
                "hata": f"Geçersiz işlem: '{islem}'. Desteklenen: ekle, listele, tamamla, sil"
            }, ensure_ascii=False)

    except Exception as e:
        return json.dumps({
            "durum": "hata",
            "hata": f"Beklenmeyen hata: {e}"
        }, ensure_ascii=False)


def ping() -> bool:
    return True


def motor_kaydet(motor) -> None:
    """Motor'a arac kaydetmesi icin kayit fonksiyonu."""
    motor._plugin_arac_kaydet(
        "TODO",
        run,
        "Yapılacaklar listesini yönetir (ekle/liste/listele/tamamla/sil)."
    )


if __name__ == "__main__":
    print(run(islem="ekle", baslik="ReYMeN projesini tamamla", oncelik="yuksek"))
    print(run(islem="listele"))
