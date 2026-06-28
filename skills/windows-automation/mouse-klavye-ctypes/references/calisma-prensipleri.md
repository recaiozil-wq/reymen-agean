---
skill_id: 458651049a27
usage_count: 3
last_used: 2026-06-21
---
# Çalışma Prensibi, Sınırlamalar ve Kurulum

## Çalışma Prensibi

### Mouse
- `move`: `SetCursorPos` ile kademeli
- `move --fast`: `SendInput` + `MOUSEEVENTF_ABSOLUTE` + `VIRTUALDESK` (çoklu monitör)
- `click/rclick/dclick`: `SendInput` ile `MOUSEINPUT` struct
- `scroll`: `SendInput` + signed long maskesi (negatif scroll için)

### Klavye
- `type`: `KEYEVENTF_UNICODE` ile — Türkçe karakter, emoji dahil
- `key`: Sanal tuş (VK) kodları + modifier sıralaması (ctrl+shift+esc gibi)
- `KeyboardInterrupt` yakalaması — kesilince takılı tuş kalmaz

### Element
- PowerShell + .NET UIAutomationClient
- Parametreler temp JSON dosyası ile (güvenli, injection yok)
- Encoding: PowerShell `$OutputEncoding = [Text.Encoding]::UTF8` + Python `utf-8-sig` öncelikli
- Arama: Name → AutomationId → ClassName → ControlType
- Fallback: regex kısmi eşleşme
- `--timeout`: 0.5sn aralıklarla retry

### Workflow Motoru
- Adım tipleri: `click`, `dclick`, `rclick`, `move`, `type`, `key`, `wait`, `if_exists`, `screenshot`, `assert`, `repeat`
- `if_exists`: element varsa `then` alt-eylemini çalıştır, yoksa atla
- `assert`: element var (`present`) veya yok (`absent`) kontrolü, başarısızsa akışı durdurur
- `repeat`: alt-eylemi N kez tekrarla (`times` + `interval`)
- `screenshot`: akış içinde ekran görüntüsü al
- `on_error`: `stop` (varsayılan) veya `skip`
- `--dry-run`: adımları yürütmeden doğrula
- `--log log.json`: zaman damgalı JSON kaydı
- `shot_on_error`: hata anında otomatik ekran görüntüsü
- JSON (.json) ve düz metin (.txt) formatı
- Her adımda KeyboardInterrupt kontrolü

### Altyapı
- `_setup_ctypes()`: 7 Win32 API için argtypes/restype tanımı (64-bit güvenliği)
- `_set_dpi_awareness()`: 3 kademeli fallback (PerMonitorV2 → shcore → SetProcessDPIAware)
- `is_elevated()`: shell32.IsUserAnAdmin()
- UIPI uyarısı: elevated olmayan süreçte tıklama/yazma etkisiz kalabilir
- `virtual_screen()`: çoklu monitör desteği

---

## Sınırlamalar
- Oyunlar/DirectX/OpenGL uygulamaları: element bulma çalışmaz (UI Automation desteklemez)
- Elevated uygulamalar: ReYMeN elevated değilse tıklamalar sessizce yutulur (UIPI)
- Notepad: bu ortamda açılamayabilir (headless sandbox)

---

## Kurulum (GitHub)

```powershell
iex "& { $(irm https://raw.githubusercontent.com/Watcher-Hermes/hermes-mouse/master/install.ps1) }"
hermesmouse pos
```

Resmi repo: https://github.com/Watcher-Hermes/hermes-mouse

---
## Ek Adimlar / Varyasyon (2026-06-21T05:24:49Z)

KOMUT_CALISTIR: "cd /tmp && git clone https://github.com/Watcher-Hermes/ReYMeN-full-backup.git hermes_backup 2>&1"

---
## Ek Adimlar / Varyasyon (2026-06-21T05:34:56Z)

