
> **Kategori:** Verimlilik

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Productivity_Agent Conduct Framework_References_Decision Template |
| **Nerede?** | Verimlilik/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# Decision Log Formatı

Her karar aşağıdaki formatta `.ReYMeN/decisions.md`'ye eklenir.

## Şablon

```markdown
## Karar #N — Kısa Başlık

**Tarih:** YYYY-MM-DD
**Karar veren:** ReYMeN

### Ne yapıldı?
[2-3 cümle, ne yapıldı]

### Neden?
[1-2 cümle, kararın gerekçesi]

### Alternatif düşünüldü mü?
- **Alternatif 1:** [açıklama] → elenme sebebi
- **Alternatif 2:** [açıklama] → elenme sebebi
- **Seçilen:** [neden bu kazandı]

### Bağlantılar
- Varsa ilgili session id'leri
- Varsa ilgili dosya yolları
- Varsa kaynak/referans
```

## Örnek

```markdown
## Karar #1 — Öncelik: Karar Döngüsü

**Tarih:** 2026-06-21
**Karar veren:** ReYMeN

### Ne yapıldı?
5 mühendislik kararı arasından Karar Döngüsü ilk uygulanacak karar olarak seçildi.

### Neden?
Diğer 4 karar tek seferlik kurallar. Döngü metasistem — kararların unutulmasını,
tekrarını, bağlam kaybını engelliyor. Döngü olmazsa hiçbir karar kalıcı olmaz.

### Alternatif düşünüldü mü?
- **Sub-Agent kuralı:** Ana thread temizliği büyük kazanç ama hangi kararların
  sub-agent'a gideceğini belirleyen yine döngü.
- **No Goblins:** Direktlik kazandırır ama kural koymak yetmez, döngüyle
  pekiştirmek gerekir.
- **Cave Modu / Status Line:** Operasyonel iyileştirmeler, stratejik değil.

### Bağlantılar
- Karar #2: Sub-Agent Kuralı (sıradaki)
- Diğer 4 karar bu döngü içinde değerlendirilecek
```

## Kurallar

1. **Her karar kaydedilir.** Küçük bile olsa, tekrar etme potansiyeli varsa yaz.
2. **Alternatif her zaman yazılır.** "Alternatif yoktu" bile geçerli.
3. **Geçmiş kontrol edilir.** `session_search` ile aynı senaryo daha önce
   çözülmüş mü diye bak — tekrar karar verme.
4. **Yargılama yok.** Sadece izle, sor, kaydet, bağla.
