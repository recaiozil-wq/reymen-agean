
> **Kategori:** Verimlilik

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Productivity_Agent Conduct Framework_References_Karar Agaci |
| **Nerede?** | Verimlilik/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# Karar Ağacı — ReYMeN Agent Flow

Bu referans conversation_loop.py'daki karar ağacını belgeler.

## Tam Akış

```
GÖREV ← Kullanıcı mesajı
  ↓
[A] task_id = uuid4
  ↓
[B] Session başlat
  ↓
[C] Budget oluştur
  ↓
[D] ONCE_HAFIZA KONTROLÜ (conversation_loop.py:400-444)
  │
  ├── OnceHafiza.hafizada_ara(hedef, kategori)
  │   ├── FTS5 skills ara
  │   ├── SQL tam eşleşme ara
  │   └── SQL LIKE (kısmi) eşleşme ara
  │
  ├── Bulundu + guven > 0.8
  │   ├── LOG: "HAFIZA ATLAMASI: guven=%.2f > 0.8"
  │   ├── sonuc["basarili"] = True
  │   ├── sonuc["yanit"] = hafiza_sonuc["cozum"]
  │   ├── sonuc["hafiza_atlama"] = True
  │   ├── budget.gorev_tamamla()
  │   └── RETURN (0 LLM çağrısı, ~%60 maliyet düşüşü)
  │
  ├── Bulundu + guven 0.5-0.8
  │   ├── "belirsiz" durumu
  │   ├── Konuşmaya system mesajı olarak ekle (LLM referans alsın)
  │   └── DEVAM → LLM döngüsü
  │
  └── Bulunamadı
      ├── self._onceki_bilgi = None
      └── DEVAM → LLM döngüsü
  ↓
[E] ONCELIK_CACHE (selamlaşma/teşekkür bypass)
  ├── hedef_alt in ONCELIK_CACHE
  ├── LOG: "CACHE ATLAMASI: 'selam' eslesmesi"
  ├── sonuc["kaynak"] = "cache"
  └── RETURN (0 LLM)
  ↓
[F] LLM DÖNGÜSÜ (while budget.devam_etmeli_mi)
  │
  ├── Circuit breaker kontrolü
  │   └── cb_acik → "KALICI DURDURMA: 3/3 ardisik hata" → BREAK
  │
  ├── Takılma dedektörü
  │   └── aynı eylem 3x → BREAK
  │
  ├── Context preflight (threshold > %50 → sıkıştır)
  ├── API mesajları oluştur
  ├── Ephemeral layerlar ekle
  ├── Prompt caching (Anthropic)
  ├── _interruptible_api_call()
  │   └── max_retry=3, exponential backoff
  ├── Yanıt parse et
  │   ├── tool_calls → _arac_calistir() → loop
  │   └── text response → persist → RETURN
  └── Budget++
  ↓
[G] ÇIKIŞ KOŞULLARI (8 adet)
  1. Hafıza guven > 0.8 (0 LLM)
  2. Cache eşleşmesi (0 LLM)
  3. tool.tamamlandi=true
  4. LLM "GOREV_BITTI" dedi
  5. Budget doldu (90 tur)
  6. Takılma (3x aynı eylem)
  7. Circuit breaker (3 ardışık hata, kalıcı)
  8. Ctrl+C kullanıcı iptali
```

## Sabitler

```python
CIRCUIT_BREAKER_MAX_HATA = 3   # 3 ardışık hata → kalıcı dur
CIRCUIT_BREAKER_KALICI = True   # kullanıcı müdahalesi ister
CIRCUIT_BREAKER_SURESI = 0      # otomatik açılmaz
MAX_RETRY = 3                    # max 3 API denemesi
TAKILMA_ESIĞI = 3               # aynı eylem 3x → dur
MAX_TUR = 90                     # max conversation turu

ONCELIK_CACHE = {
    "merhaba": "Merhaba! Size nasıl yardımcı olabilirim?",
    "selam": "Selam! Nasıl yardımcı olabilirim?",
    "teşekkür": "Rica ederim!",
    ...
}
```

## Dosyalar

| Dosya | İçerik |
|-------|--------|
| `reymen/cereyan/conversation_loop.py` | Ana karar ağacı |
| `reymen/cereyan/once_hafiza.py` | Hafıza-öncelikli API (kaydet, ara, isle) |
| `reymen/hafiza/gorev_once_kontrol.py` | Görev öncesi 5 katmanlı kontrol |
| `reymen/sistem/once_hafiza.py` | Class-based OnceHafiza wrapper |
