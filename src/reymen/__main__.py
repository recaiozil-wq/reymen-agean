"""``python -m reymen`` için giriÅŸ noktasÄ±."""

import sys
from pathlib import Path

# Proje kökünü PATH'e ekle (reymen_launcher.py'nin yanÄ±)
sys.path.insert(0, str(Path(__file__).parent.parent.parent.resolve()))
from reymen_launcher import main

if __name__ == "__main__":
    raise SystemExit(main())
