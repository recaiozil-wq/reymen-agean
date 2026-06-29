
> **Kategori:** Windows

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Kali ajanı |
| **Ne?** | Windows Automation_Kali Linux Remote_References_Ssh Varsay Lan Olarak Sshpass Kullans N Windows Openssh |
| **Nerede?** | Windows/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# SSH varsayılan olarak sshpass kullansın (Windows OpenSSH)
alias ssh='sshpass -p 1234 /c/Windows/System32/OpenSSH/ssh.exe'
alias scp='sshpass -p 1234 /c/Windows/System32/OpenSSH/scp.exe'
```

### Windows Sistem Değişkenleri (Kalıcı)

```bash
setx GIT_TERMINAL_PROMPT 0
setx GIT_ASKPASS echo
```

### Git Global Config

```bash
git config --global credential.helper ""
git config --global credential.modalprompt false
```

Bu ayarlarla:
- `ssh kali "<komut>"` → otomatik sshpass + şifre 1234 (bashrc alias)
- **Git credential manager ASLA açılmaz**
- `scp` de aynı şekilde sshpass ile çalışır

### Kali SSH Şifresi

Kali VM için SSH şifresi: `1234` (sudo şifresi ile aynı).
sshpass ile kullanılır: `sshpass -p 'kali' /c/Windows/System32/OpenSSH/ssh.exe ...`

### Reference Dosyaları

Detaylı yapılandırma için: `references/bashrc-setup.md`
Otomatik şifre doldurma scripti: `scripts/ssh_auto_pass.py`
Ağ tanı kontrol listesi: `references/session-diagnostics-checklist.md`
kali-pentest entegrasyonu: `references/kali-pentest-entegrasyonu.md`
Bridged tanısı: `references/bridge-tanisi.md`
Hermes SSH backend kilitlehmesi ve recovery: `references/hermes-ssh-backend-kilitlenmesi.md`
VM adı tutarsızlığı tanısı: `references/vm-adi-tutarsizligi-tanisi.md`