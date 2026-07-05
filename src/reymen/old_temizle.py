"""old_temizle.py â€” 7 gÃ¼nden eski .old dosyalarÄ±nÄ± temizle."""

import os, time, shutil
from pathlib import Path

PROJE = Path(__file__).parent.parent
SINIR_GUN = 7
simdi = time.time()
silinen = 0
toplam_boyut = 0

for f in sorted(PROJE.rglob("*.old")):
    yas = (simdi - f.stat().st_mtime) / 86400
    if yas > SINIR_GUN:
        boyut = f.stat().st_size
        f.unlink()
        silinen += 1
        toplam_boyut += boyut
        print(f"  ğŸ—‘ï¸ {f.relative_to(PROJE)} ({boyut//1024}KB, {yas:.0f} gÃ¼n)")

if silinen == 0:
    print(f"âœ… 7 gÃ¼nden eski .old dosyasÄ± yok (hepsi taze)")
else:
    print(f"\nâœ… {silinen} dosya silindi, ~{toplam_boyut//1024//1024}MB kurtarÄ±ldÄ±")
