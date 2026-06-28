# -*- coding: utf-8 -*-
"""Testler: reymen.cereyan.mesaj_tamirci"""
import pytest
from reymen.cereyan.mesaj_tamirci import (
    arac_cagri_argumanlarini_temizle,
    mesaj_siralamasi_tamir_et,
    surrogate_karakterleri_temizle,
    sanitize_tool_call_arguments,
    repair_message_sequence,
)


# ── Alias testleri ────────────────────────────────────────────────────────────

class TestHermesAliaslar:
    def test_sanitize_alias(self):
        assert sanitize_tool_call_arguments is arac_cagri_argumanlarini_temizle

    def test_repair_alias(self):
        assert repair_message_sequence is mesaj_siralamasi_tamir_et


# ── arac_cagri_argumanlarini_temizle ─────────────────────────────────────────

class TestAracCagriArgumentanlariniTemizle:
    def test_bos_liste_sifir_doner(self):
        assert arac_cagri_argumanlarini_temizle([]) == 0

    def test_gecerli_argumanlar_dokunulmaz(self):
        mesajlar = [
            {
                "role": "assistant",
                "content": "",
                "tool_calls": [
                    {"id": "c1", "function": {"name": "arama", "arguments": '{"query":"test"}'}}
                ],
            }
        ]
        n = arac_cagri_argumanlarini_temizle(mesajlar)
        assert n == 0
        assert mesajlar[0]["tool_calls"][0]["function"]["arguments"] == '{"query":"test"}'

    def test_bozuk_json_arguman_temizlenir(self):
        mesajlar = [
            {
                "role": "assistant",
                "content": "",
                "tool_calls": [
                    {"id": "c1", "function": {"name": "yazdir", "arguments": '{"x": }'}}
                ],
            }
        ]
        n = arac_cagri_argumanlarini_temizle(mesajlar)
        assert n == 1
        assert mesajlar[0]["tool_calls"][0]["function"]["arguments"] == "{}"

    def test_bos_arguman_temizlenir(self):
        mesajlar = [
            {
                "role": "assistant",
                "content": "",
                "tool_calls": [
                    {"id": "c2", "function": {"name": "calistir", "arguments": ""}}
                ],
            }
        ]
        arac_cagri_argumanlarini_temizle(mesajlar)
        assert mesajlar[0]["tool_calls"][0]["function"]["arguments"] == "{}"

    def test_none_arguman_temizlenir(self):
        mesajlar = [
            {
                "role": "assistant",
                "content": "",
                "tool_calls": [
                    {"id": "c3", "function": {"name": "bir_sey", "arguments": None}}
                ],
            }
        ]
        arac_cagri_argumanlarini_temizle(mesajlar)
        assert mesajlar[0]["tool_calls"][0]["function"]["arguments"] == "{}"

    def test_bozuk_arguman_mevcut_tool_mesajina_isaret_eklenir(self):
        mesajlar = [
            {
                "role": "assistant",
                "content": "",
                "tool_calls": [
                    {"id": "c4", "function": {"name": "arac", "arguments": "BOZUK"}}
                ],
            },
            {
                "role": "tool",
                "tool_call_id": "c4",
                "content": "eski sonuc",
            },
        ]
        n = arac_cagri_argumanlarini_temizle(mesajlar)
        assert n == 1
        assert "[Uyarı:" in mesajlar[1]["content"]
        assert "eski sonuc" in mesajlar[1]["content"]

    def test_bozuk_arguman_eksik_tool_mesaji_eklenir(self):
        """Tool result mesajı yoksa yeni eklenmeli."""
        mesajlar = [
            {
                "role": "assistant",
                "content": "",
                "tool_calls": [
                    {"id": "c5", "function": {"name": "arac", "arguments": "{bozuk"}}
                ],
            },
        ]
        n = arac_cagri_argumanlarini_temizle(mesajlar)
        assert n == 1
        # Yeni bir tool mesajı eklenmeli
        assert len(mesajlar) == 2
        assert mesajlar[1]["role"] == "tool"
        assert mesajlar[1]["tool_call_id"] == "c5"

    def test_user_mesajlari_etkilenmez(self):
        mesajlar = [{"role": "user", "content": "merhaba"}]
        n = arac_cagri_argumanlarini_temizle(mesajlar)
        assert n == 0
        assert mesajlar == [{"role": "user", "content": "merhaba"}]

    def test_oturum_id_gecilir(self):
        mesajlar = [
            {
                "role": "assistant",
                "content": "",
                "tool_calls": [
                    {"id": "x1", "function": {"name": "test", "arguments": "[bozuk"}}
                ],
            }
        ]
        # Hata olmadan çalışmalı
        n = arac_cagri_argumanlarini_temizle(mesajlar, oturum_id="test-session-123")
        assert n == 1

    def test_bos_bosluk_arguman_temizlenir(self):
        mesajlar = [
            {
                "role": "assistant",
                "content": "",
                "tool_calls": [
                    {"id": "ws", "function": {"name": "bos", "arguments": "   "}}
                ],
            }
        ]
        arac_cagri_argumanlarini_temizle(mesajlar)
        assert mesajlar[0]["tool_calls"][0]["function"]["arguments"] == "{}"


