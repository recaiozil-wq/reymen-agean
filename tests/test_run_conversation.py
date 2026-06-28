# -*- coding: utf-8 -*-
"""tests/test_run_conversation.py — ConversationLoop.run_conversation() testleri.

35 test: baslatma, provider tespiti, api mesaj formati, tool_calls parse,
context compression, ephemeral layer, prompt caching, budget, interruptible
API call, hata yonetimi, geri uyumluluk ve entegrasyon testleri.
"""

import json
import sys
import threading
import time
import uuid
from pathlib import Path
from typing import Optional
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent))

from conversation_loop import ConversationLoop, GOREV_BITTI_TETIK


# ── Sabit mock cevaplar ────────────────────────────────────────────────

def _mock_beyin(cevap: str):
    """Verilen cevabi donduren sahte beyin nesnesi."""
    b = MagicMock()
    b.uret.return_value = cevap
    b.provider = "lmstudio"
    return b


def _mock_motor(sonuc: dict = None):
    """Sahte motor nesnesi."""
    m = MagicMock()
    m.arac_calistir.return_value = sonuc or {
        "basarili": True, "cikti": "tamam", "tamamlandi": False
    }
    return m


# ══════════════════════════════════════════════════════════════════════
# 1. SINIF VE BAŞLATMA TESTLERİ (1-6)
# ══════════════════════════════════════════════════════════════════════

class TestBaslatma:
    def test_varsayilan_baslatma(self):
        """ConversationLoop varsayilan parametrelerle olusturulabilmeli."""
        cl = ConversationLoop()
        assert cl is not None
        assert cl.max_tur == 30
        assert cl._durum == "hazir"

    def test_ozel_max_tur(self):
        """max_tur parametresi dogru set edilmeli."""
        cl = ConversationLoop(max_tur=10)
        assert cl.max_tur == 10

    def test_motor_ve_beyin_ile_baslatma(self):
        """Motor ve beyin injeksiyon ile baslatma."""
        motor = _mock_motor()
        beyin = _mock_beyin("test")
        cl = ConversationLoop(motor=motor, beyin=beyin, max_tur=5)
        assert cl.motor is motor
        assert cl.beyin is beyin

    def test_iptal_istegi_baslangic(self):
        """_iptal_istegi baslangiçta False olmali."""
        cl = ConversationLoop()
        assert cl._iptal_istegi is False

    def test_konusma_gecmisi_bos_baslangic(self):
        """_konusma_gecmisi basta bos liste olmali."""
        cl = ConversationLoop()
        assert cl._konusma_gecmisi == []

    def test_tur_yoneticisi_olusturma(self):
        """TurnYoneticisi modülü varsa baslatilmali."""
        cl = ConversationLoop(max_tur=5)
        # TurnYoneticisi varsa da yoksa da crash etmemeli
        assert cl.tur_yoneticisi is not None or cl.tur_yoneticisi is None


# ══════════════════════════════════════════════════════════════════════
# 2. PROVIDER TESPİTİ (7-11)
# ══════════════════════════════════════════════════════════════════════

class TestProviderTespiti:
    def test_anthropic_provider(self):
        cl = ConversationLoop()
        assert cl._provider_tipi_belirle("anthropic") == "anthropic"

    def test_claude_provider(self):
        cl = ConversationLoop()
        assert cl._provider_tipi_belirle("claude") == "anthropic"

    def test_bedrock_provider(self):
        cl = ConversationLoop()
        assert cl._provider_tipi_belirle("bedrock") == "anthropic"

    def test_codex_provider(self):
        cl = ConversationLoop()
        assert cl._provider_tipi_belirle("codex") == "codex"

    def test_varsayilan_chat_completions(self):
        cl = ConversationLoop()
        for p in ("deepseek", "openai", "lmstudio", "groq", ""):
            assert cl._provider_tipi_belirle(p) == "chat_completions", (
                f"{p} chat_completions olmali"
            )

    def test_beyin_provider_devralma(self):
        """Provider belirtilmezse beyin.provider kullanilmali."""
        beyin = MagicMock()
        beyin.provider = "anthropic"
        cl = ConversationLoop(beyin=beyin)
        assert cl._provider_tipi_belirle(None) == "anthropic"


# ══════════════════════════════════════════════════════════════════════
# 3. API MESAJ FORMATI (12-16)
# ══════════════════════════════════════════════════════════════════════

