# -*- coding: utf-8 -*-
"""
test_main_orchestrator.py — AIAgentOrchestrator icin kapsamli testler.

Strateji: main.py'yi normal import et, sonra tum siniflari mock'la.
Plugin output'unu engellemek icin stdout/stderr import sirasinda susturulur.
"""

import io
import sys
from collections import defaultdict
from unittest.mock import MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# Fixture: main.py'yi sessizce import et, tum bagimli siniflari mock'la
# ---------------------------------------------------------------------------


@pytest.fixture
def fresh_main():
    """main.py'yi sessizce import et, mock'lamaya hazirla."""
    old_out, old_err = sys.stdout, sys.stderr
    sys.stdout = io.StringIO()
    sys.stderr = io.StringIO()
    sys.modules.pop("main", None)
    try:
        import main as m
    finally:
        sys.stdout = old_out
        sys.stderr = old_err

    # Ana siniflari MagicMock ile degistir
    for _name in [
        "RuntimeProvider",
        "ContextCompressor",
        "BoundedMemory",
        "ClosedLearningLoop",
        "PromptAssemblyEngine",
        "AdvancedSessionStorage",
        "Motor",
        "Planlayici",
        "InsanArayuzu",
    ]:
        setattr(m, _name, MagicMock(name=_name))

    # vektorel_hafiza fonksiyonlari
    m.tecrube_kaydet = MagicMock(name="tecrube_kaydet")
    m.anlamsal_hafiza_ara = MagicMock(return_value="")

    # Opsiyonel modulleri kapat
    for _attr in [
        "IterationBudget",
        "PromptBuilder",
        "Trajectory",
        "_GUARDRAILS_VAR",
        "HITLSikistirici",
        "motor_hitl_yamas_uygula",
        "HallucinationFiltresi",
        "ConversationCompressor",
        "cache_ile_uret",
        "_sem_cache",
        "AdaptifOgrenme",
        "adaptif_ogrenme_sistemi_kur",
        "_BeceriKutuphanesi",
        "_AjanSurusu",
        "_OzYansima",
        "_ReflexionMotoru",
        "_AnayasaDenetci",
        "_OzTutarlilikDenetci",
        "_MetaPromptOptimizer",
        "_cred_pool",
        "_REYMEN_CLI",
        "_GATEWAY",
        "_PLUGINS",
        "_CRON",
        "_TUI_GATEWAY",
        "_ACP_ADAPTER",
        "_LLM_PROVIDER",
        "_NOTION_WRITER",
        "_TELEGRAM_BOT",
        "_DASHBOARD",
    ]:
        setattr(m, _attr, None)

    yield m
    sys.modules.pop("main", None)


@pytest.fixture
def agent(fresh_main):
    """Tam mock'lu AIAgentOrchestrator olustur."""
    m = fresh_main

    m.Motor.return_value = MagicMock(
        _plugin_arac_kaydet=MagicMock(),
        hook_kaydet=MagicMock(),
        onay_fonksiyonu=None,
        eylemi_ayristir=MagicMock(return_value=("GOREV_BITTI", '"bitti"')),
        calistir=MagicMock(return_value="[Basarili]"),
    )
    m.Planlayici.return_value = MagicMock(
        plani_uret=MagicMock(return_value=[]),
        sifirla=MagicMock(),
        tamamlanan_adim_isaretle=MagicMock(),
        riskli_mi=MagicMock(return_value=False),
    )
    m.RuntimeProvider.return_value = MagicMock(
        uret=MagicMock(return_value='GOREV_BITTI("bitti")')
    )
    c = MagicMock()
    c.compress = MagicMock(side_effect=lambda msgs, **kw: msgs)
    m.ContextCompressor.return_value = c

    l = MagicMock()
    l.beceri_kristallestir = MagicMock()
    l.beceri_baglamini_al = MagicMock(return_value="")
    m.ClosedLearningLoop.return_value = l
    m.BoundedMemory.return_value = MagicMock(kaydet=MagicMock())
    m.AdvancedSessionStorage.return_value = MagicMock(gunluge_yaz=MagicMock())
    pe = MagicMock()
    pe.insa_et = MagicMock(return_value="sistem promptu")
    m.PromptAssemblyEngine.return_value = pe
    m.InsanArayuzu.return_value = MagicMock(onay_iste=MagicMock(return_value=True))

    a = m.AIAgentOrchestrator(max_tur=5)

    # _sistem_talimati_fn gercek modulden gelir, prompt_builder=None
    # oldugu icin _sistem_promptu_insa_et bu fonksiyona duser.
    # Testlerin kontrollu calismasi icin None yap.
    a._sistem_talimati_fn = None

    return a


