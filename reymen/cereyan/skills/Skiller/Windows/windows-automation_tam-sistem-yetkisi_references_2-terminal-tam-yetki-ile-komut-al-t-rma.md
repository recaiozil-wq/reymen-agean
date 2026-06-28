
> **Kategori:** Windows

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Windows ajanı |
| **Ne?** | Windows Automation_Tam Sistem Yetkisi_References_2 Terminal Tam Yetki Ile Komut Al T Rma |
| **Nerede?** | Windows/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

## 2. Terminal — Tam Yetki ile Komut Çalıştırma

```python
import subprocess

def run_cmd(command: str, cwd: str = None) -> tuple[int, str, str]:
    result = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True,
        cwd=cwd,
        encoding="utf-8",
        errors="replace",
    )
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print("[STDERR]", result.stderr)
    return result.returncode, result.stdout, result.stderr