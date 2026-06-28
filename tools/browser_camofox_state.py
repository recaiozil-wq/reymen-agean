"""
Browser fingerprint durumu yönetim aracı.
Fingerprint kaydetme, okuma, temizleme ve listeleme işlemleri.
"""
import json
import os
from datetime import datetime
import logging
logger = logging.getLogger(__name__)

_FINGERPRINT_DB = {}


def _get_db_path():
    home = os.path.expanduser("~")
    db_dir = os.path.join(home, ".ReYMeN", "profiles", "default", "data")
    os.makedirs(db_dir, exist_ok=True)
    return os.path.join(db_dir, "camofox_state.json")


def _load_db():
    global _FINGERPRINT_DB
    path = _get_db_path()
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                _FINGERPRINT_DB = json.load(f)
        except (json.JSONDecodeError, IOError):
            _FINGERPRINT_DB = {}
    else:
        _FINGERPRINT_DB = {}
    return _FINGERPRINT_DB


def _save_db():
    path = _get_db_path()
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(_FINGERPRINT_DB, f, indent=2, ensure_ascii=False)
        return True
    except IOError as e:
        raise IOError(f"Dosya yazılamadı: {e}")


def run(islem='listele', profil='default', fingerprint=None, **kwargs):
    """
    Browser fingerprint durumu yönetimi.

    Parametreler:
        islem (str): 'kaydet', 'oku', 'temizle' veya 'listele'
        profil (str): Profil adı (varsayılan: 'default')
        fingerprint (dict/str): Kaydedilecek fingerprint verisi

    Returns:
        str: İşlem sonucu.
    """
    try:
        _load_db()
        ts = datetime.now().isoformat()

        if islem == 'kaydet':
            if not fingerprint:
                return "Hata: 'fingerprint' parametresi zorunludur."
            if isinstance(fingerprint, str):
                try:
                    fingerprint = json.loads(fingerprint)
                except json.JSONDecodeError:
                    fingerprint = {"raw": fingerprint}

            if profil not in _FINGERPRINT_DB:
                _FINGERPRINT_DB[profil] = {}
            _FINGERPRINT_DB[profil] = {
                "fingerprint": fingerprint,
                "kayit_zamani": ts,
                "guncelleme": ts
            }
            _save_db()
            return f"Fingerprint kaydedildi (profil: {profil})."

        elif islem == 'oku':
            if profil not in _FINGERPRINT_DB:
                return f"Profil '{profil}' için fingerprint bulunamadı."
            data = _FINGERPRINT_DB[profil]
            return json.dumps(data, indent=2, ensure_ascii=False)

        elif islem == 'temizle':
            if profil in _FINGERPRINT_DB:
                del _FINGERPRINT_DB[profil]
                _save_db()
                return f"Profil '{profil}' fingerprint verisi temizlendi."
            return f"Profil '{profil}' zaten mevcut değil."

        elif islem == 'listele':
            if not _FINGERPRINT_DB:
                return "Kayıtlı fingerprint bulunamadı."
            liste = []
            for p, data in _FINGERPRINT_DB.items():
                kayit = data.get('kayit_zamani', 'bilinmiyor')
                liste.append(f"  - {p}: kayıt {kayit}")
            return "Kayıtlı fingerprint profilleri:\n" + "\n".join(liste)

        else:
            return f"Hata: Geçersiz işlem '{islem}'. 'kaydet', 'oku', 'temizle' veya 'listele' kullanın."

    except Exception as e:
        return f"Fingerprint durum hatası: {str(e)}"