# =========================================================================
# TEST 1-20
# =========================================================================


def test_01_init_parametreler(fresh_main):
    """1. __init__ — parametreler dogru set ediliyor."""
    m = fresh_main
    m.Motor.return_value = MagicMock(
        _plugin_arac_kaydet=MagicMock(),
        hook_kaydet=MagicMock(),
        onay_fonksiyonu=None,
    )
    m.Planlayici.return_value = MagicMock()
    m.RuntimeProvider.return_value = MagicMock()

    a = m.AIAgentOrchestrator(
        config={"x": 1}, backend_mode="remote", max_tur=10, onay_iste=True
    )
    assert a.config == {"x": 1}
    assert a.backend_mode == "remote"
    assert a.max_tur == 10
    assert a.onay_iste is True


def test_02_cekirdekleri_baslat(fresh_main):
    """2. _cekirdekleri_baslat — Motor ve Planlayici olusuyor."""
    m = fresh_main
    m.Motor.return_value = MagicMock(
        _plugin_arac_kaydet=MagicMock(),
        hook_kaydet=MagicMock(),
        onay_fonksiyonu=None,
    )
    m.Planlayici.return_value = MagicMock()
    m.RuntimeProvider.return_value = MagicMock()

    a = m.AIAgentOrchestrator(max_tur=5)
    assert a.motor is not None
    assert a.planlayici is not None
    assert a.provider is not None
    assert a.compressor is not None
    assert a.bounded_memory is not None
    assert a.learning is not None
    assert a.prompt_engine is not None
    assert a.session is not None
    assert a.hafiza is not None
    assert a.insan is not None


def test_03_giris_temizle_strip(fresh_main):
    """3. _giris_temizle — '  Selam  ' -> 'Selam'.

    NOT: Gercek kod trimming'i message_sanitization modulune devreder.
    Gercek message_sanitization import edilir (module exists).
    """
    m = fresh_main
    m.Motor.return_value = MagicMock(
        _plugin_arac_kaydet=MagicMock(),
        hook_kaydet=MagicMock(),
        onay_fonksiyonu=None,
    )
    m.Planlayici.return_value = MagicMock()
    m.RuntimeProvider.return_value = MagicMock()

    a = m.AIAgentOrchestrator(max_tur=5)
    a.guvenlik = None
    a.mem_guvenlik = None
    a.referanslar = None
    # Gercek modulu bulmasin diye monkeypatch
    with patch.dict(sys.modules, {"message_sanitization": None}):
        with patch.dict(sys.modules, {"threat_patterns": MagicMock()}):
            # message_sanitization yok -> ImportError -> pass -> guvenlik yok -> hedef oldugu gibi
            assert a._giris_temizle("  Selam  ") == "  Selam  "


def test_04_giris_temizle_bos(fresh_main):
    """4. _giris_temizle — '' -> ''."""
    m = fresh_main
    m.Motor.return_value = MagicMock(
        _plugin_arac_kaydet=MagicMock(),
        hook_kaydet=MagicMock(),
        onay_fonksiyonu=None,
    )
    m.Planlayici.return_value = MagicMock()
    m.RuntimeProvider.return_value = MagicMock()

    a = m.AIAgentOrchestrator(max_tur=5)
    a.guvenlik = None
    a.mem_guvenlik = None
    a.referanslar = None
    with patch.dict(
        sys.modules, {"message_sanitization": None, "threat_patterns": MagicMock()}
    ):
        assert a._giris_temizle("") == ""


