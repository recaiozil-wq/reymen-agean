
> **Kategori:** Windows

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Kali ajanı |
| **Ne?** | Windows Automation_Kali Linux Remote_References_Kri Ti K Kural Ifre Sormadan Kullanma |
| **Nerede?** | Windows/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

## ⚠️ KRİTİK KURAL — Şifre Sormadan Kullanma

**Kali VM asla izinsiz kullanılmaz. Kullanıcıdan her SSH oturumunda şifre iste.**

Kural:
1. Kullanıcı açıkça "kali" veya "Kali'de şunu yap" demedikçe bu skill'i kullanma.
2. **SSH bağlantısından önce kullanıcıya Kali şifresini sor.** Cevabı bekle. Şifreyi geçmiş oturumdan veya hafızadan alma — her seferinde sor.
3. SSH bağlantısı kurma, ping atma, IP tarama yapma — hiçbiri şifresiz yapılmaz.
4. **HER ADIMDA ONAY GEREK:** Kullanıcı bir Kali işlemi için izin verse bile, her bir araç/komut öncesinde kullanıcıya sor. "nmap ile 192.168.1.1 taranacak, onaylıyor musun?" gibi. Kullanıcının klavyeden yanıtını bekle. Detaylı akış için `kali-pentest` skill'inin `references/per-step-approval-workflow.md` dosyasına bak.