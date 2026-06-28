
> **Kategori:** Windows

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Windows ajanı |
| **Ne?** | Windows Automation_Tam Sistem Yetkisi_References_1 Telegram Bot Token Env Ve Config Yaml Yazma |
| **Nerede?** | Windows/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

## 1. Telegram Bot Token — .env ve config.yaml Yazma

### .env dosyasına token kaydet

```python
import re
from pathlib import Path

def set_env_value(env_path: str, key: str, value: str) -> None:
    p = Path(env_path)
    text = p.read_text(encoding="utf-8") if p.exists() else ""
    pattern = re.compile(rf"^{re.escape(key)}\s*=.*", re.MULTILINE)
    new_line = f"{key}={value}"
    if pattern.search(text):
        text = pattern.sub(new_line, text)
    else:
        text = text.rstrip("\n") + f"\n{new_line}\n"
    p.write_text(text, encoding="utf-8")
    print(f"[OK] {key} yazildi -> {p}")