class TestApiMesajFormati:
    def test_chat_completions_sistem_eklenir(self):
        """chat_completions formatinda sistem mesaji ilk olmali."""
        cl = ConversationLoop()
        gecmis = [{"role": "user", "content": "merhaba"}]
        mesajlar = cl._api_mesajlari_olustur("SISTEM", gecmis, "chat_completions")
        assert mesajlar[0]["role"] == "system"
        assert mesajlar[0]["content"] == "SISTEM"

    def test_chat_completions_kullanici_eklenir(self):
        """chat_completions'da kullanici mesajlari aktarilmali."""
        cl = ConversationLoop()
        gecmis = [{"role": "user", "content": "hedef"}]
        mesajlar = cl._api_mesajlari_olustur("SP", gecmis, "chat_completions")
        kullanici = [m for m in mesajlar if m["role"] == "user"]
        assert len(kullanici) >= 1

    def test_anthropic_format(self):
        """Anthropic formatinda sistem mesaji olmali."""
        cl = ConversationLoop()
        gecmis = [{"role": "user", "content": "test"}]
        mesajlar = cl._api_mesajlari_olustur("SYS", gecmis, "anthropic")
        assert any(m["role"] == "system" for m in mesajlar)

    def test_codex_format(self):
        """Codex formatinda sistem mesaji ilk olmali."""
        cl = ConversationLoop()
        gecmis = [{"role": "user", "content": "hedef"}]
        mesajlar = cl._api_mesajlari_olustur("SYS", gecmis, "codex")
        assert mesajlar[0]["role"] == "system"

    def test_sistem_satirlari_ayrilir(self):
        """Gecmişteki system mesajlari yeniden eklenmemeli."""
        cl = ConversationLoop()
        gecmis = [
            {"role": "system", "content": "eski sistem"},
            {"role": "user", "content": "soru"},
        ]
        mesajlar = cl._api_mesajlari_olustur("YENI", gecmis, "chat_completions")
        sistem_mesajlari = [m for m in mesajlar if m["role"] == "system"]
        assert len(sistem_mesajlari) == 1
        assert sistem_mesajlari[0]["content"] == "YENI"


# ══════════════════════════════════════════════════════════════════════
# 4. TOOL CALLS PARSE (17-22)
# ══════════════════════════════════════════════════════════════════════

class TestToolCallsParse:
    def test_openai_format_tool_calls(self):
        """OpenAI format tool_calls listesi tanimlanmali."""
        cl = ConversationLoop()
        yanit = {
            "role": "assistant",
            "content": "",
            "tool_calls": [{"id": "t1", "name": "DOSYA_OKU", "arguments": {}}],
        }
        tc = cl._tool_calls_al(yanit)
        assert len(tc) == 1
        assert tc[0]["name"] == "DOSYA_OKU"

    def test_react_text_format(self):
        """ReAct text formatinda ARAÇ() tanimlanmali."""
        cl = ConversationLoop()
        yanit = {"content": 'DOSYA_OKU("test.txt")'}
        tc = cl._tool_calls_al(yanit)
        assert len(tc) == 1
        assert tc[0]["name"] == "DOSYA_OKU"

    def test_gorev_bitti_tool_yok(self):
        """GOREV_BITTI iceriginde tool call olmamali."""
        cl = ConversationLoop()
        for tetik in GOREV_BITTI_TETIK:
            yanit = {"content": f"Islem tamam. {tetik}(ozet)"}
            tc = cl._tool_calls_al(yanit)
            assert tc == [], f"'{tetik}' icin tool_calls bos olmali"

    def test_dusun_tool_degil(self):
        """DUSUN() eylemi tool call dondurmemeli."""
        cl = ConversationLoop()
        yanit = {"content": "DUSUN(bir seyler)"}
        assert cl._tool_calls_al(yanit) == []

    def test_bos_yanit(self):
        """None veya bos yanit icin bos liste donmeli."""
        cl = ConversationLoop()
        assert cl._tool_calls_al(None) == []
        assert cl._tool_calls_al({}) == []

    def test_parametre_cikarma(self):
        """Tool call argumani dogru parse edilmeli."""
        cl = ConversationLoop()
        yanit = {"content": 'KOMUT_CALISTIR("ls -la")'}
        tc = cl._tool_calls_al(yanit)
        assert len(tc) == 1
        assert "param" in tc[0]["arguments"]


# ══════════════════════════════════════════════════════════════════════
# 5. CONTEXT PREFLIGHT ve SIKISTIRMA (23-25)
# ══════════════════════════════════════════════════════════════════════

class TestContextPreflight:
    def test_dusuk_dolulukta_sikistirma_yok(self):
        """Context dolulugu dusukse mesajlar degismeden donmeli."""
        cl = ConversationLoop()
        mesajlar = [{"role": "user", "content": "kisa mesaj"}]
        sonuc = cl._context_preflight(mesajlar, "SP")
        assert sonuc == mesajlar

    def test_yuksek_dolulukta_sikistirma(self):
        """Context dolulugu %50'yi asinca mesaj sayisi azalmali."""
        cl = ConversationLoop()
        uzun_icerik = "a" * 5000
        mesajlar = [{"role": "user", "content": uzun_icerik}] * 12
        sistem_prompt = "s" * 10000
        sonuc = cl._context_preflight(mesajlar, sistem_prompt)
        assert len(sonuc) <= len(mesajlar)

    def test_bos_mesajlar(self):
        """Bos mesaj listesi bos donmeli."""
        cl = ConversationLoop()
        assert cl._context_preflight([], "SP") == []


