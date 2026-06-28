---
skill_id: 6e8857d5c22f
usage_count: 1
last_used: 2026-06-16
---
## Kurulum Adımları

### 1. Bağımlılıkları kur

```bash
pip install flask paramiko
```

Flask ve paramiko'nun yüklü olduğunu doğrula:
```bash
python -c "import flask; import paramiko; print('OK')"
```

### 2. Ana Flask uygulamasını yaz

Dosya: `C:\Users\marko\Desktop\kali-terminal-ui.py`

**Temel yapı:**
```python
from flask import Flask, render_template_string, jsonify, request
import paramiko

app = Flask(__name__)
KALI_HOST = "192.168.0.19"    # VM'nin IP'si (bridged)
KALI_PORT = 22
KALI_USER = "kali"
KALI_PASS = "1234"
client = None

def ssh_connect():
    global client
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(KALI_HOST, port=KALI_PORT, username=KALI_USER,
                       password=KALI_PASS, timeout=5)
        return True
    except Exception as e:
        client = None
        return False

@app.route("/")
def index():