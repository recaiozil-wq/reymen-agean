# GÖREV: ReYMeN'i Hermes Seviyesine Getir

## NE
ReYMeN ajanının çıktı kalitesini, hata yönetimini ve kullanıcı deneyimini Hermes Agent seviyesine yükselt.

## SORUNLAR

### 1. Log Karmaşası — Kullanıcıya Gereksiz Log Gösteriliyor
**Yer:** `reymen/cereyan/conversation_loop.py` ve `reymen/cereyan/beyin.py`

**Sorun:** `[WARNING]` ve `[INFO]` mesajları terminalde kullanıcıya görünüyor.
**Çözüm:** Tüm print/log çıktılarını DEBUG seviyesine çek. Kullanıcıya sadece:
- Sohbet cevapları
- Hata mesajları (sadece önemli olanlar)
- İşlem başlangıç/bitiş bildirimleri

**Yapılacak:**
- `beyin.py`'deki print() ve log.warning() çağrılarını kontrol et
- conversation_loop.py'deki gereksiz print()'leri sil veya DEBUG'a çek
- Hata durumunda kullanıcıya sadece "Bir hata oluştu, tekrar deniyorum..." gibi kısa mesaj göster

### 2. BudgetConfig.provider_maliyeti Hatası
**Yer:** `reymen/cereyan/beyin.py` (1325. satır civarı)

**Sorun:** `BudgetConfig` objesinde `provider_maliyeti` attribute'u yok.
**Çözüm:** 
```python
# HATALI:
maliyet = self.budget_config.provider_maliyeti

# DOĞRU:
maliyet = getattr(self.budget_config, 'provider_maliyeti', 0)
```
Veya `budget_config.py`'ye `provider_maliyeti` property'si ekle.

### 3. Cevap Formatı — Hermes Gibi Olmalı
**Yer:** `reymen/cereyan/conversation_loop.py` (yanit hazirlama kısmı)

**Sorun:** ReYMeN'in cevapları ham metin, Hermes'teki gibi düzenli değil.
**Çözüm:** Cevap formatını şu şablona uydur:
```
[emoji] [Başlık]

[kısa açıklama]

| Kolon 1 | Kolon 2 |
|---------|---------|
| değer 1 | değer 2 |

[altta yorum]
```

**Yapılacak:**
- `_format_yanit()` fonksiyonu ekle (veya mevcut formatı geliştir)
- Emoji + başlık ile başla
- Tablo varsa düzgün formatla
- Gereksiz boşlukları temizle

### 4. Web Sonucu LLM'i Atlıyor
**Yer:** conversation_loop.py

**Sorun:** Web'den alınan veri LLM'e prompt olarak gidiyor, LLM kendi bilgisiyle cevap veriyor.
**Çözüm:** Web sonucu varsa LLM'i tamamen atla, direkt web verisini dön.

### 5. Tarih Doğrulaması
**Yer:** conversation_loop.py veya beyin.py

**Sorun:** 28 Haziran yerine 29 demiş.
**Çözüm:** Tarih sorgularında `datetime.now()` kullan, LLM'a güvenme.

## YAPILACAKLAR (SIRALI)

### Adım 1: Log Temizliği
```python
# conversation_loop.py'de:
import logging
logging.getLogger('reymen').setLevel(logging.WARNING)
# veya kullanıcıya sadece cevabı göster, log'ları gizle
```

### Adım 2: BudgetConfig Fix
```python
# budget_config.py veya beynin.py'de:
# provider_maliyeti yoksa 0 döndür
```

### Adım 3: Cevap Formatlama
```python
def _format_yanit(self, yanit: str) -> str:
    """Yanıtı Hermes formatına çevir."""
    # Emoji + başlık
    # Tablo formatı
    # Gereksiz satırları temizle
```

### Adım 4: Web Verisi Direkt Dön
```python
if web_sonucu:
    return web_sonucu  # LLM'i atla
```

## DOĞRULAMA
- `python -m pytest tests/ -x --timeout=10 -q` geçiyor mu?
- Log'lar terminalde görünmüyor mu?
- Cevap formatı Hermes'teki gibi mi?

## YASAKLAR
- Kod mantığını değiştirme
- Testleri bozma
