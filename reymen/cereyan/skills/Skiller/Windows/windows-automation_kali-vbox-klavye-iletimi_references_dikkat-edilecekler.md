
> **Kategori:** Windows

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Kali ajanı |
| **Ne?** | Windows Automation_Kali Vbox Klavye Iletimi_References_Dikkat Edilecekler |
| **Nerede?** | Windows/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

## Dikkat Edilecekler

1. **Yonlendirme (`>` , `|`) sorunu**: `>` , `|` gibi ozel karakterler `keyboardputstring` ile gonderildiginde VM terminalinde dogru calismayabilir. Karmasik komutlar icin once SSH ile calistir, sonucu `echo` ile VM'e yazdir.

2. **Bekleme suresi**: Her komuttan sonra `sleep N` ile yeterli sure ver. ozellikle `nmap`, `arp-scan` gibi uzun sureli komutlarda 3-5 saniye beklenmeli.

3. **Enter ayri gonderilmeli**: `keyboardputstring` sadece metin gonderir, Enter tusu ayrica `$'\n'` ile gonderilmelidir.

4. **Dosyaya yonlendirme calismaz**: `komut > /tmp/cikti.txt` gibi yonlendirmeler `keyboardputstring` ile calismaz. Bunun yerine SSH ile calistir, sonra `echo` ile VM'e ozeti yazdir.