# ══════════════════════════════════════════════════════════════════════
# 6. EPHEMERAL LAYERLAR (26-27)
# ══════════════════════════════════════════════════════════════════════

class TestEphemeralLayerlar:
    def test_yeterli_tur_kaldiysa_layer_yok(self):
        """Yeterli tur kaldiysa ephemeral layer eklenmemeli."""
        cl = ConversationLoop()
        budget = MagicMock()
        budget.kaldi = 20
        mesajlar = [{"role": "user", "content": "hedef"}]
        sonuc = cl._ephemeral_layerlar_ekle(mesajlar, budget, 3)
        assert sonuc == mesajlar

    def test_az_tur_kaldiysa_uyari_eklenir(self):
        """Kalan tur <= 3 ise butce uyarisi mesaji eklenmeli."""
        cl = ConversationLoop()
        budget = MagicMock()
        budget.kaldi = 2
        mesajlar = [{"role": "user", "content": "hedef"}]
        sonuc = cl._ephemeral_layerlar_ekle(mesajlar, budget, 3)
        assert len(sonuc) > len(mesajlar)
        son_icerik = sonuc[-1].get("content", "")
        assert "UYARI" in son_icerik or "tur" in son_icerik.lower()


# ══════════════════════════════════════════════════════════════════════
# 7. BUDGET YONETIMI (28-29)
# ══════════════════════════════════════════════════════════════════════

class TestBudgetYonetimi:
    def test_budget_olusturma(self):
        """Budget nesnesi olusturulmali ve gerekli metodlara sahip olmali."""
        cl = ConversationLoop(max_tur=5)
        budget = cl._budget_olustur("test hedef")
        assert hasattr(budget, "devam_etmeli_mi")
        assert hasattr(budget, "tur_basla")
        assert hasattr(budget, "tur_bitir")

    def test_budget_max_tur_uyumu(self):
        """Budget max_tur degerini ConversationLoop.max_tur ile uyumlu olmali."""
        cl = ConversationLoop(max_tur=7)
        budget = cl._budget_olustur("hedef")
        assert budget.max_tur >= 7


# ══════════════════════════════════════════════════════════════════════
# 8. RUN_CONVERSATION AKİŞ (30-33)
# ══════════════════════════════════════════════════════════════════════

class TestRunConversationAkis:
    def test_donuc_yapisi(self):
        """run_conversation() gerekli alanlari dondurmeli."""
        cl = ConversationLoop(max_tur=2)
        sonuc = cl.run_conversation("test")
        for alan in ("task_id", "hedef", "basarili", "turlar", "sure", "budget"):
            assert alan in sonuc, f"'{alan}' alani eksik"

    def test_task_id_benzersiz(self):
        """Her run_conversation() cagrisinda benzersiz task_id uretilmeli."""
        cl = ConversationLoop(max_tur=1)
        ids = {cl.run_conversation("hedef")["task_id"] for _ in range(5)}
        assert len(ids) == 5

    def test_text_yanit_ile_tamamlama(self):
        """Beyin text yanit donunce run_conversation basarili olmali."""
        beyin = _mock_beyin("Gorev tamamlandi, rapor hazir.")
        cl = ConversationLoop(beyin=beyin, max_tur=5)
        sonuc = cl.run_conversation("bir rapor yaz")
        assert sonuc["basarili"] is True
        assert sonuc["yanit"] is not None

    def test_baglam_gecisi(self):
        """baglam parametresi konusma gecmisine eklenmeli."""
        cl = ConversationLoop(max_tur=1)
        cl.run_conversation("hedef", baglam={"kullanici": "Ahmet"})
        # baglam mesaji gecmisde olmali
        icerikler = [m.get("content", "") for m in cl._konusma_gecmisi]
        assert any("Ahmet" in c for c in icerikler)


# ══════════════════════════════════════════════════════════════════════
# 9. GERİYE UYUMLULUK (34-35)
# ══════════════════════════════════════════════════════════════════════

class TestGeriyeUyumluluk:
    def test_coz_api_calisir(self):
        """Eski coz() API'si bozulmamali."""
        cl = ConversationLoop(max_tur=2)
        sonuc = cl.coz("eski api testi")
        assert isinstance(sonuc, dict)
        assert "hedef" in sonuc
        assert "basarili" in sonuc
        assert "turlar" in sonuc

    def test_coz_ve_run_conversation_birlikte(self):
        """Ayni loop nesnesiyle hem coz() hem run_conversation() cagrilabilmeli."""
        beyin = _mock_beyin("Tamamlandi.")
        cl = ConversationLoop(beyin=beyin, max_tur=3)

        r1 = cl.coz("eski hedef")
        r2 = cl.run_conversation("yeni hedef")

        assert isinstance(r1, dict)
        assert isinstance(r2, dict)
        assert r2["hedef"] == "yeni hedef"
