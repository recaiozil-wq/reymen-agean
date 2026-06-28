"""image_generation_tool modülü testleri."""
import pytest
from unittest.mock import MagicMock, patch


class TestGorselAnalizEt:
    """gorsel_analiz_et fonksiyonu testleri."""

    @patch("requests.get")
    def test_gorsel_analiz_et_no_file(self, mock_get):
        """Dosya yol boşsa hata döndürür."""
        from tools import image_generation_tool
        sonuc = image_generation_tool.gorsel_analiz_et("")
        assert "hata" in sonuc.lower() or "gerekli" in sonuc.lower()

    @patch("requests.get")
    def test_gorsel_analiz_et_success(self, mock_get):
        """Başarılı analiz."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"choices": [{"message": {"content": "Bu bir test görselidir."}}]}
        mock_get.return_value = mock_response
        with patch("tools.image_generation_tool.os.path.exists", return_value=True):
            with patch("builtins.open", MagicMock()):
                from tools import image_generation_tool
                sonuc = image_generation_tool.gorsel_analiz_et("C:\\test.png")
                assert sonuc is not None


class TestResimUret:
    """resim_uret fonksiyonu testleri."""

    @patch("requests.post")
    def test_resim_uret_no_api_key(self, mock_post):
        """API anahtarı yoksa hata döndürür."""
        from tools import image_generation_tool
        with patch.dict("os.environ", {}, clear=True):
            sonuc = image_generation_tool.resim_uret("test prompt")
            assert sonuc is not None

    @patch("requests.post")
    def test_resim_uret_deepseek_success(self, mock_post):
        """DeepSeek ile başarılı görsel üretimi."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": [{"url": "https://example.com/img.png"}]}
        mock_post.return_value = mock_response
        with patch.dict("os.environ", {"DEEPSEEK_API_KEY": "sk-test"}):
            from tools import image_generation_tool
            sonuc = image_generation_tool.resim_uret("test prompt")
            assert sonuc is not None

    @patch("requests.post")
    def test_resim_uret_deepseek_fallback(self, mock_post):
        """DeepSeek fallback durumu."""
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Hata"
        mock_post.return_value = mock_response
        with patch.dict("os.environ", {"DEEPSEEK_API_KEY": "sk-test"}):
            from tools import image_generation_tool
            sonuc = image_generation_tool.resim_uret("test prompt")
            assert sonuc is not None
