---
skill_id: 8c3d098dd90d
usage_count: 1
last_used: 2026-06-16
---
# varsa all_stems'te kontrol
```

### 2. Link Onarımı

**Kırık link türleri ve çözümleri:**

| Tür | Çözüm |
|-----|-------|
| Var olmayan skill notu (vllm, gguf vb.) | `[[link]]` → `\`link\`` |
| Koordinat formatı (`[[500, 375]]`) | `[[500, 375]]` → `` `[500, 375]` `` |
| `skills/XXX` formatı (Obsidian'a skill yazarken oluşur) | `skills/xxx` → `[[xxx]]` regex toplu dönüşümü: `re.sub(r'\[\[skills/([^\]]+?)\]\]', r'[[\1]]', content)` |
| `ReYMeN/Skills/xxx/yyy` formatı (eski yol) | `re.sub(r'\[\[ReYMeN/Skills/[^\]]+?\]\]', lambda m: '[[' + m.group(0)[2:-2].split('/')[-1] + ']]', content)` |
| `ReYMeN/Cron/xxx` formatı | `re.sub(r'\[\[ReYMeN/Cron/([^\]]+?)\]\]', r'[[\1]]', content)` |
| `ReYMeN/Skills/MOC - ...` gibi özel isimler | `content.replace('[[ReYMeN/Skills/MOC - X]]', '[[MOC - X]]')` — elle tek tek |
| Eğitim amaçlı örnekler (`[[wikilinks]]`) | Kod bloğuna çevir |
| Kategori/alt yol linkleri (`windows-automation/vscode-ac`) | Obsidian'da `windows-automation\vscode-ac` dosyasına yönlendir |
| JavaNotes .png360/.webp uzantı hataları | `.png360` → `.png` (gerçek dosya adı) |

**Önemli:** Kırık link sayarken Obsidian'ın otomatik oluşturduğu "Pasted image" referanslarını yanlış sayma. Obsidian görüntü dosyalarını otomatik linkler, onlar kırık değildir.

### 3. Orphan Temizleme

Orphan = hiçbir yerden `[[link]]` almayan dosya.

**Politika (üç aşamalı):**

**Aşama 1 — Beklenen orphan'ları filtrele:**
- `_*_index.md` — index dosyaları beklenen orphan'dır, atla
- `README.md` — MOC başlığı, atla (kendini bağlamaz)
- `Cron.md`, `subprocess-hata-cozme.md` gibi `redirect` içerenler — atla
- `Knowledge/Skills-legacy/*` — arşiv altındaki dosyalar beklenir, atla

**Aşama 2 — Gerçek orphan'ları MOC ile bağla:**
- Knowledge klasörü → `Knowledge/README.md` MOC oluştur, tüm notları alfabetik listele
- JavaNotes gibi ayrı klasörler → `KlasorAdi/README.md` MOC oluştur
- Skills/ kökündeki anlamlı dosyalar (Hibrit AI, Dolphin vb.) → `_Skills_index.md`'ye link ekle

**Aşama 3 — Eski/Skills-root legacy taşıma:**
- Skills/ kökündeki `DESCRIPTION.md`, `SKILL.md`, `README.md` gibi ReYMeN repo'dan kalan dosyalar → `Knowledge/Skills-legacy/` altına taşı
- `<50` satırlık taslak/boş skill şablonları → aynı arşive taşı
- Anlamlı içerikli dosyalar (Hibrit AI Mimarisi, dolphin-llama3, self-improvement vb.) → olduğu yerde kal, _Skills_index'e ekle

**MOC oluşturma şablonu:**
```markdown