# ── mesaj_siralamasi_tamir_et ─────────────────────────────────────────────────

class TestMesajSiralamasiTamirEt:
    def test_bos_liste(self):
        assert mesaj_siralamasi_tamir_et([]) == 0

    def test_normal_akis_dokunulmaz(self):
        mesajlar = [
            {"role": "user", "content": "Merhaba"},
            {"role": "assistant", "content": "Selam"},
            {"role": "user", "content": "Nasılsın?"},
        ]
        n = mesaj_siralamasi_tamir_et(mesajlar)
        assert n == 0
        assert len(mesajlar) == 3

    def test_ardisik_user_mesajlari_birlestir(self):
        mesajlar = [
            {"role": "user", "content": "Birinci mesaj"},
            {"role": "user", "content": "İkinci mesaj"},
        ]
        n = mesaj_siralamasi_tamir_et(mesajlar)
        assert n == 1
        assert len(mesajlar) == 1
        assert "Birinci mesaj" in mesajlar[0]["content"]
        assert "İkinci mesaj" in mesajlar[0]["content"]

    def test_uc_ardisik_user_birlestir(self):
        mesajlar = [
            {"role": "user", "content": "A"},
            {"role": "user", "content": "B"},
            {"role": "user", "content": "C"},
        ]
        n = mesaj_siralamasi_tamir_et(mesajlar)
        assert n == 2
        assert len(mesajlar) == 1
        assert "A" in mesajlar[0]["content"]
        assert "C" in mesajlar[0]["content"]

    def test_yetim_tool_atilir(self):
        """tool mesajının eşleşen assistant tool_call_id'si yoksa at."""
        mesajlar = [
            {"role": "user", "content": "Bir şey yap"},
            {"role": "tool", "tool_call_id": "yok-olan-id", "content": "sonuc"},
            {"role": "assistant", "content": "Tamam"},
        ]
        n = mesaj_siralamasi_tamir_et(mesajlar)
        assert n == 1
        # Yetim tool mesajı atılmış olmalı
        roller = [m.get("role") for m in mesajlar]
        assert "tool" not in roller

    def test_gecerli_tool_kalir(self):
        """Eşleşen assistant tool_call_id olan tool mesajı korunmalı."""
        mesajlar = [
            {"role": "user", "content": "Bir şey yap"},
            {
                "role": "assistant",
                "content": "",
                "tool_calls": [{"id": "tc1", "function": {"name": "arac"}}],
            },
            {"role": "tool", "tool_call_id": "tc1", "content": "sonuc"},
        ]
        n = mesaj_siralamasi_tamir_et(mesajlar)
        assert n == 0
        assert len(mesajlar) == 3

    def test_karisik_senaryo(self):
        """Hem yetim tool hem ardışık user: ikisi de tamir edilmeli."""
        mesajlar = [
            {"role": "user", "content": "İlk"},
            {"role": "user", "content": "İkinci"},  # ardışık → birleştir
            {"role": "tool", "tool_call_id": "hayalet", "content": "yetim"},  # yetim → at
        ]
        n = mesaj_siralamasi_tamir_et(mesajlar)
        assert n >= 2
        roller = [m.get("role") for m in mesajlar]
        assert "tool" not in roller
        assert roller.count("user") == 1

    def test_multimodal_user_birlestirme_yok(self):
        """List content'li user mesajları birleştirilmemeli."""
        mesajlar = [
            {"role": "user", "content": [{"type": "text", "text": "resme bak"}]},
            {"role": "user", "content": "açıkla"},
        ]
        onceki_uzunluk = len(mesajlar)
        mesaj_siralamasi_tamir_et(mesajlar)
        # List content olanlar birleştirilmemeli
        assert len(mesajlar) == onceki_uzunluk

    def test_yerinde_degisir(self):
        """Fonksiyon mesajlar listesini yerinde değiştirmeli."""
        mesajlar = [
            {"role": "user", "content": "A"},
            {"role": "user", "content": "B"},
        ]
        referans = mesajlar
        mesaj_siralamasi_tamir_et(mesajlar)
        assert mesajlar is referans  # Aynı obje


# ── surrogate_karakterleri_temizle ───────────────────────────────────────────

class TestSurrogateKarakterleriTemizle:
    def test_normal_metin_degismez(self):
        metin = "Merhaba dünya!"
        assert surrogate_karakterleri_temizle(metin) == metin

    def test_string_olmayan_aynen_doner(self):
        assert surrogate_karakterleri_temizle(123) == 123  # type: ignore[arg-type]
        assert surrogate_karakterleri_temizle(None) is None  # type: ignore[arg-type]

    def test_bos_string_calisir(self):
        assert surrogate_karakterleri_temizle("") == ""

    def test_ascii_metin_calisir(self):
        metin = "Hello World 123"
        assert surrogate_karakterleri_temizle(metin) == metin

    def test_turkce_karakterler_calisir(self):
        metin = "şçğüıöÖÜİĞÇŞ"
        sonuc = surrogate_karakterleri_temizle(metin)
        assert isinstance(sonuc, str)
        assert len(sonuc) > 0
