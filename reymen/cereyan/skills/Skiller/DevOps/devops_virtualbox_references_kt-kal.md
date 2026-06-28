
> **Kategori:** DevOps

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Devops_Virtualbox_References_Kt Kal |
| **Nerede?** | DevOps/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# Çıktı: kal
```

**Önemli notlar:**

- `MSYS2_ARG_CONV_EXCL="*"` **ZORUNLUDUR** — Git Bash (MSYS) yoksa `/usr/bin/qterminal` yolunu `C:/Program Files/Git/usr/bin/qterminal`'e çevirir ve hata alırsın. Bu ortam değişkeni tüm yol dönüşümünü devre dışı bırakır.
- `run` ile `--wait-stdout` kullanılır (çıktıyı yakalamak için)
- `start` ile `--wait-stdout` yoktur (GUI için)
- Guest session başarıyla açılır (`Successfully started guest session`) ama binary bulunamazsa hata alırsın
- Kali'de bilinen terminal emülatörleri: `qterminal` (öncelikli), `x-terminal-emulator`
- `xfce4-terminal`, `xterm`, `gnome-terminal` Kali'de olmayabilir
- `run` ile çıktı almak için komutun **non-interactive** olması gerekir
- Guest session için VM'in çalışıyor olması yeterli — login ekranında olması sorun değil

**Örnek 3 — Guest Control ile uygulama başlatma akışı:**

```python