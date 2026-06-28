
> **Kategori:** Windows

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Windows ajanı |
| **Ne?** | Windows Automation_Vm Web Terminal Ui_References_Html Template With Dark Terminal Theme |
| **Nerede?** | Windows/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# HTML template with dark terminal theme
    return render_template_string("""...""")

@app.route("/status")
def status():
    connected = client is not None and client.get_transport() is not None and client.get_transport().is_active()
    return jsonify({"connected": connected})

@app.route("/exec", methods=["POST"])
def exec_cmd():
    cmd = request.json.get("cmd", "")
    if not client or not client.get_transport().is_active():
        return jsonify({"error": "SSH baglantisi yok"}), 503
    stdin, stdout, stderr = client.exec_command(cmd, timeout=15)
    out = stdout.read().decode("utf-8", errors="replace")
    err = stderr.read().decode("utf-8", errors="replace")
    return jsonify({"output": out, "error": err})

if __name__ == "__main__":
    ssh_connect()
    app.run(host="127.0.0.1", port=5050, debug=False)
```

### 3. HTML Template — Dark Terminal Tema

Arayüz içermelidir:
- **Başlık:** "Kali Terminal" veya VM adı
- **Status göstergesi:** Yeşil/daire (bağlı) veya kırmızı/kare (bağlı değil)
- **Durum yazısı:** "Bağlı" / "Bağlı Değil" + IP adresi
- **Hızlı komut butonları:** whoami/ip, disk alanı, RAM, process, uptime, arp-scan, OS info, tmux son
- **Komut giriş kutusu:** Text input + "Gönder" butonu
- **Çıktı alanı:** `<pre>` etiketi, dark arkaplan, yeşil font

Butonlar bağlı değilken disabled olmalı, bağlanınca aktifleşmeli.

Örnek buton-komut eşleşmeleri:
```javascript
const PRESET_COMMANDS = {
    "whoami/ip": "whoami && hostname -I",
    "disk": "df -h /",
    "ram": "free -h",
    "process": "ps aux --sort=-%mem | head -15",
    "uptime": "uptime && last -15",
    "arp-scan": "sudo arp-scan -l 2>&1",
    "OS info": "uname -a && cat /etc/os-release | head -5",
    "tmux son": "tmux capture-pane -t hermes -p -S -50"
};
```

CSS renk paleti:
- Arkaplan: `#1a1a2e` veya `#0d0d0d`
- Metin: `#00ff00` (terminal yeşili) veya `#e0e0e0`
- Butonlar: `#16213e` arkaplan, `#0f3460` hover
- Status yeşil: `#00ff88`, status kırmızı: `#ff4444`
- Font: `'Courier New', monospace`

### 4. Masaüstü Kısayolu (.bat)

Dosya: `C:\Users\marko\Desktop\kali-terminal-ui.bat`

```batch
@echo off
title Kali Terminal UI
echo Kali Terminal UI baslatiliyor...
cd /d C:\Users\marko\Desktop
start http://localhost:5050
python kali-terminal-ui.py
pause
```

Bu `.bat` dosyası:
1. Flask sunucusunu başlatır
2. Varsayılan tarayıcıda `http://localhost:5050` açar
3. Kullanıcı tarayıcıyı kullandıktan sonra Ctrl+C ile durdurur

### 5. Test Adımları

1. VM'in çalıştığını doğrula:
   ```bash
   VBoxManage list runningvms
   ```

2. SSH ile bağlanabildiğini doğrula:
   ```bash
   sshpass -p 'kali' ssh -o ConnectTimeout=5 kali@192.168.0.19 "whoami"
   ```

3. Flask sunucusunu başlat:
   ```bash
   cd /c/Users/marko/Desktop && python kali-terminal-ui.py
   ```

4. Tarayıcıda `http://localhost:5050` aç

5. Status endpoint'ini kontrol et:
   ```bash
   curl http://localhost:5050/status