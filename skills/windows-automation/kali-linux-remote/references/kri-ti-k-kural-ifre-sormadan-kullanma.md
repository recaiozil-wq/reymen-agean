---
skill_id: 7e21e41a5286
usage_count: 1
last_used: 2026-06-16
---
## ⚠️ KRİTİK KURAL — Şifre Sormadan Kullanma

**Kali VM asla izinsiz kullanılmaz. Kullanıcıdan her SSH oturumunda şifre iste.**

Kural:
1. Kullanıcı açıkça "kali" veya "Kali'de şunu yap" demedikçe bu skill'i kullanma.
2. **SSH bağlantısından önce kullanıcıya Kali şifresini sor.** Cevabı bekle. Şifreyi geçmiş oturumdan veya hafızadan alma — her seferinde sor.
3. SSH bağlantısı kurma, ping atma, IP tarama yapma — hiçbiri şifresiz yapılmaz.
4. **HER ADIMDA ONAY GEREK:** Kullanıcı bir Kali işlemi için izin verse bile, her bir araç/komut öncesinde kullanıcıya sor. "nmap ile 192.168.1.1 taranacak, onaylıyor musun?" gibi. Kullanıcının klavyeden yanıtını bekle. Detaylı akış için `kali-pentest` skill'inin `references/per-step-approval-workflow.md` dosyasına bak.