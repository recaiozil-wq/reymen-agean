
> **Kategori:** DevOps

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Devops_Virtualbox_References_Right Separate Calls With Sleep |
| **Nerede?** | DevOps/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# RIGHT — separate calls with sleep
  "$VBOX" controlvm "$VM" keyboardputstring "echo '1'"
  "$VBOX" controlvm "$VM" keyboardputstring $'\n'
  sleep 1
  "$VBOX" controlvm "$VM" keyboardputstring "echo '2'"
  "$VBOX" controlvm "$VM" keyboardputstring $'\n'
  ```\n- **Tmux send-keys space stripping via git-bash**: When sending commands to a Kali tmux session via `ssh ... 'tmux send-keys -t hermes \"command\" Enter'`, git-bash (MSYS) or zsh may strip spaces from within quoted strings, turning `\"echo hello\"` into `echohello`. This happens because the ssh wrapper / shell serialization mangles the quoting.\n  - **Best fix**: Use `sshpass -p 'pass' ssh kali@host 'command'` directly — one command per SSH call, bypasses tmux entirely. Works reliably.\n  - **Alternative**: Use `VBoxManage keyboardputstring` for VM-console typing (no quoting issues, but no output capture).\n  - **Tmux with heredoc**: Use `ssh -tt kali@host <<'EOF' ... EOF` and inside the heredoc use `tmux send-keys -t hermes -l \"literal text\" C-m` with the `-l` literal flag.\n- **GRUB müdahale için keyboardputstring zamanlaması**: Kali boot'ta GRUB'a müdahale etmek için VBoxManage kontrol komutları kullanılır. Zamanlama kritiktir:
  1. `VBoxManage controlvm <vm> reset` — VM'i resetle
  2. Hemen (0.5 sn aralıkla) 5-8 kere `keyboardputstring "e"` gönder — GRUB menüsünde "edit" moduna girer
  3. 3 sn bekle, sonra `keyboardputscancode 50 d0` (aşağı ok) ile linux satırına git (gerekirse 2-3 kere)
  4. `keyboardputstring " systemd.unit=multi-user.target"` ile boot parametresi ekle (networking servisi takılmasın)
  5. `keyboardputscancode 1d` (Ctrl basılı), `keyboardputstring "x"`, `keyboardputscancode 9d` (Ctrl bırak) ile boot et
  - **Not:** GRUB timeout varsayılan 5 sn. İlk "e" tuşu bu süre içinde gönderilmezse GRUB otomatik boot eder ve müdahale şansı kaybedilir.
  - **Alternatif:** Her zamanlama tutmayabilir. Başarısız olursa tekrar dene.
  - **GUI mod:** `--type gui` ile başlatıp browser_vision ile GRUB ekranını görmek daha güvenilir.

### 5. Direct keyboard input to VM terminal (keyboardputstring)

Send keystrokes directly into the VM's own terminal (not SSH — this types into the VirtualBox console window). Useful for:
- Typing commands into the VM's physical terminal when SSH is unavailable or the user wants to see keys being typed
- Bypassing SSH for educational/demo purposes
- Automating boot-time GRUB edits (see GRUB section above)

**Basic usage:**
```bash
VBOX="C:\Program Files\Oracle\VirtualBox\VBoxManage.exe"
VM="kal"