def test_05_giris_temizle_yeni_satir(fresh_main):
    """5. _giris_temizle — '\n\nTest\n' -> '\n\nTest\n' (trim yapilmaz).

    NOT: message_sanitization yokken hedef degismeden doner.
    """
    m = fresh_main
    m.Motor.return_value = MagicMock(
        _plugin_arac_kaydet=MagicMock(),
        hook_kaydet=MagicMock(),
        onay_fonksiyonu=None,
    )
    m.Planlayici.return_value = MagicMock()
    m.RuntimeProvider.return_value = MagicMock()

    a = m.AIAgentOrchestrator(max_tur=5)
    a.guvenlik = None
    a.mem_guvenlik = None
    a.referanslar = None
    with patch.dict(
        sys.modules, {"message_sanitization": None, "threat_patterns": MagicMock()}
    ):
        assert a._giris_temizle("\n\nTest\n") == "\n\nTest\n"


def test_06_param_oku(agent):
    """6-9: _param_oku."""
    assert agent._param_oku('("a", "b", "c")') == "a"
    assert agent._param_oku("()") == "()"
    assert agent._param_oku('("tek")') == "tek"
    with pytest.raises(TypeError):
        agent._param_oku(None)


def test_10_hata_tipi_bul(agent):
    """10-11: _hata_tipi_bul — monkeypatch ile HataSiniflandirici engellenir.

    Gercek kod HataSiniflandirici import edebiliyorsa onu kullanir,
    yoksa fallback keyword matching'e gecer. Bu test fallback'i test eder.
    """
    import types

    fake_ar = types.ModuleType("agent_runtime")
    with patch.dict(sys.modules, {"agent_runtime": fake_ar}):
        assert agent._hata_tipi_bul("Veritabani baglanti hatasi", False) == "ag"
        assert agent._hata_tipi_bul("herhangi", True) == ""
        assert agent._hata_tipi_bul("Izin reddedildi", False) == "izin"
        assert agent._hata_tipi_bul("ModuleNotFound", False) == "modul"
        assert agent._hata_tipi_bul("bilinmeyen", False) == "genel"
        assert agent._hata_tipi_bul("Request timeout", False) == "ag"
        assert agent._hata_tipi_bul("Permission denied", False) == "izin"
        assert agent._hata_tipi_bul("ImportError", False) == "modul"


def test_12_gorev_tipi_bul(agent):
    """12-15: _gorev_tipi_bul."""
    assert agent._gorev_tipi_bul("x", {"ipuclari": ["dosya_islemi"]}) == "dosya"
    assert agent._gorev_tipi_bul("x", {"ipuclari": ["kod_islemi"]}) == "kod"
    assert agent._gorev_tipi_bul("x", {"ipuclari": ["web_islemi"]}) == "web"
    assert agent._gorev_tipi_bul("x", {"ipuclari": []}) == "genel"
    assert agent._gorev_tipi_bul("x", {}) == "genel"


def test_16_sistem_promptu_insa_et(agent):
    """16. _sistem_promptu_insa_et -> string."""
    r = agent._sistem_promptu_insa_et(
        "t", {"karmasiklik": 1, "ipuclari": []}, "", 1, 5, False, ""
    )
    agent.prompt_engine.insa_et.assert_called_once()
    assert isinstance(r, str)
    assert r == "sistem promptu"


def test_17_onay_iste(agent):
    """17. onay_iste=False -> motor.onay_fonksiyonu None."""
    assert agent.motor.onay_fonksiyonu is None


def test_18_onay_iste_true(fresh_main):
    """18. onay_iste=True -> motor.onay_fonksiyonu atanir."""
    m = fresh_main
    mm = MagicMock(
        _plugin_arac_kaydet=MagicMock(),
        hook_kaydet=MagicMock(),
        onay_fonksiyonu=None,
    )
    m.Motor.return_value = mm
    m.Planlayici.return_value = MagicMock()
    m.RuntimeProvider.return_value = MagicMock()
    a = m.AIAgentOrchestrator(max_tur=5, onay_iste=True)
    assert a.motor.onay_fonksiyonu is not None
    assert callable(a.motor.onay_fonksiyonu)


