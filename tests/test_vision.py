"""ReYMeN — Vision sistem testleri."""

from pathlib import Path
import pytest


def test_vision_adapter_import():
    """VisionAdapter import edilebiliyor mu?"""
    from reymen.cereyan.conversation_loop import VisionAdapter
    va = VisionAdapter()
    assert va is not None
    assert hasattr(va, '_vision_analiz')
    # Henüz ConversationLoop'a bağlı değil, statik mesaj döndürür
    sonuc = va._vision_analiz("test")
    assert sonuc is not None
    assert "referansi" in sonuc or "yok" in sonuc


def test_vision_tools_import():
    """vision_tools modulu import edilebiliyor mu?"""
    from reymen.cereyan.tools.vision_tools import vision_analiz
    assert callable(vision_analiz)
    sonuc = vision_analiz(gorsel_yolu="test.jpg", soru="Bu nedir?")
    assert sonuc is not None


def test_vision_kelime_tetikleyicileri():
    """Gorsel kelime tetikleyicileri dogru calisiyor mu?"""
    gorsel_kelimeler = ["foto", "resim", "gorsel", "goruntu", "ekran", "ss", "screenshot", "image", "photo", "picture"]
    test_sorgular = {
        "bu fotoyu analiz et": True,
        "ekran goruntusu al": True,
        "python kodu yaz": False,
        "resimdeki yaziyi oku": True,
        "merhaba dunya": False,
    }
    for sorgu, beklenen in test_sorgular.items():
        sonuc = any(k in sorgu.lower() for k in gorsel_kelimeler)
        assert sonuc == beklenen, f"'{sorgu}' -> {sonuc}, beklenen {beklenen}"


def test_vision_url_bulma():
    """URL/resim yolu regex calisiyor mu?"""
    import re
    pattern = r'https?://[^\s]+\.(jpg|jpeg|png|gif|webp|bmp)'
    testler = {
        "https://example.com/image.jpg": True,
        "https://site.com/foto.png": True,
        "C:\\Users\\photo.jpg": False,
        "merhaba": False,
    }
    for text, beklenen in testler.items():
        sonuc = bool(re.search(pattern, text, re.IGNORECASE))
        assert sonuc == beklenen, f"'{text}' -> {sonuc}, beklenen {beklenen}"
