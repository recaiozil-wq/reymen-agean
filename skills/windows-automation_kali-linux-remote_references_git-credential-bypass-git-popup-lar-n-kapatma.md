
> **Kategori:** Windows

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Kali ajanı |
| **Ne?** | Windows Automation_Kali Linux Remote_References_Git Credential Bypass Git Popup Lar N Kapatma |
| **Nerede?** | Windows/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

## Git Credential Bypass (Git Popup'larını Kapatma)

Windows'ta Git işlemleri sırasında açılan **Git Credential Manager popup'larını** tamamen devre dışı bırakmak için:

### Ortam Değişkenleri (~/.bashrc)

```bash
export GIT_ASKPASS=echo
export SSH_ASKPASS=echo
export DISPLAY=
export GIT_TERMINAL_PROMPT=0