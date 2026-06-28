# -*- coding: utf-8 -*-
"""gateway/platforms/yuanbao_media.py testleri."""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest


class TestGuessMimeType:
    def test_image_types(self):
        from gateway.platforms.yuanbao_media import guess_mime_type
        assert guess_mime_type("foto.jpg") == "image/jpeg"
        assert guess_mime_type("foto.jpeg") == "image/jpeg"
        assert guess_mime_type("foto.png") == "image/png"
        assert guess_mime_type("foto.gif") == "image/gif"
        assert guess_mime_type("foto.webp") == "image/webp"
        assert guess_mime_type("foto.bmp") == "image/bmp"

    def test_document_types(self):
        from gateway.platforms.yuanbao_media import guess_mime_type
        assert guess_mime_type("belge.pdf") == "application/pdf"
        assert guess_mime_type("belge.docx") == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        assert guess_mime_type("belge.txt") == "text/plain"

    def test_audio_video(self):
        from gateway.platforms.yuanbao_media import guess_mime_type
        assert guess_mime_type("ses.mp3") == "audio/mpeg"
        assert guess_mime_type("video.mp4") == "video/mp4"

    def test_unknown(self):
        from gateway.platforms.yuanbao_media import guess_mime_type
        assert guess_mime_type("dosya.xyz") == "application/octet-stream"


class TestIsImage:
    def test_image_by_mime(self):
        from gateway.platforms.yuanbao_media import is_image
        assert is_image("test.jpg", "image/jpeg") is True
        assert is_image("test.xyz", "image/png") is True

    def test_image_by_ext(self):
        from gateway.platforms.yuanbao_media import is_image
        assert is_image("test.jpg") is True
        assert is_image("test.png") is True
        assert is_image("test.gif") is True
        assert is_image("test.pdf") is False
        assert is_image("test.mp4", "video/mp4") is False


class TestGetImageFormat:
    def test_get_image_format_known(self):
        from gateway.platforms.yuanbao_media import get_image_format
        assert get_image_format("image/jpeg") == 1
        assert get_image_format("image/png") == 3
        assert get_image_format("image/gif") == 2
        assert get_image_format("image/webp") == 255

    def test_get_image_format_unknown(self):
        from gateway.platforms.yuanbao_media import get_image_format
        assert get_image_format("application/pdf") == 255
        assert get_image_format("") == 255


class TestBuildImageMsgBody:
    def test_build_image_msg_body(self):
        from gateway.platforms.yuanbao_media import build_image_msg_body
        result = build_image_msg_body(
            url="https://cdn.example.com/img.jpg",
            uuid="abc123",
            size=1024,
            width=800,
            height=600,
            mime_type="image/jpeg",
        )
        assert len(result) == 1
        assert result[0]["msg_type"] == "TIMImageElem"
        assert result[0]["msg_content"]["uuid"] == "abc123"
        assert result[0]["msg_content"]["image_format"] == 1
        assert result[0]["msg_content"]["image_info_array"][0]["width"] == 800
        assert result[0]["msg_content"]["image_info_array"][0]["height"] == 600
        assert result[0]["msg_content"]["image_info_array"][0]["url"] == "https://cdn.example.com/img.jpg"

    def test_build_image_msg_body_default_uuid(self):
        from gateway.platforms.yuanbao_media import build_image_msg_body
        result = build_image_msg_body(
            url="https://cdn.example.com/path/foto.jpg",
            filename="foto.jpg",
            mime_type="image/png",
        )
        assert result[0]["msg_content"]["image_format"] == 3


class TestBuildFileMsgBody:
    def test_build_file_msg_body(self):
        from gateway.platforms.yuanbao_media import build_file_msg_body
        result = build_file_msg_body(
            url="https://cdn.example.com/doc.pdf",
            filename="rapor.pdf",
            uuid="file123",
            size=2048,
        )
        assert len(result) == 1
        assert result[0]["msg_type"] == "TIMFileElem"
        assert result[0]["msg_content"]["uuid"] == "file123"
        assert result[0]["msg_content"]["file_name"] == "rapor.pdf"
        assert result[0]["msg_content"]["file_size"] == 2048
        assert result[0]["msg_content"]["url"] == "https://cdn.example.com/doc.pdf"

    def test_build_file_msg_body_default_uuid(self):
        from gateway.platforms.yuanbao_media import build_file_msg_body
        result = build_file_msg_body("https://example.com/f.txt", "f.txt")
        assert result[0]["msg_content"]["uuid"] == "f.txt"


class TestMD5Hex:
    def test_md5_hex(self):
        from gateway.platforms.yuanbao_media import md5_hex
        result = md5_hex(b"test data")
        assert isinstance(result, str)
        assert len(result) == 32
        assert result == __import__("hashlib").md5(b"test data").hexdigest()


class TestConstants:
    def test_constants(self):
        from gateway.platforms.yuanbao_media import (
            UPLOAD_INFO_PATH,
            DEFAULT_API_DOMAIN,
            DEFAULT_MAX_SIZE_MB,
            COS_USE_ACCELERATE,
        )
        assert UPLOAD_INFO_PATH == "/api/resource/genUploadInfo"
        assert DEFAULT_API_DOMAIN == "yuanbao.tencent.com"
        assert DEFAULT_MAX_SIZE_MB == 50
        assert COS_USE_ACCELERATE is True


class TestBasenameFromUrl:
    def test_basename(self):
        from gateway.platforms.yuanbao_media import _basename_from_url
        assert _basename_from_url("http://example.com/path/foto.jpg") == "foto.jpg"
        assert _basename_from_url("http://example.com/") == ""
        assert _basename_from_url("") == ""
