# -*- coding: utf-8 -*-
"""gateway/platforms/wecom_crypto.py testleri."""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest


class TestWeComCryptoExceptions:
    def test_exceptions_are_subclasses(self):
        from gateway.platforms.wecom_crypto import WeComCryptoError, SignatureError, DecryptError, EncryptError
        assert issubclass(SignatureError, WeComCryptoError)
        assert issubclass(DecryptError, WeComCryptoError)
        assert issubclass(EncryptError, WeComCryptoError)


class TestPKCS7Encoder:
    def test_encode_pads(self):
        from gateway.platforms.wecom_crypto import PKCS7Encoder
        encoded = PKCS7Encoder.encode(b"test")
        assert len(encoded) == 32  # 32 is block_size
        assert encoded[:4] == b"test"
        assert encoded[-1] == 28  # 28 bytes of padding

    def test_encode_exact_block(self):
        from gateway.platforms.wecom_crypto import PKCS7Encoder
        data = b"a" * 32
        encoded = PKCS7Encoder.encode(data)
        assert len(encoded) == 64  # one full extra block
        assert encoded[-1] == 32

    def test_decode_valid(self):
        from gateway.platforms.wecom_crypto import PKCS7Encoder
        data = b"test" + b"\x1c" * 28
        decoded = PKCS7Encoder.decode(data)
        assert decoded == b"test"

    def test_decode_invalid_padding(self):
        from gateway.platforms.wecom_crypto import PKCS7Encoder, DecryptError
        # padding byte > block_size
        with pytest.raises(DecryptError):
            PKCS7Encoder.decode(b"test" + b"\x40" * 28)

    def test_decode_malformed_padding(self):
        from gateway.platforms.wecom_crypto import PKCS7Encoder, DecryptError
        # 33 bytes of 0x21 padding (wrong value 33 > block_size 32)
        with pytest.raises(DecryptError):
            PKCS7Encoder.decode(b"test" + b"\x21" * 33)

    def test_decode_empty(self):
        from gateway.platforms.wecom_crypto import PKCS7Encoder, DecryptError
        with pytest.raises(DecryptError):
            PKCS7Encoder.decode(b"")


class TestSHA1Signature:
    def test_sha1_signature(self):
        from gateway.platforms.wecom_crypto import _sha1_signature
        sig = _sha1_signature("token", "1234567890", "nonce123", "encrypted_data")
        assert isinstance(sig, str)
        assert len(sig) == 40  # SHA1 hex digest length

    def test_sha1_signature_deterministic(self):
        from gateway.platforms.wecom_crypto import _sha1_signature
        sig1 = _sha1_signature("token", "ts", "n", "e")
        sig2 = _sha1_signature("token", "ts", "n", "e")
        assert sig1 == sig2


class TestWXBizMsgCrypt:
    def test_init_requires_token(self):
        from gateway.platforms.wecom_crypto import WXBizMsgCrypt
        with pytest.raises(ValueError, match="token is required"):
            WXBizMsgCrypt("", "a" * 43, "receive_id")

    def test_init_requires_key(self):
        from gateway.platforms.wecom_crypto import WXBizMsgCrypt
        with pytest.raises(ValueError, match="encoding_aes_key is required"):
            WXBizMsgCrypt("token", "", "receive_id")

    def test_init_requires_key_len(self):
        from gateway.platforms.wecom_crypto import WXBizMsgCrypt
        with pytest.raises(ValueError, match="must be 43 chars"):
            WXBizMsgCrypt("token", "short", "receive_id")

    def test_init_requires_receive_id(self):
        from gateway.platforms.wecom_crypto import WXBizMsgCrypt
        with pytest.raises(ValueError, match="receive_id is required"):
            WXBizMsgCrypt("token", "a" * 43, "")

    def test_init_success(self):
        from gateway.platforms.wecom_crypto import WXBizMsgCrypt
        crypt = WXBizMsgCrypt("my_token", "a" * 43, "my_receive_id")
        assert crypt.token == "my_token"
        assert crypt.receive_id == "my_receive_id"
        assert len(crypt.key) == 32

    def test_encrypt_decrypt_roundtrip(self):
        from gateway.platforms.wecom_crypto import WXBizMsgCrypt
        crypt = WXBizMsgCrypt("test_token", "a" * 43, "test_receive_id")

        plaintext = "<xml><Content>Merhaba</Content></xml>"
        encrypted_xml = crypt.encrypt(plaintext, nonce="nonce123", timestamp="1234567890")

        # Assert XML structure
        assert "<xml>" in encrypted_xml
        assert "<Encrypt>" in encrypted_xml
        assert "<MsgSignature>" in encrypted_xml
        assert "<TimeStamp>" in encrypted_xml
        assert "<Nonce>" in encrypted_xml

    def test_encrypt_generates_nonce(self):
        from gateway.platforms.wecom_crypto import WXBizMsgCrypt
        crypt = WXBizMsgCrypt("test_token", "a" * 43, "test_receive_id")
        xml1 = crypt.encrypt("test", nonce="abc", timestamp="123")
        xml2 = crypt.encrypt("test", nonce="def", timestamp="456")
        assert xml1 != xml2

    def test_decrypt_raises_on_bad_signature(self):
        from gateway.platforms.wecom_crypto import WXBizMsgCrypt, SignatureError
        crypt = WXBizMsgCrypt("token", "a" * 43, "receive_id")
        with pytest.raises(SignatureError, match="signature mismatch"):
            crypt.decrypt("bad_sig", "ts", "nonce", "encrypted")

    def test_decrypt_raises_on_bad_base64(self):
        from gateway.platforms.wecom_crypto import WXBizMsgCrypt, DecryptError, SignatureError
        crypt = WXBizMsgCrypt("token", "a" * 43, "receive_id")
        from gateway.platforms.wecom_crypto import _sha1_signature
        sig = _sha1_signature("token", "ts", "nonce", "!!!invalid base64!!!")
        with pytest.raises(DecryptError):
            crypt.decrypt(sig, "ts", "nonce", "!!!invalid base64!!!")

    def test_verify_url_calls_decrypt(self):
        from gateway.platforms.wecom_crypto import WXBizMsgCrypt, SignatureError
        crypt = WXBizMsgCrypt("token", "a" * 43, "receive_id")
        with pytest.raises(SignatureError):
            crypt.verify_url("bad", "ts", "n", "e")

    def test_random_nonce_length(self):
        from gateway.platforms.wecom_crypto import WXBizMsgCrypt
        nonce = WXBizMsgCrypt._random_nonce()
        assert len(nonce) == 10

    def test_random_nonce_alphabet(self):
        from gateway.platforms.wecom_crypto import WXBizMsgCrypt
        import string
        valid = set(string.ascii_letters + string.digits)
        for _ in range(10):
            nonce = WXBizMsgCrypt._random_nonce()
            assert all(c in valid for c in nonce)
