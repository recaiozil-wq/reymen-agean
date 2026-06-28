---
name: autonomous-ai-agents_claude-code_references_windows-orchestration-bridge
description: Claude Code — Hermes Orchestration Guide (Windows)
title: "Autonomous Ai Agents Claude Code References Windows Orchestration Bridge"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Claude Code — Hermes Orchestration Guide (Windows) |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Claude Code — Hermes Orchestration Guide (Windows)

Hermes'i Claude Code ile koordine ederek **analiz → kod düzeltme** iş akışı. Hermes bulguyu yapar, Claude Code düzeltmeyi kodlar.

## Desteklenen Yöntemler

| Yöntem | Araç | Onay Gerekir? | İzleme |
|--------|------|---------------|--------|
| **VS Code GUI Bridge** | `vscode_yaz.bat` | Hayır (önceden tıklanmışsa) | Ekran görüntüsü ile |
| **CLI Print Mode** | `claude -p "..."` | Hayır | Terminal çıktısı |
| **CLI Interactive** | `claude` (PTY) | Evet (trust + permissions) | PTY log |


## Yöntem 1: VS Code GUI Bridge (Windows)

Hermes'in bulgularını VS Code içindeki Claude Agent sohbet kutusuna iletir.

### Pipeline

```
🧠 Hermes (analiz + strateji)
   ↓  "Şu kodu düzelt: ..."
📝 vscode_yaz.bat <mesaj>
   ↓  pyautogui clipboard yapıştır + Enter
🛠️ VS Code Claude Agent (kodu düzeltir)
```

### Script'ler

| Script | Yol | Açıklama |
|--------|-----|----------|
| `vscode_yaz.bat` | `C:\Users\marko\AppData\Local\hermes\scripts\vscode_yaz.bat` | Giriş noktası — metni alır, Python scriptine yönlendirir |
| `vscode_ctrl.py` | `C:\Users\marko\AppData\Local\hermes\scripts\vscode_ctrl.py` | VS Code'u bulur, Command Palette açar, Claude Focus on Chat Input çalıştırır, clipboard yapıştırır, Enter gönderir |

### Çalışma Prensibi

1. `vscode_ctrl.py` EnumWindows ile VS Code penceresini bulur
2. `SetForegroundWindow` + `ShowWindow(SW_SHOWMAXIMIZED)` ile öne getirir
3. `Ctrl+Shift+P` → Command Palette açar
4. `typewrite("Claude: Focus on Chat Input")` yazar → Enter
5. `Set-Clipboard` PowerShell ile mesajı panoya kopyalar
6. `Ctrl+A` → `Ctrl+V` → `Enter` ile Claude'a gönderir

### Windows'a Özel Püf Noktalar

| # | Sorun | Çözüm |
|---|-------|-------|
| 1 | `SetForegroundWindow` bazen başarısız olur | Önce Alt+Tab bypass'ı dene (WScript.Shell SendKeys), sonra SetForegroundWindow |
| 2 | VS Code açık değilse | `code <proje_dizini>` ile önce VS Code'u aç |
| 3 | Clipboard tırnak karakterleri bozulur | `text.replace("'", "\`")` veya Python ile doğrudan `win32clipboard` kullan |
| 4 | Odak yanlış yere giderse | 4 farklı foreground denemesi yap (alt+tab, görev çubuğu, window text match) |
| 5 | Claude sohbet kutusu koordinatı değişir | Asla sabit koordinat kullanma — Command Palette yöntemi kullan |
| 6 | **Bash özel karakterler** (parantez/yıldız/tek tırnak) terminal argümanında kaybolur | Uzun/kompleks mesajları doğrudan `vscode_yaz.bat <mesaj>` ile gönderme. Önce bir temp dosyaya yaz, sonra Python 3.14 ile okuyup `clip.exe` + `pyautogui` ile elle gönder (aşağıdaki script) |

### Ne Zaman Kullanılır

- Kullanıcı VS Code'da değişiklikleri manuel izlemek istediğinde
- Claude Agent'ın yaptığı değişiklikleri görmek istediğinde
- `claude` komutu terminalde çalışmıyorsa (OAuth/PATH sorunu)


## Yöntem 2: CLI Print Mode (Onay Gerektirmez)

```bash
claude -p "Şu kodu düzelt: ..." --allowedTools "Read,Edit,Write,Bash" --max-turns 30
```

Detay: `claude-code-cli-autonomous` skill'ine bak.


## İş Akışı: Hermes → Claude Code

```
1. ANALİZ — Kodu tara, hatayı bul, çözüm stratejisi belirle
2. KOMUT OLUŞTUR — Hedef dosyaları belirt, ne yapılacağını net yaz
3. VS CODE'A GÖNDER — vscode_yaz.bat <komut> ile Claude Agent'a yapıştır
4. KONTROL ET — Ekran görüntüsü al veya dosyaları doğrula
5. KAYDET — Çözümü skill/memory/Obsidian olarak kaydet
```

## İlgili Dosyalar

| Dosya | Konum |
|-------|-------|
| `vscode_yaz.bat` | `C:\Users\marko\AppData\Local\hermes\scripts\vscode_yaz.bat` |
| `vscode_ctrl.py` | `C:\Users\marko\AppData\Local\hermes\scripts\vscode_ctrl.py` |
| Claude Code CLI | `C:\Users\marko\AppData\Roaming\npm\claude.cmd` |
