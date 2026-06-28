# -*- coding: utf-8 -*-
"""tools/approval.py — Onay mekanizmasi.

Kullanici onayi gerektiren islemleri yonetir.
.ReYMeN/pending/ klasorunde JSON dosyalari ile calisir.
"""

import json
import os
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


def _dosyadan_yukle(dosya_yolu: str) -> dict:
    """JSON dosyasini yukler, hata durumunda bos dict doner."""
    try:
        with open(dosya_yolu, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, Exception):
        return {}


def _dosyaya_kaydet(dosya_yolu: str, veri: dict) -> None:
    """Veriyi JSON dosyasina kaydeder."""
    with open(dosya_yolu, "w", encoding="utf-8") as f:
        json.dump(veri, f, ensure_ascii=False, indent=2)


def approval(islem: str = "onay_bekle", islem_id: str = None,
             aciklama: str = "") -> str:
    """Onay mekanizmasi.

    Args:
        islem: "onay_bekle", "onay_ver", "onay_reddet" veya "liste".
        islem_id: Onay islem ID'si.
        aciklama: Islem aciklamasi (onay_bekle'de kullanilir).

    Returns:
        Islem sonucu metni.
    """
    try:
        pending_dir = _pending_klasoru()

        if islem == "onay_bekle":
            return _onay_bekle(pending_dir, islem_id, aciklama)

        elif islem == "onay_ver":
            return _onay_ver(pending_dir, islem_id)

        elif islem == "onay_reddet":
            return _onay_reddet(pending_dir, islem_id)

        elif islem == "liste":
            return _listele(pending_dir)

        else:
            return f"[Hata] Bilinmeyen islem: {islem}. Secenekler: onay_bekle, onay_ver, onay_reddet, liste"

    except Exception as e:
        return f"[Hata] Onay mekanizmasi: {e}"


def _onay_bekle(pending_dir: Path, islem_id: str = None,
                aciklama: str = "") -> str:
    """Yeni bir onay istegi olusturur.
    
    REYMEN_OTOMATIK_ONAY=true ise direkt onaylanmis sayilir (dosya olusturmaz).
    """
    # Otomatik onay: direkt True döner, pending'e yazmaz
    if os.environ.get("REYMEN_OTOMATIK_ONAY", "").lower() in ("true", "1", "yes"):
        return f"[Onay] (otomatik) '{islem_id or 'anonim'}' onaylandi."

    if not islem_id:
        islem_id = str(uuid.uuid4())[:8]

    dosya_yolu = pending_dir / f"{islem_id}.json"

    # Zaten var mi?
    if dosya_yolu.exists():
        return f"[Uyari] Bu islem zaten bekliyor: {islem_id}"

    kayit = {
        "id": islem_id,
        "durum": "beklemede",
        "aciklama": aciklama,
        "olusturma": time.time(),
        "son_guncelleme": time.time(),
    }
    _dosyaya_kaydet(str(dosya_yolu), kayit)

    return (
        f"[Onay] Islem '{islem_id}' onay bekliyor.\n"
        f"  Aciklama: {aciklama or '(yok)'}\n"
        f"  Onay vermek: approval(islem='onay_ver', islem_id='{islem_id}')\n"
        f"  Reddetmek: approval(islem='onay_reddet', islem_id='{islem_id}')"
    )


def _onay_ver(pending_dir: Path, islem_id: str) -> str:
    """Bekleyen bir onay istegini onaylar."""
    if not islem_id:
        return "[Hata] islem_id gerekli."

    dosya_yolu = pending_dir / f"{islem_id}.json"

    if not dosya_yolu.exists():
        return f"[Hata] Islem bulunamadi: {islem_id}"

    kayit = _dosyadan_yukle(str(dosya_yolu))
    if kayit.get("durum") != "beklemede":
        return f"[Uyari] Islem '{islem_id}' zaten {kayit.get('durum', 'bilinmiyor')}."

    kayit["durum"] = "onaylandi"
    kayit["son_guncelleme"] = time.time()
    _dosyaya_kaydet(str(dosya_yolu), kayit)

    return f"[Onay] '{islem_id}' onaylandi."