KOMUT_CALISTIR: "cd /tmp && git clone https://github.com/Watcher-Hermes/ReYMeN-full-backup.git 2>&1"
KOMUT_CALISTIR: "git clone https://github.com/Watcher-Hermes/ReYMeN-full-backup.git"
PYTHON_CALISTIR: "import subprocess; result = subprocess.run(['git', 'clone', 'https://github.com/Watcher-Hermes/ReYMeN-full-backup.git'], capture_output=True, text=True, timeout=60); print('STDOUT:', result.stdout); print('STDERR:', result.stderr); print('RC:', result.returncode)"
PYTHON_CALISTIR: "import subprocess; import os; result = subprocess.run(['find', '/', '-type', 'd', '-name', 'ReYMeN-full-backup'], capture_output=True, text=True, timeout=10); print('Konumlar:', result.stdout); print('Hata:', result.stderr)"
PYTHON_CALISTIR: "import os; print('CWD:', os.getcwd()); print('ls:', os.listdir('.'))"
PYTHON_CALISTIR: "import os; found = [];\nfor root, dirs, files in os.walk('C:/'):\n    if 'ReYMeN-full-backup' in dirs:\n        found.append(os.path.join(root, 'ReYMeN-full-backup'))\n        if len(found) >= 3:\n            break\nprint('Bulunanlar:', found)"
PYTHON_CALISTIR: "import os; path = 'C:/Users/marko/ReYMeN-full-backup'; print('İçerik:', os.listdir(path))"
PYTHON_CALISTIR: "import os; path = 'C:/Users/marko/ReYMeN-full-backup'; skills_path = os.path.join(path, 'skills'); \nif os.path.exists(skills_path):\n    skills = os.listdir(skills_path);\n    print(f'Skills sayısı: {len(skills)}');\n    print(f'İlk 10 skill: {skills[:10]}');\nelse:\n    print('Skills klasörü bulunamadı')"
PYTHON_CALISTIR: "import os; path = 'C:/Users/marko/ReYMeN-full-backup'; mem_path = os.path.join(path, 'Hermes Memor'); \nif os.path.exists(mem_path):\n    mem_items = os.listdir(mem_path);\n    print(f'Memory sayısı: {len(mem_items)}');\n    print(f'Memory içeriği: {mem_items[:20]}');\nelse:\n    print('Memory klasörü bulunamadı')"
PYTHON_CALISTIR: "import os; path = 'C:/Users/marko/ReYMeN-full-backup/Hermes Memor'; \nfiles = ['MEMORY.md', 'USER.md']; \nfor f in files:\n    fp = os.path.join(path, f);\n    if os.path.exists(fp):\n        with open(fp, 'r', encoding='utf-8', errors='ignore') as fh:\n            content = fh.read();\n            print(f'=== {f} ({len(content)} karakter) ===');\n            print(content[:500]);\n            print('...');\n    else:\n        print(f'{f} bulunamadı')"
PYTHON_CALISTIR: "import os; \npath = 'C:/Users/marko/ReYMeN-full-backup/Hermes Memor'; \nfiles = ['MEMORY.md', 'USER.md']; \nfor f in files:\n    fp = os.path.join(path, f);\n    with open(fp, 'r', encoding='utf-8', errors='ignore') as fh:\n        content = fh.read();\n    # Hafızaya kaydetmek için yazdır\n    print(f'\\n\\n=== {f} İÇERİĞİ ===\\n{content}\\n=== {f} SONU ===')"
PYTHON_CALISTIR: "import os; path = 'C:/Users/marko/ReYMeN-full-backup/Hermes Memor/MEMORY.md'; \nwith open(path, 'rb') as f:\n    raw = f.read();\n# Sadece yazdırılabilir karakterleri al\ntext = raw.decode('utf-8', errors='replace');\nprint('MEMORY.md içeriği yüklendi, karakter sayısı:', len(text))"
PYTHON_CALISTIR: "import os; path = 'C:/Users/marko/ReYMeN-full-backup/Hermes Memor/USER.md'; \nif os.path.exists(path):\n    with open(path, 'rb') as f:\n        raw = f.read();\n    text = raw.decode('utf-8', errors='replace');\n    print('USER.md içeriği yüklendi, karakter sayısı:', len(text));\nelse:\n    print('USER.md bulunamadı')"
PYTHON_CALISTIR: "import os; path = 'C:/Users/marko/ReYMeN-full-backup/Hermes Memor/MEMORY.md'; \nwith open(path, 'rb') as f:\n    raw = f.read();\ntext = raw.decode('utf-8', errors='replace');\n# İlk 2000 karakteri göster\nprint(text[:2000])"
HAFIZA_ARA: "[HAFIZA_KAYIT] MEMORY.md: ZORUNLU KURAL - VS CODE YAZMA: Kullanıcı VS Code'a yaz dediğinde vscode_yaz.bat çalıştır. ZORUNLU KURAL - KONUM KAYDET: konum kaydet dendiğinde find_caret.py çalıştır. KULLANICI TERCIHLERİ: UTF-8 kullan, API key'i asla yazdırma"
PYTHON_CALISTIR: "import os; path = 'C:/Users/marko/ReYMeN-full-backup/Hermes Memor/USER.md'; \nwith open(path, 'rb') as f:\n    raw = f.read();\ntext = raw.decode('utf-8', errors='replace');\nprint(text)"
HAFIZA_ARA: "[HAFIZA_KAYIT] USER.md: Skill yükleme/güncelleme çift yönlü: (1) Hermes local skill kütüphanesine yükle, (2) GitHub Watcher-Hermes/hermes-skills reposuna push et, (3) README.md güncelle. Teknik olarak kesin ve doğrulanmış bilgi bekler."
PYTHON_CALISTIR: "import os; skills_path = 'C:/Users/marko/ReYMeN-full-backup/skills'; \nfirst_skill = os.path.join(skills_path, '3d-pipeline'); \nprint('3d-pipeline içeriği:', os.listdir(first_skill) if os.path.isdir(first_skill) else 'dizin değil')"
PYTHON_CALISTIR: "import os; skills_path = 'C:/Users/marko/ReYMeN-full-backup/skills'; \nfirst_skills = ['3d-pipeline', 'a2a-agent-spec', 'a2a-integrator']; \nfor s in first_skills[:3]:\n    sp = os.path.join(skills_path, s, 'SKILL.md');\n    if os.path.exists(sp):\n        with open(sp, 'rb') as f:\n            raw = f.read();\n        text = raw.decode('utf-8', errors='replace');\n        print(f'\\n=== {s} ===\\n{text[:300]}...');\n    else:\n        print(f'{s} SKILL.md bulunamadı')"
PYTHON_CALISTIR: "import os; skills_path = 'C:/Users/marko/ReYMeN-full-backup/skills'; \nskills = sorted(os.listdir(skills_path)); \nprint(f'Toplam {len(skills)} skill'); \n# Tüm skill isimlerini yazdır\nfor i, s in enumerate(skills):\n    print(f'{i+1}. {s}')"
PYTHON_CALISTIR: "import os; skills_path = 'C:/Users/marko/ReYMeN-full-backup/skills'; \nskills = sorted(os.listdir(skills_path)); \nsummary = []; \nfor s in skills[:50]:  # İlk 50 skill için\n    sp = os.path.join(skills_path, s, 'SKILL.md');\n    desc = '';\n    if os.path.exists(sp):\n        with open(sp, 'rb') as f:\n            raw = f.read();\n        text = raw.decode('utf-8', errors='replace');\n        # description satırını bul\n        for line in text.split('\\n'):\n            if line.startswith('description:'):\n                desc = line.replace('description:', '').strip();\n                break;\n    summary.append(f'{s}: {desc}');\nprint('\\n'.join(summary))"
PYTHON_CALISTIR: "import os; skills_path = 'C:/Users/marko/ReYMeN-full-backup/skills'; \nskills = sorted(os.listdir(skills_path)); \nall_skills = []; \nfor s in skills:\n    sp = os.path.join(skills_path, s, 'SKILL.md');\n    desc = '';\n    if os.path.exists(sp):\n        with open(sp, 'rb') as f:\n            raw = f.read();\n        text = raw.decode('utf-8', errors='replace');\n        for line in text.split('\\n'):\n            if line.startswith('description:'):\n                desc = line.replace('description:', '').strip().strip('\"');\n                break;\n    all_skills.append(f'{s}: {desc}');\n# Dosyaya yaz\noutput_path = 'C:/Users/marko/ReYMeN-full-backup/skills_summary.txt';\nwith open(output_path, 'w', encoding='utf-8') as f:\n    f.write('\\n'.join(all_skills));\nprint(f'{len(all_skills)} skill özeti yazıldı: {output_path}')"
PYTHON_CALISTIR: "import os; skills_path = 'C:/Users/marko/ReYMeN-full-backup/skills'; skills = sorted(os.listdir(skills_path)); all_skills = []; \nfor s in skills:\n    sp = os.path.join(skills_path, s, 'SKILL.md');\n    desc = '';\n    if os.path.exists(sp):\n        with open(sp, 'rb') as f:\n            raw = f.read();\n        text = raw.decode('utf-8', errors='replace');\n        for line in text.split('\\n'):\n            if 'description:' in line:\n                desc = line.split('description:')[1].strip().strip('\"');\n                break;\n    all_skills.append(f'{s}: {desc}');\noutput_path = 'C:/Users/marko/ReYMeN-full-backup/skills_summary.txt';\nwith open(output_path, 'w', encoding='utf-8') as f:\n    f.write('\\n'.join(all_skills));\nprint(f'{len(all_skills)} skill yazildi: {output_path}')"
PYTHON_CALISTIR: "import os\nskills_path = 'C:/Users/marko/ReYMeN-full-backup/skills'\nskills = sorted(os.listdir(skills_path))\nall_skills = []\nfor s in skills:\n    sp = os.path.join(skills_path, s, 'SKILL.md')\n    desc = ''\n    if os.path.exists(sp):\n        with open(sp, 'rb') as f:\n            raw = f.read()\n        text = raw.decode('utf-8', errors='replace')\n        for line in text.split('\\n'):\n            if 'description:' in line:\n                desc = line.split('description:')[1].strip().replace(chr(34), '')\n                break\n    all_skills.append(s + ': ' + desc)\noutput_path = 'C:/Users/marko/ReYMeN-full-backup/skills_summary.txt'\nwith open(output_path, 'w', encoding='utf-8') as f:\n    f.write('\\n'.join(all_skills))\nprint(str(len(all_skills)) + ' skill yazildi: ' + output_path)"
PYTHON_CALISTIR: "import os\npath = 'C:/Users/marko/ReYMeN-full-backup/skills_summary.txt'\nsize = os.path.getsize(path)\nprint(f'Dosya boyutu: {size} bytes ({size/1024:.1f} KB)')\n# İlk 5 ve son 5 satırı göster\nwith open(path, 'r', encoding='utf-8') as f:\n    lines = f.readlines()\nprint(f'Toplam satir: {len(lines)}')\nprint('Ilk 5:')\nfor l in lines[:5]:\n    print(l.strip())\nprint('...\\nSon 5:')\nfor l in lines[-5:]:\n    print(l.strip())"
HAFIZA_ARA: "skills_summary.txt dosyasındaki 540 skill özetini hafızama kaydet. Dosya yolu: C:/Users/marko/ReYMeN-full-backup/skills_summary.txt"
