
> **Kategori:** Windows

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Windows ajanı |
| **Ne?** | Windows Automation_Tam Sistem Yetkisi_References_Renk Arama Belirli Renk Nerede |
| **Nerede?** | Windows/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# Renk arama — belirli renk nerede?
found = pyautogui.locateOnScreen(r"C:\Users\marko\Downloads\hedef.png",
                                  confidence=0.9)
if found:
    pyautogui.click(found)
```

---