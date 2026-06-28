# -*- coding: utf-8 -*-
"""gateway/platforms/yuanbao_media.py — Yuanbao Medya Gonderme.

Gorsel, video, dosya paylasimi. HTTP multipart ile.
"""

import os
import json
import logging

try:
    import requests
    _REQUESTS_OK = True
except ImportError:
    _REQUESTS_OK = False

logger = logging.getLogger(__name__)

_BASE_URL = "https://api.yuanbao.cn/v1"
_DESTEK_MEDYA = frozenset({"image", "video", "document", "audio", "file"})


def _token_al() -> str:
    token = os.environ.get("YUANBAO_TOKEN", "")
    if token and not token.startswith("***"):
        return token
    return ""


def send_message(hedef: str, mesaj: str, medya_yolu: str = None, medya_turu: str = "image", **kwargs) -> dict:
    """Yuanbao'ya medya dosyasi gonderir.

    Args:
        hedef: Grup kodu veya kullanici ID'si
        mesaj: Mesaj icerigi (caption/aciklama)
        medya_yolu: Medya dosyasi yolu (yerel)
        medya_turu: Medya tipi (image, video, document, audio, file)

    Keyword Args:
        dosya_url: Dogrudan URL ile gonderme (medya_yolu yerine)
        dosya_adi: Gonderilecek dosya adi (opsiyonel)
        caption: Mesaj alt yazisi (mesaj parametresi ile ayni)

    Returns:
        dict: {"durum": "basarili", ...} veya {"durum": "hata", ...}
    """
    if not _REQUESTS_OK:
        return {"durum": "hata", "hata": "requests kutuphanesi yok."}

    token = _token_al()
    if not token:
        return {"durum": "hata", "hata": "YUANBAO_TOKEN ayarlanmamis."}

    if medya_turu not in _DESTEK_MEDYA:
        return {"durum": "hata", "hata": f"Desteklenmeyen medya turu: {medya_turu}. Su desteklenir: {', '.join(sorted(_DESTEK_MEDYA))}"}

    caption = kwargs.get("caption", mesaj)
    headers = {"Authorization": f"Bearer {token}"}

    try:
        if medya_yolu:
            # Yerel dosyadan multipart upload
            dosya_adi = kwargs.get("dosya_adi", os.path.basename(medya_yolu))
            with open(medya_yolu, "rb") as f:
                files = {
                    "file": (dosya_adi, f, _mime_turu(medya_turu, dosya_adi)),
                    "type": (None, medya_turu),
                    "caption": (None, caption[:2000]),
                    "target": (None, hedef),
                }
                r = requests.post(
                    f"{_BASE_URL}/media/upload",
                    files=files,
                    headers=headers,
                    timeout=60,
                )
        elif kwargs.get("dosya_url"):
            # URL'den indirip gonder
            dosya_url = kwargs["dosya_url"]
            r = requests.post(
                f"{_BASE_URL}/media/send",
                json={
                    "target": hedef,
                    "type": medya_turu,
                    "url": dosya_url,
                    "caption": caption[:2000],
                },
                headers={**headers, "Content-Type": "application/json"},
                timeout=30,
            )
        else:
            # Sadece mesaj gonder (medyasiz)
            r = requests.post(
                f"{_BASE_URL}/groups/{hedef}/messages",
                json={"content": caption[:2000]},
                headers={**headers, "Content-Type": "application/json"},
                timeout=10,
            )

        data = r.json()
        if r.status_code == 200:
            return {"durum": "basarili", "yanit": data}
        return {"durum": "hata", "hata": f"API hatasi {r.status_code}: {data}"}

    except FileNotFoundError:
        return {"durum": "hata", "hata": f"Dosya bulunamadi: {medya_yolu}"}
    except Exception as e:
        return {"durum": "hata", "hata": str(e)}


def _mime_turu(medya_turu: str, dosya_adi: str = "") -> str:
    """Medya tipine gore MIME turu doner."""
    mime_map = {
        "image": "image/jpeg",
        "video": "video/mp4",
        "document": "application/pdf",
        "audio": "audio/mpeg",
        "file": "application/octet-stream",
    }
    if dosya_adi:
        ext = os.path.splitext(dosya_adi)[1].lower()
        ext_mime = {
            ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png",
            ".gif": "image/gif", ".webp": "image/webp",
            ".mp4": "video/mp4", ".mov": "video/quicktime", ".avi": "video/x-msvideo",
            ".mp3": "audio/mpeg", ".wav": "audio/wav", ".ogg": "audio/ogg",
            ".pdf": "application/pdf", ".doc": "application/msword",
            ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            ".zip": "application/zip",
        }
        if ext in ext_mime:
            return ext_mime[ext]
    return mime_map.get(medya_turu, "application/octet-stream")


def ping() -> bool:
    """Yuanbao baglantisini kontrol eder.

    Returns:
        bool: Token varsa ve API ulasilabilirse True
    """
    token = _token_al()
    if not token:
        return False
    try:
        r = requests.get(
            f"{_BASE_URL}/ping",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10,
        )
        return r.status_code == 200
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Upstream Hermes uyumluluk fonksiyonlari
# ---------------------------------------------------------------------------

