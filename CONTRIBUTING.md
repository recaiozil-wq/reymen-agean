# Katkıda Bulunma Rehberi

ReYMeN projesine katkıda bulunmayı düşündüğünüz için teşekkürler!

## 🐛 Hata Bildirme

Hata bildirimleri için [GitHub Issues](https://github.com/recaiozil-wq/reymen-agean/issues/new/choose) sayfasını kullanın.

Bildiriminizde şu bilgileri ekleyin:
- Python sürümü (`python --version`)
- İşletim sistemi
- Hatanın tam metni
- Nasıl tekrarlanacağı

## 💡 Özellik Talebi

Yeni bir özellik önermek için [GitHub Issues](https://github.com/recaiozil-wq/reymen-agean/issues/new/choose) sayfasını kullanın. Talebinizin:
- Ne yapmak istediğinizi
- Neden gerekli olduğunu
- Nasıl çalışması gerektiğini

açıklayın.

## 🔧 Geliştirme Ortamı

```bash
# Depoyu klonla
git clone https://github.com/recaiozil-wq/reymen-agean.git
cd reymen-agean

# Sanal ortam oluştur
python -m venv venv
source venv/bin/activate  # Linux
venv\Scripts\activate     # Windows

# Geliştirme bağımlılıkları
pip install -e ".[dev]"
```

## 📝 Kod Stili

- **Dil:** Türkçe (yorumlar ve değişken isimleri)
- **Formatter:** `ruff format`
- **Linter:** `ruff check`
- **Test:** `pytest`

Commit mesajları:
```
kategori: kısa açıklama

- Detay 1
- Detay 2
```

Kategoriler: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`

## 🧪 Test

```bash
pytest reymen/test/
```

## 🔄 Pull Request Süreci

1. Branch oluşturun: `git checkout -b feat/ozellik-adi`
2. Değişiklikleri yapın
3. Testleri çalıştırın: `pytest`
4. Commit: `git commit -m "feat: kisaca aciklama"`
5. Push: `git push origin feat/ozellik-adi`
6. GitHub'da PR açın
