# -*- coding: utf-8 -*-
"""video_generation_tool.py — Video Uretme Araci.

AI video servislerine (RunwayML, HyperFrames) API cagrisi yapar.
"""

import os
from pathlib import Path


def video_uret(prompt: str, servis: str = "runway", sure: int = 5) -> str:
    """AI ile video uret.

    Args:
        prompt: Video aciklamasi
        servis: Video servisi (runway, hyperframes)
        sure: Video suresi (saniye)

    Returns:
        Video URL'si veya hata mesaji
    """
    if not prompt:
        return "[Video]: Prompt gerekli."

    if servis == "runway":
        api_key = os.environ.get("RUNWAYML_API_KEY", "")
        if not api_key:
            return "[Video]: RUNWAYML_API_KEY ayarlanmamis."
        try:
            import requests
            r = requests.post(
                "https://api.runwayml.com/v1/generate",
                json={"prompt": prompt, "duration": sure},
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=120,
            )
            if r.status_code == 200:
                return f"[Video]: {r.json().get('url', 'Uretildi')}"
            return f"[Video]: Hata {r.status_code}"
        except ImportError:
            return "[Video]: requests kutuphanesi yok."
        except Exception as e:
            return f"[Video]: Hata: {e}"

    elif servis == "hyperframes":
        # HyperFrames local
        try:
            import subprocess
            import sys
            hf_script = Path(__file__).parent.parent / "tools" / "hyperframes.py"
            if not hf_script.exists():
                return "[Video]: hyperframes.py bulunamadi."
            r = subprocess.run(
                [sys.executable, str(hf_script), "--prompt", prompt],
                capture_output=True, text=True, timeout=120,
            )
            return r.stdout.strip() or "[Video]: HyperFrames tamam."
        except subprocess.TimeoutExpired:
            return "[Video]: Zaman asimi."
        except Exception as e:
            return f"[Video]: Hata: {e}"

    return f"[Video]: Bilinmeyen servis: {servis}"


if __name__ == "__main__":
    print(video_uret("bir kedi videosu"))
