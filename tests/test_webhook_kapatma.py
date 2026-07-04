"""Kapatma: webhook.py"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from reymen.sistem.webhook import kaydet, calistir

print(
    "OK webhook: import basarili (kaydet=%s, calistir=%s)"
    % (callable(kaydet), callable(calistir))
)
