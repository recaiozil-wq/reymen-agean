# -*- coding: utf-8 -*-
"""Testler: reymen.cereyan.hook_dispatcher"""

import pytest
from reymen.cereyan.hook_dispatcher import (
    hook_kaydet,
    hook_kaldir,
    hook_cagir,
    invoke_hook,
    register_hook,
    tum_hooklari_temizle,
    kayitli_hooklar,
    hook,
    GECERLI_OLAYLAR,
    oturum_baslat_tetikle,
    oturum_bitir_tetikle,
    tur_baslat_tetikle,
    tur_bitir_tetikle,
    arac_cagri_tetikle,
    arac_sonuc_tetikle,
    hata_tetikle,
    context_sikistirma_tetikle,
)


@pytest.fixture(autouse=True)
def temizle():
    """Her testten önce ve sonra tüm hook'ları temizle."""
    tum_hooklari_temizle()
    yield
    tum_hooklari_temizle()


class TestHookKayit:
    def test_gecerli_olay_kayit(self):
        cagirildi = []
        hook_kaydet("on_session_start", lambda **kw: cagirildi.append(kw))
        sonuclar = hook_cagir("on_session_start", session_id="abc")
        assert len(sonuclar) == 1
        assert cagirildi[0]["session_id"] == "abc"

    def test_bilinmeyen_olay_valueerror(self):
        with pytest.raises(ValueError, match="Bilinmeyen hook olayı"):
            hook_kaydet("bilinmeyen_olay", lambda: None)

    def test_ayni_callback_iki_kez_kayit_edilmez(self):
        fn = lambda **kw: None
        hook_kaydet("on_turn_start", fn)
        hook_kaydet("on_turn_start", fn)
        sonuclar = hook_cagir("on_turn_start", tur=1)
        assert len(sonuclar) == 1

    def test_farkli_callbackler_ayri_kayit(self):
        cagirildi = []
        hook_kaydet("on_turn_end", lambda **kw: cagirildi.append("a"))
        hook_kaydet("on_turn_end", lambda **kw: cagirildi.append("b"))
        hook_cagir("on_turn_end", tur=1, basarili=True)
        assert cagirildi == ["a", "b"]

    def test_kayit_olmayan_olay_bos_liste(self):
        sonuclar = hook_cagir("on_error")
        assert sonuclar == []


class TestHookKaldir:
    def test_kaldir_basarili(self):
        fn = lambda **kw: "x"
        hook_kaydet("on_tool_call", fn)
        kaldirildi = hook_kaldir("on_tool_call", fn)
        assert kaldirildi is True
        assert hook_cagir("on_tool_call", arac_adi="test", argumanlar={}) == []

    def test_kayitli_olmayan_kaldir_false(self):
        fn = lambda **kw: None
        assert hook_kaldir("on_tool_call", fn) is False

    def test_bilinmeyen_olay_kaldir_false(self):
        fn = lambda **kw: None
        assert hook_kaldir("bilinmeyen", fn) is False


class TestHookCagir:
    def test_return_deger_toplanir(self):
        hook_kaydet("on_turn_start", lambda **kw: 42)
        hook_kaydet("on_turn_start", lambda **kw: "merhaba")
        sonuclar = hook_cagir("on_turn_start", tur=1)
        assert sonuclar == [42, "merhaba"]

    def test_hata_veren_callback_diger_calisiyor(self):
        cagirildi = []

        def hata_veren(**kw):
            raise RuntimeError("kasıtlı hata")

        def normal(**kw):
            cagirildi.append("normal")
            return "normal"

        hook_kaydet("on_error", hata_veren)
        hook_kaydet("on_error", normal)
        sonuclar = hook_cagir("on_error", hata=RuntimeError("test"))
        # İlki None (hata), ikincisi "normal"
        assert sonuclar == [None, "normal"]
        assert cagirildi == ["normal"]

    def test_tum_kwargs_iletilir(self):
        alindi = {}

        def alici(**kw):
            alindi.update(kw)

        hook_kaydet("on_tool_result", alici)
        hook_cagir(
            "on_tool_result",
            arac_adi="yazdir",
            sonuc="tamam",
            sure_sn=0.5,
            ekstra="veri",
        )
        assert alindi["arac_adi"] == "yazdir"
        assert alindi["sonuc"] == "tamam"
        assert alindi["sure_sn"] == 0.5
        assert alindi["ekstra"] == "veri"


