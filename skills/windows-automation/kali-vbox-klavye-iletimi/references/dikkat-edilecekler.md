---
skill_id: 94e311f4d5ae
usage_count: 1
last_used: 2026-06-16
---
## Dikkat Edilecekler

1. **Yonlendirme (`>` , `|`) sorunu**: `>` , `|` gibi ozel karakterler `keyboardputstring` ile gonderildiginde VM terminalinde dogru calismayabilir. Karmasik komutlar icin once SSH ile calistir, sonucu `echo` ile VM'e yazdir.

2. **Bekleme suresi**: Her komuttan sonra `sleep N` ile yeterli sure ver. ozellikle `nmap`, `arp-scan` gibi uzun sureli komutlarda 3-5 saniye beklenmeli.

3. **Enter ayri gonderilmeli**: `keyboardputstring` sadece metin gonderir, Enter tusu ayrica `$'\n'` ile gonderilmelidir.

4. **Dosyaya yonlendirme calismaz**: `komut > /tmp/cikti.txt` gibi yonlendirmeler `keyboardputstring` ile calismaz. Bunun yerine SSH ile calistir, sonra `echo` ile VM'e ozeti yazdir.