
> **Kategori:** Verimlilik

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Windows ajanı |
| **Ne?** | Productivity_Windows Shortcut Testing_References_Manual Key Method |
| **Nerede?** | Verimlilik/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# Manuel Tuş Yöntemi — İşine Yarar Örnekler

## Temel Bloklar

```python
from pyautogui import keyDown, press, keyUp

# Tek tuşa bas (Win + X)
keyDown('winleft')
press('x')
keyUp('winleft')

# İki tuş kombinasyonu (Win + E)
keyDown('winleft')
press('e')
keyUp('winleft')

# Üçlü kombinasyon (Win + Ctrl + Sol)
keyDown('winleft')
keyDown('ctrl')
press('left')
keyUp('ctrl')
keyUp('winleft')
```

## Tek Kullanımlı Yardımcı

```python
def press_win_combo(win_key='winleft', combo_keys=None):
    if combo_keys is None:
        combo_keys = []
    keyDown(win_key)
    for k in combo_keys:
        press(k)
    keyUp(win_key)
```

## Kullanım Haritası

| İstenen Kısayol | Kod |
|-----------------|-----|
| Win + S | `press_win_combo('winleft', ['s'])` |
| Win + V | `press_win_combo('winleft', ['v'])` |
| Win + I | `press_win_combo('winleft', ['i'])` |
| Win + D | `press_win_combo('winleft', ['d'])` |
| Win + Tab | `press_win_combo('winleft', ['tab'])` |
| Win + Ctrl + Sol | `press_win_combo('winleft', ['ctrl', 'left'])` |
| Win + Ctrl + Sağ | `press_win_combo('winleft', ['ctrl', 'right'])` |
| Win + Shift + S | `press_win_combo('winleft', ['shift', 's'])` |
| Win + Shift + V | `press_win_combo('winleft', ['shift', 'v'])` |
| Win + L | `press_win_combo('winleft', ['l'])` |
| Win + H | `press_win_combo('winleft', ['h'])` |
| Win + E (Dosya Gezgini) | `press_win_combo('winleft', ['e'])` |
| Win + Home | `press_win_combo('winleft', ['home'])` |
| Win + W | `press_win_combo('winleft', ['w'])` |
| Win + , | `press_win_combo('winleft', [','])` |
| Win + . | `press_win_combo('winleft', ['.'])` |
| Win + Pause | `press_win_combo('winleft', ['pause'])` |
| Win + Prtsc | `press_win_combo('winleft', ['printscreen'])` |
| Win + Alt + Tab | `keyDown('winleft'); keyDown('alt'); press('tab'); keyUp('alt'); keyUp('winleft')` |

## Yaygın Hatalar ve Önlemler

- `press()` karakterlerin tam adını kullan: `left`, `right`, `up`, `down`, `tab`, `enter`, `space`, `shift`, `ctrl`, `alt`
- Basit harf/rakam için direkt `press('a')` yeterli; kendisi keyDown/keyUp yapar
- Kombo içinde birden fazla modifiye tuş varsa, bireysel `keyDown/keyUp` tercih et
- İşlem arasında 0.3–0.6 saniye bekle; çok kısa bekleme sistem kısayolunu kaydetmez
- Win tuşunu her zaman en son bırak; yanlış sırayla `keyUp` kilitlenmeye neden olabilir
