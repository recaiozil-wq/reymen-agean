
> **Kategori:** Windows

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Kali ajanı |
| **Ne?** | Windows Automation_Kali Linux Remote_References_Public Key Auth Birincil Tercih Edilen Y Ntem |
| **Nerede?** | Windows/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

## Public Key Auth (Birincil, Tercih Edilen Yöntem)

Kali'ye public key auth kuruluysa, şifresiz bağlantı:

```bash
ssh kali "whoami && hostname"
```

SSH config (`~/.ssh/config`):
```
Host kali
    HostName 192.168.0.19
    User kali
    IdentityFile ~/.ssh/id_ed25519
    StrictHostKeyChecking no
```

**NOT:** Windows'ta git-bash SSH, Windows OpenSSH'ten farklıdır.
- git-bash SSH (`/usr/bin/ssh`): `ssh kali "<komut>"` çalışır
- Windows OpenSSH (`C:\Windows\System32\OpenSSH\ssh.exe`): `sshpass` ile kullanılır

sshpass **sadece** Windows OpenSSH ile çalışır, git-bash SSH ile çalışmaz.
Tam sshpass yolu:
```
C:\Users\marko\AppData\Local\Microsoft\WinGet\Packages\xhcoding.sshpass-win32_Microsoft.Winget.Source_8wekyb3d8bbwe\sshpass.exe
```