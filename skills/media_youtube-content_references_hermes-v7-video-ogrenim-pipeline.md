
> **Kategori:** Medya

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Video ajanı |
| **Ne?** | Media_Youtube Content_References_Hermes V7 Video Ogrenim Pipeline |
| **Nerede?** | Medya/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# Hermes v7 Video Öğrenim Pipeline

## Ne Zaman Kullanılır

Kullanıcı sadece bir YouTube URL'si paylaştığında (başka açıklama yok, sadece link). ASLA özet veya transkript yapma — doğrudan pipeline'ı çalıştır.

## Pipeline Konumu

```
C:\Users\marko\OneDrive\Desktop\hermes_v7\hermes_v7.py
```

## Çalıştırma Komutu

```powershell
python "C:\Users\marko\OneDrive\Desktop\hermes_v7\hermes_v7.py" --debug-video "<URL>"
```

## Çıktının Taşınması

Pipeline bitince oluşan `.md` dosyasını (genellikle `knowledge_base/...` altında) şu vault yoluna kopyala:

```
C:\Users\marko\OneDrive\Belgeler\Obsidian Vault\YouTube Öğrenimler\
```

## Kullanıcıya Rapor Formatı

```
✓ Video öğrenildi: <başlık>
  Skill: <dosya_adı>.md
  Kategori: <kategori>
  Güven: <skor>/100
  Vault: YouTube Öğrenimler/<dosya_adı>.md
```
