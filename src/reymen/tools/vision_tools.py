"""ReYMeN tools.vision_tools shim â€” ReYMeN vision fonksiyonlarÄ±nÄ± ReYMeN'e yÃ¶nlendirir."""

from __future__ import annotations

import json
import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)


def vision_analyze_tool(
    image_url: str,
    question: Optional[str] = None,
    **kwargs,
) -> str:
    """ReYMeN vision_analyze_tool â€” ReYMeN vision engine'e yÃ¶nlendirir.

    GÃ¶rsel analizi iÃ§in LLM'in vision yeteneÄŸini kullanÄ±r.
    """
    try:
        from reymen.arac.araclar_goruntu import gorsel_analiz

        result = gorsel_analiz(image_url, question or "")
        return json.dumps({"success": True, "analysis": result})
    except ImportError:
        # Fallback: dosyayÄ± oku ve dÃ¶ndÃ¼r
        try:
            if image_url.startswith(("http://", "https://")):
                import urllib.request
                import tempfile

                with urllib.request.urlopen(image_url, timeout=10) as resp:
                    data = resp.read()
                return json.dumps(
                    {
                        "success": True,
                        "image_size": len(data),
                        "note": "Vision analysis not available (araclar_goruntu not found)",
                    }
                )
        except Exception as _e:
            logger.warning("[VisionTools] except Exception (L37): %s", Exception)
            pass
        return json.dumps(
            {
                "success": False,
                "error": f"Vision analysis unavailable: {image_url}",
            }
        )
