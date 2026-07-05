"""``python -m reymen`` iÃ§in giriÅŸ noktasÄ±."""

import sys
from pathlib import Path

# Proje kÃ¶kÃ¼nÃ¼ PATH'e ekle (reymen_launcher.py'nin yanÄ±)
sys.path.insert(0, str(Path(__file__).parent.parent.parent.resolve()))
from reymen_launcher import main

if __name__ == "__main__":
    raise SystemExit(main())
