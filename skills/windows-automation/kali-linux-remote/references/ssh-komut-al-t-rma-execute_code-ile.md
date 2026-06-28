---
skill_id: 6fd1708e6d1d
usage_count: 1
last_used: 2026-06-16
---
## SSH Komut Çalıştırma (execute_code ile)

**Basit komutlar** için `terminal` aracı yeterli:
```python
sshpass_path = r"C:\Users\marko\AppData\Local\Microsoft\WinGet\Packages\xhcoding.sshpass-win32_Microsoft.Winget.Source_8wekyb3d8bbwe\sshpass.exe"

cmd = [
    sshpass_path, "-p", "1234",
    "ssh", "-o", "StrictHostKeyChecking=no",
    "-o", "ConnectTimeout=10",
    f"kali@192.168.0.19",
    "komut_buraya"
]

result = subprocess.run(cmd, capture_output=True, text=True, timeout=30,
    env={**os.environ, "SSHPASS": "1234"})
print(result.stdout)
```