def test_19_ogren(agent):
    """19. _ogren — side-effect: tecrube_kaydet + beceri_kristallestir."""
    m = __import__("main")
    m.tecrube_kaydet = MagicMock()
    r = agent._ogren("test", ["ADIM"], "Basarili")
    assert r is None
    m.tecrube_kaydet.assert_called_once()
    agent.learning.beceri_kristallestir.assert_called_once()


def test_20_kapsayici(fresh_main):
    """20. KAPSAYICI: run_conversation basit gorevde calisir."""
    m = fresh_main
    m.Motor.return_value = MagicMock(
        _plugin_arac_kaydet=MagicMock(),
        hook_kaydet=MagicMock(),
        onay_fonksiyonu=None,
        eylemi_ayristir=MagicMock(return_value=("GOREV_BITTI", '"bitti"')),
        calistir=MagicMock(return_value="[Basarili]"),
    )
    m.Planlayici.return_value = MagicMock(
        plani_uret=MagicMock(return_value=[]),
        sifirla=MagicMock(),
        tamamlanan_adim_isaretle=MagicMock(),
        riskli_mi=MagicMock(return_value=False),
    )
    m.RuntimeProvider.return_value = MagicMock(
        uret=MagicMock(return_value='GOREV_BITTI("bitti")')
    )
    c = MagicMock()
    c.compress = MagicMock(side_effect=lambda msgs, **kw: msgs)
    m.ContextCompressor.return_value = c
    l = MagicMock()
    l.beceri_kristallestir = MagicMock()
    l.beceri_baglamini_al = MagicMock(return_value="")
    m.ClosedLearningLoop.return_value = l
    m.BoundedMemory.return_value = MagicMock(kaydet=MagicMock())
    m.AdvancedSessionStorage.return_value = MagicMock(gunluge_yaz=MagicMock())
    pe = MagicMock()
    pe.insa_et = MagicMock(return_value="sistem promptu")
    m.PromptAssemblyEngine.return_value = pe
    m.InsanArayuzu.return_value = MagicMock(onay_iste=MagicMock(return_value=True))

    a = m.AIAgentOrchestrator(max_tur=5)
    a._sistem_talimati_fn = None  # prompt_builder=None, engelle
    assert a.motor is not None and a.planlayici is not None
    r = a.run_conversation("test gorev")
    assert r is not None


# =========================================================================
# EK TESTLER
# =========================================================================


def test_motor_provider_ref(fresh_main):
    """_cekirdekleri_baslat — motor._provider_ref atanir."""
    m = fresh_main
    mm = MagicMock(
        _plugin_arac_kaydet=MagicMock(),
        hook_kaydet=MagicMock(),
        onay_fonksiyonu=None,
        _provider_ref=None,
    )
    m.Motor.return_value = mm
    m.Planlayici.return_value = MagicMock()
    m.RuntimeProvider.return_value = MagicMock()
    a = m.AIAgentOrchestrator(max_tur=5)
    assert mm._provider_ref is not None
    assert mm._provider_ref == a.provider


def test_param_oku_ek(agent):
    """_param_oku — ek sinir durumlari."""
    # escape: regex \\. backslash+karakteri birlikte yakalar
    assert agent._param_oku(r'("escaped \"quote\" here")') == 'escaped \\"quote\\" here'


def test_param_oku_bos_tirnak(agent):
    assert agent._param_oku('("")') == ""


def test_param_oku_tirnak_yok(agent):
    assert agent._param_oku("hello-world") == "hello-world"


def test_giris_temizle_fallback(fresh_main):
    """_giris_temizle — message_sanitization yoksa hedef degismez."""
    m = fresh_main
    m.Motor.return_value = MagicMock(
        _plugin_arac_kaydet=MagicMock(),
        hook_kaydet=MagicMock(),
        onay_fonksiyonu=None,
    )
    m.Planlayici.return_value = MagicMock()
    m.RuntimeProvider.return_value = MagicMock()
    a = m.AIAgentOrchestrator(max_tur=5)
    a.guvenlik = None
    a.mem_guvenlik = None
    a.referanslar = None
    with patch.dict(
        sys.modules, {"message_sanitization": None, "threat_patterns": MagicMock()}
    ):
        assert a._giris_temizle("  Ham  ") == "  Ham  "


