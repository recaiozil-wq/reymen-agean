# GÖREV: ReYMeN'e ReYMeN Benzeri Hafıza Sistemi Ekle

## NE
ReYMeN ajanına ReYMeN'teki gibi kalıcı hafıza (memory) sistemi ekle.

## NEDEN
ReYMeN'te:
- MEMORY.md (50K karakter) — kalıcı notlar, ortam bilgileri, kullanıcı tercihleri
- USER.md (50K karakter) — kullanıcı profili
- Session search (FTS5) — geçmiş konuşmalarda arama
- Her oturumda otomatik yüklenir

ReYMeN'de zaten OnceHafiza ve session_search var ama ReYMeN'teki gibi yapılandırılmış memory sistemi yok.

## YAPILACAKLAR

### 1. MEMORY.md ve USER.md Oluştur
**Yer:** `reymen/hafiza/MEMORY.md` ve `reymen/hafiza/USER.md`

MEMORY.md formatı:
```markdown
# ReYMeN Hafıza

## Kullanıcı Tercihleri
- Dil: Türkçe
- Kısa ve öz cevaplar tercih edilir
- ...

## Ortam Bilgileri
- İşletim Sistemi: Windows 10/11
- Çalışma Dizini: ...
- ...
```

USER.md formatı:
```markdown
# Kullanıcı Profili

## İletişim Tarzı
- Çok kısa direkt komutlar
- Tablo formatında cevaplar sever
- ...

## Teknik Bilgiler
- ReYMeN Agent sahibi
- ReYMeN fork'u
- ...
```

### 2. Memory Yöneticisi Oluştur
**Yer:** `reymen/hafiza/memory_manager.py`

```python
"""
memory_manager.py — ReYMeN kalıcı hafıza yöneticisi.

ReYMeN'teki MEMORY.md + USER.md sisteminin ReYMeN versiyonu.
Her oturum başında hafızayı yükler, sonunda kaydeder.
"""

class MemoryManager:
    def __init__(self, memory_path: str = None, user_path: str = None):
        """Hafıza yöneticisini başlat."""

    def yukle(self) -> dict:
        """MEMORY.md ve USER.md'yi oku, içeriğini döndür."""

    def kaydet(self, memory_icerik: str, user_icerik: str):
        """Güncellenmiş hafızayı dosyaya yaz."""

    def guncelle(self, hedef: str, anahtar: str, deger: str):
        """Hafızada bir anahtarı güncelle (ör: yeni öğrenilen bilgi)."""

    def ekle(self, hedef: str, metin: str):
        """Hafızaya yeni bilgi ekle (sona append)."""

    def ozet(self) -> str:
        """Hafıza özeti: karakter sayısı, doluluk oranı."""
```

### 3. Oturum Açılışında Otomatik Yükle
**Yer:** `reymen/cereyan/conversation_loop.py` (güncelle)

Her konuşma başlangıcında:
```python
from reymen.hafiza.memory_manager import MemoryManager
mm = MemoryManager()
hafiza = mm.yukle()
# Hafızayı prompt'a ekle (sistem mesajı olarak)
```

### 4. Karakter Limiti Kontrolü
- MEMORY.md: max 50,000 karakter
- USER.md: max 50,000 karakter
- Limit aşılınca uyarı ver, en eski kayıtları buda

### 5. Session Arşivleme
ReYMeN'te olduğu gibi, eski session'lar `.ReYMeN/notes/` altında .md olarak saklansın. Bunun için `session_export` fonksiyonu ekle.

## DOĞRULAMA
- MEMORY.md ve USER.md var mı?
- MemoryManager import edilebiliyor mu?
- yukle() ve kaydet() çalışıyor mu?
- Karakter limiti kontrolü çalışıyor mu?

## YASAKLAR
- OnceHafiza'yı değiştirme (farklı bir sistem)
- Mevcut session_search.py'yi değiştirme
- Testleri bozma
