# conftest.py — ReYMeN test yapilandirmasi
import sys
from pathlib import Path

# Proje kokunu ve src/ dizinini sys.path'e ekle
PROJE_KOK = Path(__file__).parent.resolve()
SRC_DIR = PROJE_KOK / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
if str(PROJE_KOK) not in sys.path:
    sys.path.insert(0, str(PROJE_KOK))