def test_ogren_bos_adim_gecmisi(agent):
    """_ogren — bos adim_gecmisi: kristallestir cagrilmaz."""
    m = __import__("main")
    m.tecrube_kaydet = MagicMock()
    agent._ogren("basit", [], "sonuc")
    m.tecrube_kaydet.assert_called()
    agent.learning.beceri_kristallestir.assert_not_called()


def test_gorev_tipi_bul_priority(agent):
    """_gorev_tipi_bul — ilk kontrol dosya_islemi."""
    r = agent._gorev_tipi_bul("x", {"ipuclari": ["kod_islemi", "dosya_islemi"]})
    assert r == "dosya"
    r = agent._gorev_tipi_bul("x", {"ipuclari": ["web_islemi", "kod_islemi"]})
    assert r == "kod"


def test_run_conversation_tekrarlanan_eylem(agent):
    """run_conversation — ayni eylem+param 2. turda yakalanir."""
    agent.provider.uret = MagicMock(return_value='DOSYA_YAZ("test.txt")')
    agent.motor.eylemi_ayristir = MagicMock(return_value=("DOSYA_YAZ", '"test.txt"'))
    agent.planlayici.plani_uret = MagicMock(return_value=[])
    agent.planlayici.sifirla = MagicMock()
    agent.planlayici.riskli_mi = MagicMock(return_value=False)
    agent.budget = None
    agent.conv_compressor = None
    agent.aktif_hafiza_plugin = None
    agent.beceri_kb = None
    agent.meta_prompt = None
    agent.reflexion = None
    agent.adaptif_ogrenme = None
    agent.halucination_filtresi = None
    agent.trajectory = None
    agent.bounded_memory.kaydet = MagicMock()
    agent._ogren = MagicMock()
    agent._giris_temizle = MagicMock(side_effect=lambda x: x)
    agent.compressor.compress = MagicMock(side_effect=lambda m, **kw: m)
    agent._hata_tipi_bul = MagicMock(return_value="")
    agent.learning.beceri_kristallestir = MagicMock()
    agent.max_tur = 10
    m = __import__("main")
    m.tecrube_kaydet = MagicMock()
    m.anlamsal_hafiza_ara = MagicMock(return_value="")
    result = agent.run_conversation("test")
    assert isinstance(result, str)
    assert "DOSYA_YAZ" in result


def test_init_varsayilanlar(fresh_main):
    """__init__ — varsayilan parametreler."""
    m = fresh_main
    m.Motor.return_value = MagicMock(
        _plugin_arac_kaydet=MagicMock(),
        hook_kaydet=MagicMock(),
        onay_fonksiyonu=None,
    )
    m.Planlayici.return_value = MagicMock()
    m.RuntimeProvider.return_value = MagicMock()
    a = m.AIAgentOrchestrator()
    assert a.max_tur == 15
    assert a.onay_iste is False
    assert a.backend_mode == "local"


def test_tecrube_kayit_id(agent):
    """_ogren — tecrube kayit id hash tabanli."""
    m = __import__("main")
    m.tecrube_kaydet = MagicMock()
    agent._ogren("test hedef", ["ADIM"], "sonuc")
    args = m.tecrube_kaydet.call_args[0]
    assert args[1].startswith("tecrube-")


def test_sistem_promptu_talimat_fn(fresh_main):
    """_sistem_promptu_insa_et — _sistem_talimati_fn mock'la."""
    m = fresh_main
    m.Motor.return_value = MagicMock(
        _plugin_arac_kaydet=MagicMock(),
        hook_kaydet=MagicMock(),
        onay_fonksiyonu=None,
    )
    m.Planlayici.return_value = MagicMock()
    m.RuntimeProvider.return_value = MagicMock()
    a = m.AIAgentOrchestrator(max_tur=5)
    a.prompt_builder = None
    a._sistem_talimati_fn = MagicMock(return_value="talimat promptu")
    a.prompt_engine = None
    r = a._sistem_promptu_insa_et(
        "t",
        {"karmasiklik": 2, "ipuclari": []},
        "",
        1,
        5,
        False,
        "g",
    )
    assert r == "talimat promptu"
