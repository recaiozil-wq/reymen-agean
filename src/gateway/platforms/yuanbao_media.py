# -*- coding: utf-8 -*-
"""Yuanbao media utilities — MIME types, image/file message builders."""

from __future__ import annotations

import hashlib
import os
from typing import Any, Dict, List, Optional


# ── Constants ───────────────────────────────────────────────────────────────

UPLOAD_INFO_PATH = "/api/resource/genUploadInfo"
DEFAULT_API_DOMAIN = "yuanbao.tencent.com"
DEFAULT_MAX_SIZE_MB = 50
COS_USE_ACCELERATE = True

_MIME_MAP = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".gif": "image/gif",
    ".webp": "image/webp",
    ".bmp": "image/bmp",
    ".pdf": "application/pdf",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".txt": "text/plain",
    ".mp3": "audio/mpeg",
    ".mp4": "video/mp4",
}

_IMAGE_FORMAT_MAP = {
    "image/jpeg": 1,
    "image/gif": 2,
    "image/png": 3,
    "image/webp": 255,
}

_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"}


# ── Functions ───────────────────────────────────────────────────────────────


def guess_mime_type(filename: str) -> str:
    ext = os.path.splitext(filename)[1].lower()
    return _MIME_MAP.get(ext, "application/octet-stream")


def is_image(filename: str, mime_type: str = "") -> bool:
    ext = os.path.splitext(filename)[1].lower()
    if ext in _IMAGE_EXTENSIONS:
        return True
    if mime_type and mime_type.startswith("image/"):
        return True
    return False


def get_image_format(mime_type: str) -> int:
    return _IMAGE_FORMAT_MAP.get(mime_type, 255)


def build_image_msg_body(
    url: str,
    filename: str = "",
    uuid: str = "",
    size: int = 0,
    width: int = 0,
    height: int = 0,
    mime_type: str = "image/jpeg",
) -> List[Dict[str, Any]]:
    if not uuid:
        uuid = filename or _basename_from_url(url)
    fmt = get_image_format(mime_type)
    return [
        {
            "msg_type": "TIMImageElem",
            "msg_content": {
                "uuid": uuid,
                "image_format": fmt,
                "image_info_array": [
                    {
                        "url": url,
                        "width": width,
                        "height": height,
                        "size": size,
                    }
                ],
            },
        }
    ]


def build_file_msg_body(
    url: str,
    filename: str = "",
    uuid: str = "",
    size: int = 0,
) -> List[Dict[str, Any]]:
    if not uuid:
        uuid = filename or _basename_from_url(url)
    return [
        {
            "msg_type": "TIMFileElem",
            "msg_content": {
                "uuid": uuid,
                "file_name": filename,
                "file_size": size,
                "url": url,
            },
        }
    ]


def md5_hex(data: bytes) -> str:
    return hashlib.md5(data).hexdigest()


def _basename_from_url(url: str) -> str:
    from urllib.parse import urlparse
    path = urlparse(url).path
    return os.path.basename(path)
