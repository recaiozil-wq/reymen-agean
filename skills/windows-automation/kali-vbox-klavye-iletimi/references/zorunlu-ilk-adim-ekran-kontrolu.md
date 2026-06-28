---
skill_id: abe31390ccec
usage_count: 1
last_used: 2026-06-16
---
## ZORUNLU ILK ADIM — Ekran Kontrolu

Kali VM'e komut gondermeden ONCE:

1. **Ekran goruntusu al**:
   ```bash
   "C:\\Program Files/Oracle/VirtualBox/VBoxManage.exe" controlvm "kal" screenshotpng "C:\\Users\\marko\\Desktop\\kali_desktop.png"
   ```

2. **vision_analyze ile kontrol et**: Masaustu acik mi? Terminal penceresi gorunuyor mu?
   - Eger **login ekrani** gorunuyorsa → kullanici adi `kali` ve sifre `1234` ile gir
   - Eger **masaustu** aciksa (taskbar, ikonlar, terminal penceresi) → dogrudan komut yaz
   - VM kapaliysa → once `startvm` ile baslat

3. **Eger terminal aciksa** (imlec bekliyor) → `keyboardputstring` ile dogrudan komut yaz, `$'\n'` ile Enter gonder

4. **SSH gereksiz**: Masaustu acikken terminale yazmak icin SSH'e gerek yok. `keyboardputstring` yeterli.