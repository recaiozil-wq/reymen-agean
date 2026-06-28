---
skill_id: 61e9adc3d934
usage_count: 1
last_used: 2026-06-16
---
## Önemli Kod Desenleri

### SSH Bağlantı Kontrolü

```python
def is_connected():
    return (client is not None and
            client.get_transport() is not None and
            client.get_transport().is_active())
```

Her komut gönderme isteğinde ve status sorgusunda bu kontrol yapılmalı.

### Hata Yönetimi

```python
try:
    stdin, stdout, stderr = client.exec_command(cmd, timeout=15)
except paramiko.SSHException as e:
    return jsonify({"error": f"SSH hatasi: {str(e)}"}), 500
except socket.timeout:
    return jsonify({"error": "Komut zamani asimi (15sn)"}), 504
```

### Buton Disable/Enable Mantığı (JavaScript)

```javascript
function updateUI(connected) {
    document.querySelectorAll("button[data-cmd]").forEach(b => b.disabled = !connected);
    document.getElementById("cmd-input").disabled = !connected;
    document.getElementById("send-btn").disabled = !connected;
    // Status indicator
    const dot = document.getElementById("status-dot");
    dot.className = connected ? "status-green" : "status-red";
    document.getElementById("status-text").textContent =
        connected ? `Bağlı (${vm_ip})` : "Bağlı Değil";
}
```