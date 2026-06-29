
> **Kategori:** Windows

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Kali ajanı |
| **Ne?** | Windows Automation_Vm Web Terminal Ui_References_Kt Output Kali N192 168 0 19 N Error |
| **Nerede?** | Windows/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# Çıktı: {"output": "kali\n192.168.0.19\n", "error": ""}
```

**Kritik:** Kali'de default shell **zsh**. Çok satırlı komutlar ve tırnak içinde `$()` kullanımı hata verir. Komutları tek satırda `&&` ile birleştir, tek tırnak kullan:

```