
> **Kategori:** DevOps

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Devops_Virtualbox_References_Wait For Nmap To Finish Adjust Based On Subnet Size |
| **Nerede?** | DevOps/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# Wait for nmap to finish (adjust based on subnet size)
sleep 6
```

**Pitfalls:**
- **Bash/zsh quoting on Windows git-bash**: `$'\\n'` syntax works in git-bash (MSYS) but NOT in PowerShell or cmd.exe. If running elevated, use cmd.exe with a different quoting strategy (echo newline or use `keyboardputscancode 1c 9c` for Enter).
- **Race conditions — EN ÖNEMLİ SORUN**: If you type too fast without adequate `sleep`, the next command gets typed into the previous command's output area or prompt line — effectively creating a malformed command or writing to a non-shell context. Required sleep durations:
  - Simple `echo` commands: 1-2 sn
  - `arp-scan`, `iwlist` gibi kısa taramalar: 3-5 sn
  - `nmap -sn` gibi subnet taramaları: 6-10 sn
  - Ping sweep loop: 15-60 sn (254 IP)
  - `apt-get install`, `systemctl restart`: 10-20 sn
- **Long compound commands fail**: Multi-part shell commands (% `echo '...' && echo '...' && echo '...'`) chained into a single `keyboardputstring` call often fail because the VirtualBox keyboard buffer cannot handle the full string. Instead, split into separate calls with sleep between each:
  ```
  "$VBOX" controlvm "kal" keyboardputstring "echo Baslik 1"
  "$VBOX" controlvm "kal" keyboardputstring $'\\n'
  sleep 1
  "$VBOX" controlvm "kal" keyboardputstring "echo Baslik 2"
  "$VBOX" controlvm "kal" keyboardputstring $'\\n'
  ```
- **No visual confirmation**: The user must confirm the output appeared on-screen. They use it for demonstration/education purposes; if something goes wrong, they'll tell you to retry.
- **Cannot type interactive passwords**: `sudo` without NOPASSWD will prompt for a password on-screen. Configure NOPASSWD in `/etc/sudoers` first if you need to run sudo commands via keyboardputstring.
- **Shell operators do NOT work**: `>`, `|`, `$()`, backticks, `&&` (sometimes), and other shell metacharacters are sent as literal text, not interpreted. Use SSH for redirected/pipe'd commands.
- **No output capture**: `keyboardputstring` is a one-way operation — you type keys but cannot read the VM screen. For verifiable execution or when the user needs proof, use SSH instead.

### 6. Guest Control — VBoxManage guestcontrol (ÖNCELİKLİ)

`VBoxManage guestcontrol`, VM'in içinde doğrudan komut/program çalıştırmanı sağlar.
**keyboardputstring'ten ÖNCE tercih edilir** çünkü:
- Çıktıyı yakalayabilirsin (`--wait-stdout` ile)
- Zamanlama sorunu yok (sleep gerekmez)
- Login ekranındayken bile çalışır (oturum açar)
- Git Bash yol dönüşümü için `MSYS2_ARG_CONV_EXCL="*"` kullan

**İki alt komut:**

| Komut | Kullanım | Çıktı |
|-------|----------|-------|
| `run` | Çalıştır + çıktıyı bekle | `--wait-stdout` ile yakalanabilir |
| `start` | GUI uygulaması başlat (arka planda) | Çıktı yok, sadece başlat |

**Örnek 1 — Kali'de terminal aç (EN SIK KULLANIM):**

Kali'de terminal açmak için `keyboardputstring` + Ctrl+Alt+T yerine guestcontrol kullan — çok daha güvenilir:

```bash