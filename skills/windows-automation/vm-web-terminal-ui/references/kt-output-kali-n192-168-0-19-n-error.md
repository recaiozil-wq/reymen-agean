---
skill_id: 2ce03b0ec11b
usage_count: 1
last_used: 2026-06-16
---
# Çıktı: {"output": "kali\n192.168.0.19\n", "error": ""}
```

**Kritik:** Kali'de default shell **zsh**. Çok satırlı komutlar ve tırnak içinde `$()` kullanımı hata verir. Komutları tek satırda `&&` ile birleştir, tek tırnak kullan:

```