class TestHermesAliaslar:
    def test_invoke_hook_alias(self):
        assert invoke_hook is hook_cagir

    def test_register_hook_alias(self):
        assert register_hook is hook_kaydet


class TestDecorator:
    def test_hook_decorator_kayit(self):
        @hook("on_session_end")
        def oturum_bitti(**kw):
            return kw.get("session_id")

        sonuclar = hook_cagir("on_session_end", session_id="xyz")
        assert sonuclar == ["xyz"]

    def test_hook_decorator_bilinmeyen_olay(self):
        with pytest.raises(ValueError):

            @hook("bilinmeyen_olay")
            def fn(**kw):
                pass


class TestGecerliOlaylar:
    def test_tum_olay_adlari(self):
        beklenen = {
            "on_session_start",
            "on_session_end",
            "on_turn_start",
            "on_turn_end",
            "on_tool_call",
            "on_tool_result",
            "on_error",
            "on_context_compress",
        }
        assert GECERLI_OLAYLAR == beklenen


class TestKayitliHooklar:
    def test_bos_baskiste(self):
        assert kayitli_hooklar() == {}

    def test_kayitli_olanlar_listelenir(self):
        def oturum_fn(**kw):
            pass

        hook_kaydet("on_session_start", oturum_fn)
        ozet = kayitli_hooklar()
        assert "on_session_start" in ozet
        assert "oturum_fn" in ozet["on_session_start"]


class TestKisaYolTetikleyiciler:
    def test_oturum_baslat(self):
        sonuc = []
        hook_kaydet("on_session_start", lambda **kw: sonuc.append(kw))
        oturum_baslat_tetikle("ses-1", agent_adi="ReYMeN")
        assert sonuc[0]["session_id"] == "ses-1"
        assert sonuc[0]["agent_adi"] == "ReYMeN"

    def test_oturum_bitir(self):
        sonuc = []
        hook_kaydet("on_session_end", lambda **kw: sonuc.append(kw))
        oturum_bitir_tetikle("ses-1", tur_sayisi=5)
        assert sonuc[0]["tur_sayisi"] == 5

    def test_tur_baslat(self):
        sonuc = []
        hook_kaydet("on_turn_start", lambda **kw: sonuc.append(kw))
        tur_baslat_tetikle(3, task_id="t-1")
        assert sonuc[0]["tur"] == 3

    def test_tur_bitir(self):
        sonuc = []
        hook_kaydet("on_turn_end", lambda **kw: sonuc.append(kw))
        tur_bitir_tetikle(3, basarili=True)
        assert sonuc[0]["basarili"] is True

    def test_arac_cagri(self):
        sonuc = []
        hook_kaydet("on_tool_call", lambda **kw: sonuc.append(kw))
        arac_cagri_tetikle("dosya_oku", {"yol": "/tmp/x"})
        assert sonuc[0]["arac_adi"] == "dosya_oku"
        assert sonuc[0]["argumanlar"]["yol"] == "/tmp/x"

    def test_arac_sonuc(self):
        sonuc = []
        hook_kaydet("on_tool_result", lambda **kw: sonuc.append(kw))
        arac_sonuc_tetikle("dosya_oku", "içerik", sure_sn=0.1)
        assert sonuc[0]["sonuc"] == "içerik"

    def test_hata_tetikle(self):
        yakalandi = []
        hook_kaydet("on_error", lambda **kw: yakalandi.append(kw))
        e = ValueError("test hatası")
        hata_tetikle(e, olay_baglami="api_call")
        assert yakalandi[0]["hata"] is e
        assert yakalandi[0]["olay_baglami"] == "api_call"

    def test_context_sikistirma(self):
        sonuc = []
        hook_kaydet("on_context_compress", lambda **kw: sonuc.append(kw))
        context_sikistirma_tetikle(50, token_tahmini=80000)
        assert sonuc[0]["mesaj_sayisi"] == 50
        assert sonuc[0]["token_tahmini"] == 80000
