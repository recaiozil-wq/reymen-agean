"""reymen_exe.py — Minimal exe wrapper for ReYMeN launcher.
Sadece subprocess ile reymen_launcher.py'yi calistirir."""

import os
import shutil
import subprocess
import sys
from pathlib import Path

# Proje kokunu bul
_exe = Path(sys.executable).resolve()
for _p in [_exe.parent, _exe.parent.parent, _exe.parent.parent.parent]:
    _launcher = _p / "reymen_launcher.py"
    if _launcher.exists():
        os.chdir(str(_p))
        sys.exit(subprocess.call([sys.executable, str(_launcher)] + sys.argv[1:]))

# Bulamadiysa PATH'te ara
_launcher = shutil.which("reymen_launcher.py")
if _launcher:
    sys.exit(subprocess.call([sys.executable, _launcher] + sys.argv[1:]))

print("reymen_launcher.py bulunamadi!")
sys.exit(1)
