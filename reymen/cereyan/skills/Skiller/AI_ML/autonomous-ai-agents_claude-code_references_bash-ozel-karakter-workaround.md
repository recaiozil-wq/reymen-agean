---
name: autonomous-ai-agents_claude-code_references_bash-ozel-karakter-workaround
description: Bash Özel Karakter Workaround — VS Code Claude Terminal
title: "Autonomous Ai Agents Claude Code References Bash Ozel Karakter Workaround"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Bash Özel Karakter Workaround — VS Code Claude Terminal |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Bash Özel Karakter Workaround — VS Code Claude Terminal

## Sorun

`vscode_yaz.bat <mesaj>` ile uzun mesaj gönderirken **git-bash terminali** şu karakterleri yorumlar:

| Karakter | Sorun |
|----------|-------|
| `(`, `)` | Subshel açmaya çalışır — `syntax error near unexpected token` |
| `*` | Globbing yapar |
| `'` (tek tırnak) | String delimiter — kesintiye uğratır |
| `$` | Variable expansion |
| `` ` `` | Command substitution |

## Çözüm: Temp Dosya + Python Inline

Mesajı bir temp dosyaya yaz, sonra Python 3.14 ile o dosyayı okuyarak manuel gönder:

### Adım 1: Temp dosya oluştur

```bash
cat > /tmp/hermes_task.txt << 'HERMES_EOF'
**Görev:** Buraya uzun mesajın
Birden fazla satır
Özel karakterler ( ) * $ vs.
HERMES_EOF
```

### Adım 2: Python 3.14 ile VS Code'a gönder

```bash
"C:\Users\marko\AppData\Local\Python\PythonCore-3.14-64\python.exe" -c "
import pyautogui, subprocess, ctypes, time

# Dosyadan oku
with open(r'C:\Users\marko\AppData\Local\Temp\hermes_task.txt', 'r', encoding='utf-8') as f:
    text = f.read()

# VS Code focus
user32 = ctypes.windll.user32
found = []
@ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
def cb(hwnd, _):
    if user32.IsWindowVisible(hwnd):
        buf = ctypes.create_unicode_buffer(512)
        user32.GetWindowTextW(hwnd, buf, 512)
        if 'visual studio code' in buf.value.lower():
            found.append(hwnd)
    return True
user32.EnumWindows(cb, 0)

if found:
    user32.ShowWindow(found[0], 3)
    user32.SetForegroundWindow(found[0])
    time.sleep(1.0)

# Command Palette -> Claude Focus
pyautogui.hotkey('ctrl', 'shift', 'p')
time.sleep(0.7)
pyautogui.typewrite('Claude: Focus on Chat Input', interval=0.05)
time.sleep(0.5)
pyautogui.press('enter')
time.sleep(1.0)

# Clipboard + paste
subprocess.run('clip', input=text, text=True, encoding='utf-8', capture_output=True)
time.sleep(0.3)
pyautogui.hotkey('ctrl', 'a')
time.sleep(0.1)
pyautogui.hotkey('ctrl', 'v')
time.sleep(0.3)
pyautogui.press('enter')

print('Gonderildi')
" 2>&1
```

## Ne Zaman Kullanılır

- `vscode_yaz.bat` çalışmazsa (bash karakter hatası)
- Mesaj çok uzunsa (>1000 karakter)
- İçinde `(`, `)`, `*`, `$`, `` ` `` gibi özel karakterler varsa

## Not

- Python 3.14 yolu: `C:\Users\marko\AppData\Local\Python\PythonCore-3.14-64\python.exe`
- `pyautogui` ve `ctypes` Python 3.14'te yüklü (Hermes venv'ında değil)
- Temp dosya yolu: `C:\Users\marko\AppData\Local\Temp\hermes_task.txt`
