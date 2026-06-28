---
skill_id: b5af830a8a07
usage_count: 1
last_used: 2026-06-16
---
## KULLANICI KURALLARI (DEGISTIRILEMEZ)

1. **ONCE EKRANA BAK**: Her VM komutundan once `screenshotpng` al, `vision_analyze` ile kontrol et. Terminal aciksa direkt yaz, login ekraniysa sifre gir, VM kapaliysa baslat.

2. **SSH ARKADA, VBoxManage ONCE**: Karmasik islemleri SSH ile arka planda calistir, sonuclari `keyboardputstring` ile VM terminaline yaz. SSH sadece data almak icin.

3. **help ile COZUM ARA**: VM'de bir komut calismazsa veya sonuc beklendigi gibi degilse, once Kali'de `--help`, `man`, veya `help` dene. Disaridan arastirma yapmadan once VM icinde cozum ara.

4. **TURKCE Q KLAVYE HATASI**: `keyboardputstring` ile `kali` yazarken dikkat — TURKCE 'i' (ı) degil, INGILIZCE 'i' (i) kullan. `kali` = k-a-l-i (4 ASCII karakter). `kalı` = k-a-l-ı (Turkce 'ı', isaretsiz). Yanlis yazarsan login ekraninda kalirsin.
   - Cozum: `keyboardputstring` ile sadece ASCII karakterleri kullan. Ozel Turkce karakterlerden kacin.