def _onay_reddet(pending_dir: Path, islem_id: str) -> str:
    """Bekleyen bir onay istegini reddeder."""
    if not islem_id:
        return "[Hata] islem_id gerekli."

    dosya_yolu = pending_dir / f"{islem_id}.json"

    if not dosya_yolu.exists():
        return f"[Hata] Islem bulunamadi: {islem_id}"

    kayit = _dosyadan_yukle(str(dosya_yolu))
    if kayit.get("durum") != "beklemede":
        return f"[Uyari] Islem '{islem_id}' zaten {kayit.get('durum', 'bilinmiyor')}."

    kayit["durum"] = "reddedildi"
    kayit["son_guncelleme"] = time.time()
    _dosyaya_kaydet(str(dosya_yolu), kayit)

    return f"[Onay] '{islem_id}' reddedildi."


def _listele(pending_dir: Path) -> str:
    """Bekleyen tum onay isteklerini listeler."""
    dosyalar = sorted(pending_dir.glob("*.json"))

    if not dosyalar:
        return "[Onay] Bekleyen islem yok."

    sonuc = ["[Onay] Bekleyen islemler:"]
    for f in dosyalar:
        kayit = _dosyadan_yukle(str(f))
        sonuc.append(
            f"  - {kayit.get('id', f.stem)}: "
            f"{kayit.get('durum', 'bilinmiyor')} | "
            f"{kayit.get('aciklama', '')[:60]}"
        )

    return "\n".join(sonuc)


def run(**kwargs) -> str:
    """Approval modulu icin genel run() wrapper'ı."""
    return approval(**kwargs)


# ── YOLO MODE ─────────────────────────────────────────────────────────────────
# Dangerous mode: atlar tum tehlikeli komut onaylarini
# Kaynak: Hermes Agent approval.py

import os as _os
import threading as _threading

_session_yolo: set = set()
_yolo_lock = _threading.Lock()
_YOLO_ENV_VAR = "REYMEN_YOLO_MODE"

# Process-start flag'indan donmus deger (`reymen --yolo` ile set edilir)
_YOLO_MODE_FROZEN: bool = _os.environ.get(_YOLO_ENV_VAR, "").strip() in ("1", "true", "yes", "on")


def enable_session_yolo(session_key: str) -> None:
    """Bir oturum icin YOLO modunu aktif et."""
    with _yolo_lock:
        _session_yolo.add(session_key)


def disable_session_yolo(session_key: str) -> None:
    """Bir oturum icin YOLO modunu devre disi birak."""
    with _yolo_lock:
        _session_yolo.discard(session_key)


def is_session_yolo_enabled(session_key: str) -> bool:
    """YOLO modu aktif mi?"""
    with _yolo_lock:
        return session_key in _session_yolo


def set_current_session_key(session_key: str) -> None:
    """Aktif CLI oturumunun YOLO state key'ini sakla.
    
    ``run_conversation`` tarafindan her tur basinda cagrilir,
    boylece ``/yolo`` toggle'i bir sonraki tehlikeli komutta
    hemen etkili olur.
    """
    global _CURRENT_SESSION_KEY
    _CURRENT_SESSION_KEY = session_key


_CURRENT_SESSION_KEY: str = "default"


def yolo_ac(session_key: str = "") -> None:
    """YOLO modunu ac (disardan erisim icin)."""
    key = session_key or _CURRENT_SESSION_KEY
    enable_session_yolo(key)


def yolo_kapat(session_key: str = "") -> None:
    """YOLO modunu kapat."""
    key = session_key or _CURRENT_SESSION_KEY
    disable_session_yolo(key)


def check_all_command_guards(command: str, cwd: str = "", **kwargs) -> dict:
    """Tum komut guardslarini kontrol et - ReYMeN uyumluluk stubu."""
    return {"allowed": True, "command": command, "guards_passed": []}