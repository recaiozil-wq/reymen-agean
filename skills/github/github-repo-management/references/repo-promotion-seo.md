---
skill_id: 9a5208188893
usage_count: 1
last_used: 2026-06-16
---
# Repo Promotion & SEO

Bir GitHub reposunu öne çıkarmak ve profesyonel göstermek için yapılması gerekenler.

## 1. Repo Açıklaması (Description)

```bash
gh repo edit <owner>/<repo> \
  --description "Kısa, net, dikkat çekici açıklama"
```

- Maksimum 350 karakter
- Anahtar rakamları ekle (örn. "1.038 modüler skill — 4.476 reference, 0 şişkin")
- Kullanıcıya değeri hemen göster

## 2. Konu Etiketleri (Topics)

```bash
gh repo edit <owner>/<repo> \
  --add-topic "konu1" \
  --add-topic "konu2"
```

En fazla 20 etiket. İyi seçilmiş topic'ler GitHub aramasında üst sıralara çıkarır.

**Örnek:** `hermes-agent`, `ai-agent`, `skills`, `modular`, `windows-automation`, `llm`, `skills-library`

## 3. LICENSE Dosyası

Repo köküne `LICENSE` dosyası ekle. GitHub otomatik tanır ve repo sayfasında gösterir.

```bash
# MIT License — en yaygın, "AS IS" garantisiz, copyright notice korunmalı
```

**Seçenekler:**

| Lisans | Kısıtlama | Garanti | Ne Zaman Kullanılır |
|--------|-----------|---------|-------------------|
| MIT | Sadece copyright notice koru | YOK | Herkes kullanabilsin ama ismin kalsın istiyorsan |
| Unlicense (Public Domain) | Hiçbir kısıtlama yok | YOK | "Ne yaparlarsa yapsınlar, hiçbir şart yok" |

**Önemli:** Kullanıcı "yasal yükümlülük vermesin" derse → **LICENSE dosyasını sil** veya **Unlicense** kullan. MIT bile copyright notice koruma şartı getirir.

## 4. Profesyonel README

| Bileşen | Açıklama |
|---------|----------|
| Logo | Resmi logo veya SVG — ortalanmış, genişlik 500-600px |
| Badge'ler | shields.io ile: skill sayısı, reference sayısı, kategori sayısı |
| İstatistik tablosu | Metrikleri net göster |
| Kategori yapısı | Klasör ağacı veya tablo |
| Hızlı başlangıç | Kullanıcının hemen kullanmaya başlayabileceği 3 satır |
| Bağlantılar | İlgili repo'lar |

**Badge örneği:**
```markdown
![skills](https://img.shields.io/badge/skills-1,038-6366f1?style=flat-square)
```

**Logo tercih sırası:**
1. Projenin resmi web sitesindeki logo (OG image)
2. Kendi tasarladığın SVG
3. text-only markdown

## 5. Social Preview (Paylaşım Görseli)

GitHub'da repo linki paylaşılınca çıkan görsel.

```bash
# OG image'i indir ve .github/ klasörüne koy
mkdir -p .github
curl -sL "https://ornek-site.com/og-image.png" -o .github/social-preview.png
```

Sonra GitHub'da **Settings > Social preview** kısmından manuel seç. Veya OG image zaten README'deyse GitHub otomatik kullanır.

## 6. Gereksiz Dosyaları Temizle

Repo kökünde skill dışı ne varsa sil veya taşı:

| Dosya/Dizin | Ne Yap |
|-------------|--------|
| `*.obsolete` | Sil |
| `manifest.json` (büyükse) | Sil veya `.gitignore` |
| `diagramming/`, `domain/`, `gifs/` | Konuyla ilgisizse sil |
| `__cleanup_deprecated_*` | Skill dizini altına taşınmışsa sil |

## 7. Doğrulama

```bash
# Repo bilgilerini kontrol et
gh repo view <owner>/<repo> --json description,topics,homepageUrl

# GitHub'da repo sayfasını aç
open "https://github.com/<owner>/<repo>"
```

## Sık Yapılan Hatalar

| Hata | Çözüm |
|------|-------|
| Açıklama çok uzun | 350 karakter sınırı, önemli rakamları öne koy |
| Topic eklenmemiş | Aramada görünmez, en az 5 topic ekle |
| LICENSE yok | GitHub "Add license" uyarısı gösterir |
| README'de logo kırık | URL'nin erişilebilir olduğunu kontrol et |
| Gereksiz dosyalar | Repo karmaşık görünür, ilk izlenim kötü olur |
| GitHub MCP push hatası (auth) | MCP Authentication Failed → `gh CLI` ile clone'la, dosyaları kopyala, commit+push yap |
| Social preview otomatik ayarlanmaz | `.github/social-preview.png` indir, GitHub Settings > Social preview'dan manuel seç |
