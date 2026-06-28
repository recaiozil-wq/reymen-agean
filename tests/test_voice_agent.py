#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_voice_agent.py — VoiceMode birim testleri."""

import sys
sys.path.insert(0, ".")

from agent.voice_agent import VoiceMode, voice_mode


class TestVoiceModeInit:
    """VoiceMode baslatma testleri."""

    def test_init_bos_config(self):
        vm = VoiceMode({})
        assert vm._varsayilan_ses == "tr-TR-AhmetNeural"
        assert vm._varsayilan_sure == 5
        assert vm._arka_tts is True
        assert vm.ping() is True

    def test_init_ozel_config(self):
        vm = VoiceMode({"voice": {
            "default_voice": "tr-TR-EmelNeural",
            "listen_seconds": 10,
            "fallback_tts": False,
        }})
        assert vm._varsayilan_ses == "tr-TR-EmelNeural"
        assert vm._varsayilan_sure == 10
        assert vm._arka_tts is False

    def test_init_config_yok(self):
        vm = VoiceMode()
        assert vm._varsayilan_ses == "tr-TR-AhmetNeural"
        assert vm._varsayilan_sure == 5

    def test_singleton(self):
        vm1 = voice_mode({"voice": {}})
        vm2 = voice_mode()
        assert vm1 is vm2


class TestVoiceModeKomut:
    """/voice komutu testleri."""

    def test_komut_bos(self):
        vm = VoiceMode({})
        r = vm.komut_islem("")
        assert "ReYMeN Ses Modu" in r
        assert "edge-tts" in r
        assert "Komutlar" in r

    def test_komut_status(self):
        vm = VoiceMode({})
        r = vm.komut_islem("status")
        assert "ReYMeN Ses Modu" in r

    def test_komut_konus_bos(self):
        vm = VoiceMode({})
        r = vm.komut_islem("konus")
        assert "Kullanım" in r

    def test_komut_konus(self):
        vm = VoiceMode({})
        # edge-tts yoksa da fallback mesaji doner
        r = vm.komut_islem("konus Merhaba")
        # Ya "[Ses] edge-tts" ya da "[Hata]: Kullanilabilir TTS backend'i yok."
        assert r.startswith("[Ses]") or r.startswith("[Hata]")

    def test_komut_dinle(self):
        vm = VoiceMode({})
        r = vm.komut_islem("dinle")
        # speech_recognition yoksa "[Hata]: speech_recognition"
        # yoksa "[Ses] Alinan metin: ..." veya "[Ses] Ses anlasilamadi"
        assert ("[Hata]" in r or "[Ses]" in r)

    def test_komut_ses_goster(self):
        vm = VoiceMode({})
        r = vm.komut_islem("ses")
        assert "Gecerli ses:" in r

    def test_komut_ses_degistir(self):
        vm = VoiceMode({})
        r = vm.komut_islem("ses tr-TR-EmelNeural")
        assert "degistirildi" in r
        assert vm._varsayilan_ses == "tr-TR-EmelNeural"

    def test_komut_test(self):
        vm = VoiceMode({})
        r = vm.komut_islem("test")
        assert r.startswith("[Ses]") or r.startswith("[Hata]")

    def test_komut_bilinmeyen(self):
        vm = VoiceMode({})
        r = vm.komut_islem("olmayan_komut")
        assert "Bilinmeyen" in r

    def test_komut_dinle_sure(self):
        vm = VoiceMode({})
        r = vm.komut_islem("dinle 3")
        assert ("[Hata]" in r or "[Ses]" in r)


class TestVoiceModeTTS:
    """TTS testleri (backend yoksa fallback mesaji)."""

    def test_konus_bos(self):
        vm = VoiceMode({})
        r = vm.konus("")
        assert "Hata" in r

    def test_konus_bosluk(self):
        vm = VoiceMode({})
        r = vm.konus("   ")
        assert "Hata" in r

    def test_konus_normal(self):
        vm = VoiceMode({})
        r = vm.konus("Merhaba dunya")
        # edge-tts yoksa "[Hata]": Kullanilabilir TTS backend'i yok"
        # varsa dosya yolu doner
        assert r.startswith("[Ses]") or r.startswith("[Hata]")

    def test_konus_dosyaya(self):
        vm = VoiceMode({})
        dosya = vm.konus_dosyaya("Merhaba")
        if vm.edge_tts:
            assert dosya is not None
            assert dosya.endswith(".mp3")
        else:
            assert dosya is None

    def test_konus_ozel_ses(self):
        vm = VoiceMode({})
        r = vm.konus("Test", ses="tr-TR-EmelNeural")
        assert r.startswith("[Ses]") or r.startswith("[Hata]")


class TestVoiceModeSTT:
    """STT testleri (backend yoksa fallback)."""

    def test_dinle_normal(self):
        vm = VoiceMode({})
        r = vm.dinle(2)
        if vm.speech_rec:
            # Mikrofon yoksa "[Ses] Ses anlasilamadi"
            # varsa "[Ses] Alinan metin: ..."
            assert "[Ses]" in r
        else:
            assert "[Hata]" in r

    def test_dinle_default_sure(self):
        vm = VoiceMode({})
        r = vm.dinle()
        # Varsayilan sure 5
        if vm.speech_rec:
            assert "[Ses]" in r
        else:
            assert "[Hata]" in r


class TestVoiceModeDurum:
    """Durum gosterme testi."""

    def test_durum(self):
        vm = VoiceMode({})
        r = vm._durum_goster()
        assert "Varsayilan ses" in r
        assert "edge-tts" in r
        assert "SAPI" in r
        assert "STT" in r
        assert "konus" in r
