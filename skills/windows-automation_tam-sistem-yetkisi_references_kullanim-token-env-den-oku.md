
> **Kategori:** Windows

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Windows ajanı |
| **Ne?** | Windows Automation_Tam Sistem Yetkisi_References_Kullanim Token Env Den Oku |
| **Nerede?** | Windows/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# Kullanim — token .env'den oku:
import os
from dotenv import load_dotenv
load_dotenv(r"C:\Users\marko\AppData\Local\hermes\.env")
test_telegram_bot(os.getenv("TELEGRAM_BOT_TOKEN", ""))
```

---