# -*- coding: utf-8 -*-
"""tests/test_security_engine.py — SecurityEngine modülü testleri."""

import json
import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))


class TestSecurityEngine:
    """SecurityEngine birim testleri."""

    @pytest.fixture(autouse=True)
    def _modulu_yukle(self):
        from security_engine import SecurityEngine
        self.SecurityEngine = SecurityEngine

    # ── Kurulum ───────────────────────────────────────────────────────────

    def test_engine_baslatma_varsayilan(self):
        """SecurityEngine varsayılan parametrelerle başlatılabilmeli."""
        se = self.SecurityEngine()
        assert se is not None

    def test_engine_baslatma_kural_dosyasi_ile(self):
        """SecurityEngine kural dosyası ile başlatılabilmeli."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump({"test_kural": "test"}, f)
            kural_yolu = f.name
        try:
            se = self.SecurityEngine(kural_dosyasi=kural_yolu)
            assert se._ozel_kurallar.get("test_kural") == "test"
        finally:
            Path(kural_yolu).unlink(missing_ok=True)

    def test_engine_baslatma_gecersiz_kural_dosyasi(self):
        """Geçersiz kural dosyası engine başlatmayı engellememeli."""
        se = self.SecurityEngine(kural_dosyasi="olmayan_dosya.json")
        assert se._ozel_kurallar == {}

    def test_engine_ilk_durum(self):
        """Yeni engine'de açık ve risk sıfır olmalı."""
        se = self.SecurityEngine()
        assert se._risk_seviyesi == 0
        assert se._son_tarama is None
        assert se._aciklar == []

    # ── tarama_yap ────────────────────────────────────────────────────────

    def test_tarama_yap_bos_metin(self):
        """Boş metin taraması sıfır açık dönmeli."""
        se = self.SecurityEngine()
        sonuc = se.tarama_yap("")
        assert sonuc["acik_sayisi"] == 0

    def test_tarama_yap_guvenli_metin(self):
        """Güvenli metin taraması açık bulmamalı."""
        se = self.SecurityEngine()
        sonuc = se.tarama_yap("Bugün hava çok güzel.")
        assert sonuc.get("acik_sayisi", 0) == 0

    def test_tarama_yap_pii_email_tespit(self):
        """E-posta adresi PII olarak tespit edilmeli."""
        se = self.SecurityEngine()
        sonuc = se.tarama_yap("email: test@example.com")
        assert sonuc["acik_sayisi"] >= 1
        pii_var = any(a.get("tur") == "pii" for a in sonuc.get("aciklar", []))
        assert pii_var

    def test_tarama_yap_pii_tckn_tespit(self):
        """11 haneli TCKN PII olarak tespit edilmeli."""
        se = self.SecurityEngine()
        sonuc = se.tarama_yap("TC: 12345678901")
        assert sonuc["acik_sayisi"] >= 1

    def test_tarama_yap_tehdit_kelimesi_rmrf(self):
        """'rm -rf' tehdit kelimesi olarak tespit edilmeli."""
        se = self.SecurityEngine()
        sonuc = se.tarama_yap("rm -rf / komutu")
        assert sonuc["acik_sayisi"] >= 1
        tehdit_var = any(a.get("tur") == "tehdit" for a in sonuc.get("aciklar", []))
        assert tehdit_var

    def test_tarama_yap_tehdit_drop_table(self):
        """'drop table' tehdit kelimesi olarak tespit edilmeli."""
        se = self.SecurityEngine()
        sonuc = se.tarama_yap("drop table users")
        assert sonuc["acik_sayisi"] >= 1

    def test_tarama_yap_tehdit_eval(self):
        """'eval(' tehdit kelimesi olarak tespit edilmeli."""
        se = self.SecurityEngine()
        sonuc = se.tarama_yap("eval('1+1')")
        assert sonuc["acik_sayisi"] >= 1

    def test_tarama_yap_risk_yuksek_parola(self):
        """'parola' risk anahtarı yüksek seviyede tespit edilmeli."""
        se = self.SecurityEngine()
        sonuc = se.tarama_yap("parola = 'admin123'")
        assert sonuc["acik_sayisi"] >= 1
        yuksek_var = any(
            a.get("seviye") in ("yuksek", "kritik")
            for a in sonuc.get("aciklar", [])
        )
        assert yuksek_var

    def test_tarama_yap_risk_yuksek_api_key(self):
        """'api_key' yüksek risk olarak tespit edilmeli."""
        se = self.SecurityEngine()
        sonuc = se.tarama_yap("api_key = 'sk-xxx'")
        assert sonuc["acik_sayisi"] >= 1

    def test_tarama_yap_risk_orta_localhost(self):
        """'localhost' orta risk olarak tespit edilmeli."""
        se = self.SecurityEngine()
        sonuc = se.tarama_yap("baglanti = 'localhost:8080'")
        assert sonuc["acik_sayisi"] >= 1
        orta_var = any(a.get("seviye") == "orta" for a in sonuc.get("aciklar", []))
        assert orta_var

    def test_tarama_yap_risk_orta_debug(self):
        """'debug' orta risk olarak tespit edilmeli."""
        se = self.SecurityEngine()
        sonuc = se.tarama_yap("debug = True")
        assert sonuc["acik_sayisi"] >= 1

    def test_tarama_yap_risk_dusuk_temp(self):
        """'temp' düşük risk olarak tespit edilmeli."""
        se = self.SecurityEngine()
        sonuc = se.tarama_yap("temp = '/tmp/dosya'")
        assert sonuc["acik_sayisi"] >= 1

    def test_tarama_yap_dosya_oku(self):
        """Geçici dosyayı tarayabilmeli."""
        se = self.SecurityEngine()
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("test@example.com ve parola=123")
            dosya_yolu = f.name
        try:
            sonuc = se.tarama_yap(dosya_yolu)
            assert sonuc.get("basari") is not False or sonuc.get("acik_sayisi", 0) > 0
        finally:
            Path(dosya_yolu).unlink(missing_ok=True)

    def test_tarama_yap_olmayan_dosya(self):
        """Olmayan dosya metin olarak işlenir, açık sayısı 0 olur."""
        se = self.SecurityEngine()
        sonuc = se.tarama_yap("/olmayan/dosya.txt")
        # isfile False olduğu için string olarak işlenir, açık bulmaz
        assert "acik_sayisi" in sonuc
        assert sonuc["hedef"] == "dogrudan"

    def test_tarama_sonrasi_son_tarama_guncellenir(self):
        """Tarama sonrası _son_tarama güncellenmeli."""
        se = self.SecurityEngine()
        se.tarama_yap("test")
        assert se._son_tarama is not None
        assert "zaman" in se._son_tarama

    def test_tarama_sonrasi_aciklar_guncellenir(self):
        """Tarama sonrası _aciklar ve _risk_seviyesi güncellenmeli."""
        se = self.SecurityEngine()
        se.tarama_yap("parola = '123' ve test@site.com")
        assert len(se._aciklar) >= 1
        assert se._risk_seviyesi > 0

    # ── risk_analizi ──────────────────────────────────────────────────────

    def test_risk_analizi_once_tarama_yoksa(self):
        """Tarama yapılmadan risk_analizi hata dönmeli."""
        se = self.SecurityEngine()
        sonuc = se.risk_analizi()
        assert "hata" in sonuc

    def test_risk_analizi_dusuk(self):
        """Düşük riskli içerik için risk seviyesi 'dusuk' olmalı."""
        se = self.SecurityEngine()
        se.tarama_yap("örnek içerik")
        analiz = se.risk_analizi()
        assert analiz.get("risk_puani", 100) < 40

    def test_risk_analizi_yuksek_tehdit(self):
        """Çok tehdit içeren içerik için yüksek risk dönmeli."""
        se = self.SecurityEngine()
        se.tarama_yap(
            "parola='x' sifre='y' token='z' api_key='k' rm -rf / eval('x')"
        )
        analiz = se.risk_analizi()
        assert analiz.get("risk_puani", 0) >= 15

    def test_risk_analizi_tavsiye_uretir(self):
        """risk_analizi tavsiye metni içermeli."""
        se = self.SecurityEngine()
        se.tarama_yap("parola = 'x'")
        analiz = se.risk_analizi()
        assert "tavsiye" in analiz
        assert isinstance(analiz["tavsiye"], str)

    def test_risk_analizi_acik_sayilari(self):
        """risk_analizi kritik/yüksek/orta/düşük sayılarını içermeli."""
        se = self.SecurityEngine()
        se.tarama_yap("rm -rf / test@site.com localhost temp")
        analiz = se.risk_analizi()
        assert "kritik_sayisi" in analiz
        assert "yuksek_sayisi" in analiz
        assert "orta_sayisi" in analiz
        assert "dusuk_sayisi" in analiz

    # ── rapor_uret ────────────────────────────────────────────────────────

    def test_rapor_uret_once_tarama_yoksa(self):
        """Tarama yapılmadan rapor_uret uyarı dönmeli."""
        se = self.SecurityEngine()
        rapor = se.rapor_uret()
        assert "Henuz tarama" in rapor

    def test_rapor_uret_ozet(self):
        """Özet rapor metin döndürmeli."""
        se = self.SecurityEngine()
        se.tarama_yap("test")
        rapor = se.rapor_uret(seviye="ozet")
        assert isinstance(rapor, str)
        assert "RISK" in rapor or "GUVENLIK" in rapor

    def test_rapor_uret_json(self):
        """JSON rapor dict döndürmeli."""
        se = self.SecurityEngine()
        se.tarama_yap("test")
        rapor = se.rapor_uret(seviye="json")
        assert isinstance(rapor, dict)
        assert "tarama" in rapor
        assert "analiz" in rapor

    def test_rapor_uret_detayli_acik_listesi(self):
        """Detaylı rapor açık listesini içermeli."""
        se = self.SecurityEngine()
        se.tarama_yap("parola ve test@site.com")
        rapor = se.rapor_uret(seviye="detayli")
        assert "Acik Listesi" in rapor or "Detayli" in rapor

    # ── duzelt ────────────────────────────────────────────────────────────

    def test_duzelt_gecersiz_girdi(self):
        """Geçersiz açık bilgisi ile duzelt hata dönmeli."""
        se = self.SecurityEngine()
        sonuc = se.duzelt(None)
        assert sonuc.get("basari") is False

    def test_duzelt_pii(self):
        """PII açığı düzeltme önerisi dönmeli."""
        se = self.SecurityEngine()
        sonuc = se.duzelt({"tur": "pii", "etiket": "EMAIL"})
        assert sonuc.get("basari") is True
        assert "redakte" in sonuc.get("duzeltme", "")

    def test_duzelt_tehdit(self):
        """Tehdit açığı düzeltme önerisi dönmeli."""
        se = self.SecurityEngine()
        sonuc = se.duzelt({"tur": "tehdit", "etiket": "rm -rf"})
        assert sonuc.get("basari") is True
        assert "temizleme" in sonuc.get("duzeltme", "")

    def test_duzelt_risk(self):
        """Risk açığı düzeltme önerisi dönmeli."""
        se = self.SecurityEngine()
        sonuc = se.duzelt({"tur": "risk", "etiket": "parola"})
        assert sonuc.get("basari") is True
        assert "inceleme" in sonuc.get("duzeltme", "")

    def test_duzelt_bilinmeyen_tur(self):
        """Bilinmeyen açık türü için başarısız dönmeli."""
        se = self.SecurityEngine()
        sonuc = se.duzelt({"tur": "xyz", "etiket": "test"})
        assert sonuc.get("basari") is False

    # ── aciklari_listele / son_taramayi_getir ─────────────────────────────

    def test_aciklari_listele_bos(self):
        """Henüz tarama yoksa boş liste dönmeli."""
        se = self.SecurityEngine()
        assert se.aciklari_listele() == []

    def test_aciklari_listele_dolu(self):
        """Tarama sonrası açık listesi dolu olmalı."""
        se = self.SecurityEngine()
        se.tarama_yap("parola = 'x'")
        assert len(se.aciklari_listele()) >= 1

    def test_son_taramayi_getir_none(self):
        """Henüz tarama yoksa None dönmeli."""
        se = self.SecurityEngine()
        assert se.son_taramayi_getir() is None

    def test_son_taramayi_getir_dolu(self):
        """Tarama sonrası son tarama dict dönmeli."""
        se = self.SecurityEngine()
        se.tarama_yap("test")
        son = se.son_taramayi_getir()
        assert isinstance(son, dict)
        assert "hedef" in son
