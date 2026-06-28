---
skill_id: 0382b30a0834
usage_count: 1
last_used: 2026-06-16
---
## Pitfalls

0. **ÖNCE regex taraması — replace için tam formatı doğrula:** Kırık link düzeltirken `[[hedef|görünen]]` formatını `[[hedef]]` ararken kaçırma. `re.findall(r'\\[\\[([^\\]|]+?)(?:[|#][^\\]]*)?\\]\\]', content)` ile tarama yaptığında formattan `|görünen` kısmı ayrışır, ama sonra Python `str.replace('[[hedef]]', ...)` ile düzeltme yaparken `[[hedef|görünen]]` eşleşmez. **Çözüm:** replace yapmadan önce content içinde tam string'i (pipe dahil) kontrol et:
   `if '[[hedef|görünen]]' in content:` — varsa o haliyle replace et.

0. **Büyük vault tarama performansı (1000+ dosya):** Ana vault 1456 dosya, ReYMeN/ 304 dosya iken tek bir `os.walk` + tüm dosyaları `read_text()` ile tarama 3-5 saniye sürer. Script'i yazarken:
   - `os.walk`'ı 1 kere çalıştır, `existing` set'ini oluştur, sonra 2. turda her dosyayı oku
   - Regex derlemesini loop dışında yap: `pattern = re.compile(r'\\[\\[([^\\]]+?)\\]\\]')`
   - `.gitignore`, `.obsidian/` ve `node_modules/` altını atla
   - İki vault'u (ana + ReYMeN/) ayrı ayrı tara, aynı script içinde iki tarama çalıştır

0. **Ana vault + ReYMeN alt vault çapraz linkleri:** Ana vault (`JavaNotes/`) ReYMeN/ altındaki sayfalara link verirse, Ana vault taraması ReYMeN/ dosyalarını `existing` set'ine katmazsa kırık sayar. **Çözüm:** Her iki vault'un dosyalarını da `existing` set'ine ekle, link kaynağına bakmaksızın her vault'taki tüm linkleri kontrol et.

1. **`_README` gibi özel isimli dosyalar:** ReYMeN GitHub repo'sundan kalan `[[_README|açıklama]]` linkleri vault'ta `_README.md` olmadığı için her zaman kırıktır. Bunları inlint code'a (`\`_README\``) çevir. Ama `_software-development_index` gibi gerçek index dosyalarına yapılan linkleri KARIŞTIRMA — onlar vault'ta var.

2. **Windows'ta `\` vs `/` yolları:** Obsidian wikilink'leri `/` kullanır (`windows-automation/vscode-ac`), ama filesystem `\` bekler. Link çözümlemede her iki formata da bak.
2. **re.sub group reference hatası:** Python 3.14'te `re.sub(r'...', r'`\1, \2`', ...)` backtick içindeki `\1` çalışmaz. Lambda fonksiyon kullan.
3. **Obsidian'in otomatik resim linkleri:** `[[Pasted image 2023...]]` gibi linkler gerçekte `.png` dosyalarıdır, Obsidian vault assets klasöründe durur. Kırık link sayma bunları yanlış pozitif olarak raporlayabilir — kontrol et.
4. **Skill notlarının orphan görünmesi:** Bir skill notu kendi kategorisi dışında hiçbir yerde referans alınmamış olabilir. Bu durumda `_category_index.md`'ye ekleyerek düzelt.
5. **Python 3.14 ile re.sub:** Backreference içeren stringlerde backtick karakter sorunu yaratır. Her zaman lambda fonksiyon kullan:
   ```python
   content = re.sub(r'\[\[(\d+),\s*(\d+)\]\]',
                    lambda m: f'`[{m.group(1)}, {m.group(2)}]`',
                    content)
   ```
7. **`skills/XXX` formatında linkler:** Obsidian'a skill notları yazılırken `skills/XXX` formatında linkler oluşabilir (`[[skills/hermes-agent]]`). Bunları topluca `[[XXX]]`'e çevir:
   ```python
   content = re.sub(r'\[\[skills/([^\]]+?)\]\]', r'[[\1]]', content)
   ```
   Bu regex **en son** uygulanmalı — önce diğer tüm düzeltmeler yapılmalı.

8. **Redirect notları oluştur:** Eski isimle var olmayan ama eski linklerin yöneldiği sayfalar için (Cron, gece-gelistirme, MOC - Windows Otomasyon, subprocess-hata-cozme) kısa redirect notları oluştur. İçinde sadece `➡️ [[hedef]]` yazsın.

9. **execute_code içinde write_file sınırı:** `execute_code` tool call limitine (50) takılabilir. Çok sayıda dosya düzeltilecekse direkt `open(path, 'w').write(content)` kullan — tool call limitini harcamaz. `from hermes_tools import write_file` import etme, direkt Python file I/O yap.

10. **Kontrol scriptinde alt klasör eşleme:** Sadece `stem` ile eşleme yapma — `ReYMeN/skills/autonomous-ai-agents/_autonomous-ai-agents_index`'e link `[[autonomous-ai-agents/_autonomous-ai-agents_index]]` şeklinde olabilir. `existing` set'ine tüm `relpath`'leri koy ve `endswith('/' + target)` ile kontrol et.
7. **ReYMeN/Knowledge klasörü:** `ReYMeN/Knowledge/` yoksa `mkdir -p` ile oluştur. Dosya taşıma için `terminal(mv)` kullan.