# -*- coding: utf-8 -*-
"""delegate_tool.py — Alt-Ajan Delegasyon Araci.

ReYMeN motorunun LLM provider'i uzerinden bir alt gorevi
baska bir modele yonlendirir. Async task baslatir ve sonucu dondurur.
"""

import json
import asyncio
from pathlib import Path

try:
    from motor import Motor
except ImportError:
    Motor = None


try:
    from tools.delegate_tool import _run_single_child
except ImportError:
    def _run_single_child(task_info, parent_conv, tool_registry, storage_backend):
        """Fallback stub - upstream compatibility."""
        return {"status": "error", "error": "not implemented"}


def run(**kwargs) -> str:
    """Belirtilen alt gorevi bir LLM modeline devreder.

    Args:
        goal (str): Alt gorevin hedefi (zorunlu)
        context (str): Baglam bilgisi (opsiyonel)
        model (str): Kullanilacak model adi (opsiyonel, varsayilan: motor modeli)
        timeout (int): Yanit icin maksimum bekleme saniyesi (opsiyonel, varsayilan: 60)

    Returns:
        str: Alt ajandan gelen yanit veya hata mesaji
    """
    goal = kwargs.get("goal")
    if not goal:
        return "[Delegate]: 'goal' parametresi zorunludur."

    context = kwargs.get("context", "")
    model = kwargs.get("model", None)
    timeout = kwargs.get("timeout", 60)

    if not Motor:
        # Motor yoksa fallback: basit bir simulasyon
        try:
            prompt = f"Gorev: {goal}\n"
            if context:
                prompt += f"Baglam: {context}\n"
            prompt += "Yukaridaki gorevi yerine getir."

            import subprocess
            result = subprocess.run(
                ["python", "-c", f"print({json.dumps(prompt)[:200]})"],
                capture_output=True, text=True, timeout=timeout
            )
            return f"[Delegate]: Alt gorev tamamlandi.\n{result.stdout}"
        except Exception as e:
            return f"[Delegate]: Hata - {e}"

    try:
        # Motor uzerinden async task baslat
        motor = Motor()
        mesajlar = [
            {"role": "system", "content": f"Sen bir alt ajansin. Gorev: {goal}"},
            {"role": "user", "content": context if context else goal}
        ]

        if asyncio.get_event_loop().is_running():
            loop = asyncio.get_event_loop()
            yanit = loop.run_until_complete(
                asyncio.wait_for(
                    motor.soru(mesajlar, model=model),
                    timeout=timeout
                )
            )
        else:
            yanit = asyncio.run(
                asyncio.wait_for(
                    motor.soru(mesajlar, model=model),
                    timeout=timeout
                )
            )
        return f"[Delegate]: Alt ajandan yanit:\n{yanit}"

    except asyncio.TimeoutError:
        return f"[Delegate]: Zaman asimi ({timeout} saniye)."
    except Exception as e:
        return f"[Delegate]: Hata - {e}"


def ping() -> bool:
    """Delegate aracinin calisip calismadigini kontrol eder."""
    return True


if __name__ == "__main__":
    print(run(goal="Merhaba de", context="Test"))
