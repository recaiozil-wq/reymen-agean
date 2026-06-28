
> **Kategori:** Windows

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Windows ajanı |
| **Ne?** | Windows Automation_Tam Sistem Yetkisi_References_Ornekler |
| **Nerede?** | Windows/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# Ornekler:
run_cmd("ipconfig")
run_cmd("pip list", cwd=r"C:\Users\marko\hermes-ai")
run_cmd(r".\venv\Scripts\activate && python hermes.py --version",
        cwd=r"C:\Users\marko\hermes-ai")
```

### PowerShell komutu çalıştır

```python
import subprocess

def run_ps(script: str) -> str:
    result = subprocess.run(
        ["powershell", "-NoProfile", "-NonInteractive", "-Command", script],
        capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    return result.stdout + result.stderr