_MIME_GUESS: dict[str, str] = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".gif": "image/gif",
    ".webp": "image/webp",
    ".bmp": "image/bmp",
    ".svg": "image/svg+xml",
    ".mp4": "video/mp4",
    ".mov": "video/quicktime",
    ".avi": "video/x-msvideo",
    ".mkv": "video/x-matroska",
    ".mp3": "audio/mpeg",
    ".wav": "audio/wav",
    ".ogg": "audio/ogg",
    ".flac": "audio/flac",
    ".pdf": "application/pdf",
    ".doc": "application/msword",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".xls": "application/vnd.ms-excel",
    ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ".zip": "application/zip",
    ".tar": "application/x-tar",
    ".gz": "application/gzip",
    ".json": "application/json",
    ".xml": "application/xml",
    ".txt": "text/plain",
    ".html": "text/html",
    ".css": "text/css",
    ".js": "text/javascript",
    ".py": "text/x-python",
}

_IMAGE_EXTENSIONS: frozenset = frozenset({".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".svg"})

_IMAGE_MIME_PREFIXES: tuple = ("image/",)


def guess_mime_type(filename: str, default: str = "application/octet-stream") -> str:
    """Dosya adindan MIME turu tahmin et.

    Args:
        filename: Dosya adi veya yolu
        default: Varsayilan MIME turu

    Returns:
        str: MIME turu
    """
    ext = os.path.splitext(filename)[1].lower() if "." in filename else ""
    return _MIME_GUESS.get(ext, default)


def is_image(filename: str, mime: str = "") -> bool:
    """Dosya adi veya MIME turune gore gorsel mi?

    Args:
        filename: Dosya adi
        mime: MIME turu (opsiyonel)

    Returns:
        bool: Gorselse True
    """
    if mime and mime.startswith(_IMAGE_MIME_PREFIXES):
        return True
    ext = os.path.splitext(filename)[1].lower() if "." in filename else ""
    return ext in _IMAGE_EXTENSIONS


# ---------------------------------------------------------------------------
# Upstream Hermes uyumluluk: mesaj govdesi olusturma
# ---------------------------------------------------------------------------

UPLOAD_INFO_PATH: str = "/api/resource/genUploadInfo"
DEFAULT_API_DOMAIN: str = "yuanbao.tencent.com"  # media-specific
DEFAULT_MAX_SIZE_MB: int = 50
COS_USE_ACCELERATE: bool = True

_IMAGE_FORMAT_MAP: dict[str, int] = {
    "image/jpeg": 1,
    "image/gif": 2,
    "image/png": 3,
    "image/bmp": 4,
    "image/webp": 255,
}


def get_image_format(mime_type: str) -> int:
    """MIME turune gore TIM resim format kodu.

    Args:
        mime_type: MIME turu (ornek: ``image/jpeg``)

    Returns:
        int: TIMImageElem format kodu (255 = unknown/webp)
    """
    return _IMAGE_FORMAT_MAP.get(mime_type, 255)


def build_image_msg_body(
    url: str,
    uuid: str | None = None,
    size: int = 0,
    width: int = 0,
    height: int = 0,
    mime_type: str | None = None,
    filename: str | None = None,
) -> list[dict]:
    """TIMImageElem mesaj govdesi olustur.

    Args:
        url: Resim URL'si
        uuid: Benzersiz ID (None ise filename veya URL'den cikar)
        size: Dosya boyutu (byte)
        width: Gorsel genisligi (px)
        height: Gorsel yuksekligi (px)
        mime_type: MIME turu (None ise filename/URL'den tahmin)
        filename: Dosya adi

    Returns:
        list[dict]: ``[{"msg_type": "TIMImageElem", ...}]``
    """
    if uuid is None:
        if filename:
            uuid = filename
        else:
            uuid = os.path.basename(url.rstrip("/")) or url
    if mime_type is None:
        mime_type = guess_mime_type(filename or url)

    return [{
        "msg_type": "TIMImageElem",
        "msg_content": {
            "uuid": uuid,
            "image_format": get_image_format(mime_type),
            "image_info_array": [{
                "url": url,
                "width": width,
                "height": height,
                "size": size,
            }],
        },
    }]


def build_file_msg_body(
    url: str,
    filename: str,
    uuid: str | None = None,
    size: int = 0,
) -> list[dict]:
    """TIMFileElem mesaj govdesi olustur.

    Args:
        url: Dosya URL'si
        filename: Dosya adi
        uuid: Benzersiz ID (None ise filename kullanilir)
        size: Dosya boyutu (byte)

    Returns:
        list[dict]: ``[{"msg_type": "TIMFileElem", ...}]``
    """
    if uuid is None:
        uuid = filename

    return [{
        "msg_type": "TIMFileElem",
        "msg_content": {
            "uuid": uuid,
            "file_name": filename,
            "file_size": size,
            "url": url,
        },
    }]


def md5_hex(data: bytes) -> str:
    """Bytes verinin MD5 hash'ini hexadecimal string olarak dondur.

    Args:
        data: Hash'lenecek bytes veri

    Returns:
        str: 32 karakterlik MD5 hexdigest
    """
    import hashlib
    return hashlib.md5(data).hexdigest()


def _basename_from_url(url: str) -> str:
    """URL'den dosya adini cikar.

    Args:
        url: HTTP URL

    Returns:
        str: Dosya adi (veya bos)
    """
    if not url or url.endswith("/"):
        return ""
    return os.path.basename(url.rstrip("/"))
