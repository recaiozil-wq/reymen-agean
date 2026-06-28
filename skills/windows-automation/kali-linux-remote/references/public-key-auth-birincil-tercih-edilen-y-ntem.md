---
skill_id: 1d718d087c3e
usage_count: 1
last_used: 2026-06-16
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