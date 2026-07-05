# -*- coding: utf-8 -*-
"""
araclar_makro.py â€” Makro kaydet/oynat (TinyTask mantÄ±ÄŸÄ±).
"Beni takip et" -> fare/klavye olaylarÄ±nÄ± zaman damgasÄ±yla kaydeder.
"Oynat" -> kaydÄ± aynÄ± sÄ±rayla tekrar eder.

KayÄ±tlar JSON olarak saklanÄ±r; her uygulama/proje iÃ§in ayrÄ± dosya.
BaÄŸÄ±mlÄ±lÄ±k: pynput (kayÄ±t iÃ§in), pyautogui (oynatma iÃ§in). Opsiyonel.

DÄ°KKAT: Bu KÃ–R tekrardÄ±r â€” aynÄ± koordinatlara aynÄ± sÄ±rayla tÄ±klar.
Pencere yeri/boyutu deÄŸiÅŸirse kayÄ±t bozulabilir. Ekran-OCR-TÄ±kla daha dayanÄ±klÄ±dÄ±r.
"""

import json
import os
import time
import logging

logger = logging.getLogger(__name__)

try:
    from pynput import mouse, keyboard

    PYNPUT_OK = True
except Exception:
    PYNPUT_OK = False

try:
    import pyautogui

    PYAUTOGUI_OK = True
except Exception:
    PYAUTOGUI_OK = False


class MakroKaydedici:
    def __init__(self, kayit_dizini=".ReYMeN/makrolar"):
        self.kayit_dizini = kayit_dizini
        os.makedirs(kayit_dizini, exist_ok=True)
        self._olaylar = []
        self._baslangic = None
        self._mouse_listener = None
        self._kb_listener = None

    def kaydi_baslat(self):
        """Fare/klavye dinleyicilerini baÅŸlatÄ±r."""
        if not PYNPUT_OK:
            return "[Makro]: pynput kurulu deÄŸil (pip install pynput)."
        self._olaylar = []
        self._baslangic = time.time()

        def on_click(x, y, button, pressed):
            if pressed:
                self._olaylar.append(
                    {
                        "t": time.time() - self._baslangic,
                        "tip": "click",
                        "x": x,
                        "y": y,
                        "buton": str(button),
                    }
                )

        def on_press(key):
            self._olaylar.append(
                {"t": time.time() - self._baslangic, "tip": "tus", "key": str(key)}
            )

        self._mouse_listener = mouse.Listener(on_click=on_click)
        self._kb_listener = keyboard.Listener(on_press=on_press)
        self._mouse_listener.start()
        self._kb_listener.start()
        return "[Makro]: KayÄ±t baÅŸladÄ±. 'kaydi_durdur(ad)' ile bitir."

    def kayda_basla(self):
        """kaydi_baslat() icin kisayol alias."""
        return self.kaydi_baslat()

    def kaydi_durdur(self, makro_adi):
        """Dinleyicileri durdurur ve kaydÄ± dosyaya yazar."""
        if self._mouse_listener:
            self._mouse_listener.stop()
        if self._kb_listener:
            self._kb_listener.stop()
        yol = os.path.join(self.kayit_dizini, f"{makro_adi}.json")
        with open(yol, "w", encoding="utf-8") as f:
            json.dump(self._olaylar, f, ensure_ascii=False, indent=2)
        return f"[Makro]: '{makro_adi}' kaydedildi ({len(self._olaylar)} olay) -> {yol}"

    def oynat(self, makro_adi, hiz=1.0):
        """KayÄ±tlÄ± makroyu aynÄ± zamanlamayla tekrar eder."""
        if not PYAUTOGUI_OK:
            return "[Makro]: pyautogui kurulu deÄŸil."
        yol = os.path.join(self.kayit_dizini, f"{makro_adi}.json")
        if not os.path.exists(yol):
            return f"[Makro]: '{makro_adi}' bulunamadÄ±."
        with open(yol, "r", encoding="utf-8") as f:
            olaylar = json.load(f)

        onceki_t = 0
        for olay in olaylar:
            bekle = (olay["t"] - onceki_t) / hiz
            if bekle > 0:
                time.sleep(min(bekle, 5))  # gÃ¼venlik: max 5sn bekleme
            onceki_t = olay["t"]
            if olay["tip"] == "click":
                pyautogui.click(olay["x"], olay["y"])
            elif olay["tip"] == "tus":
                tus = olay["key"].replace("'", "").replace("Key.", "")
                try:
                    pyautogui.press(tus)
                except Exception as _araclar__e97:
                    print(f"[UYARI] araclar_makro.py:98 - {_araclar__e97}")
        return f"[Makro]: '{makro_adi}' oynatÄ±ldÄ± ({len(olaylar)} olay)."

    def makro_listesi(self):
        dosyalar = [
            f[:-5] for f in os.listdir(self.kayit_dizini) if f.endswith(".json")
        ]
        return dosyalar


def motor_kaydet(motor):
    """Makro araÃ§larÄ±nÄ± motora kaydet."""
    if not hasattr(motor, "_plugin_arac_kaydet"):
        return
    _mk = MakroKaydedici()
    motor._plugin_arac_kaydet(
        "MAKRO_OYNAT_ADI",
        lambda ad="": _mk.oynat(str(ad)),
        "KayÄ±tlÄ± makroyu Ã§alÄ±ÅŸtÄ±r (ad: makro adÄ±)",
    )
    motor._plugin_arac_kaydet(
        "MAKRO_LISTESI",
        lambda: str(_mk.makro_listesi()),
        "KayÄ±tlÄ± makro listesini gÃ¶ster",
    )


if __name__ == "__main__":
    m = MakroKaydedici(kayit_dizini="/tmp/ReYMeN_makro")
    print("MakroKaydedici hazir (pynput:%s, pyautogui:%s)" % (PYNPUT_OK, PYAUTOGUI_OK))
    print("Kayitli makrolar:", m.makro_listesi())
