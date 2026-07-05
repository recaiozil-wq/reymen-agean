# -*- coding: utf-8 -*-
"""
subagent_runner.py â€” Alt-ajan Ã§alÄ±ÅŸtÄ±rÄ±cÄ±.
DelegationManager tarafÄ±ndan subprocess olarak Ã§aÄŸrÄ±lÄ±r.
Stdin'den JSON {goal, context} alÄ±r, stdout'a JSON {status, result} yazar.
"""

import json
import sys
import time
import traceback
import logging

logger = logging.getLogger(__name__)


def run(goal: str, context: str = "") -> dict:
    """
    Verilen goal/context ile alt-ajan gÃ¶revini Ã§alÄ±ÅŸtÄ±r.
    Basit bir LLM benzeri yanÄ±t Ã¼retir â€” gerÃ§ek ortamda bu bir AI Ã§aÄŸrÄ±sÄ± olur.
    """
    try:
        # GÃ¶revi iÅŸle
        baslik = goal.strip()
        if not baslik:
            return {"status": "error", "result": "BoÅŸ hedef gÃ¶nderildi"}

        lines = baslik.split("\n")
        adim_sayisi = len([l for l in lines if l.strip()])

        sonuc_parts = [
            f"[SubAgent] GÃ¶rev tamamlandÄ±: {baslik[:120]}",
            f"  BaÄŸlam: {context[:200] if context else '(yok)'}",
            f"  Ä°ÅŸlenen adÄ±m sayÄ±sÄ±: {adim_sayisi or 1}",
        ]

        # GÃ¶rev tÃ¼rÃ¼ne gÃ¶re basit bir Ã§Ä±ktÄ± oluÅŸtur
        goal_lower = baslik.lower()
        if "ara" in goal_lower or "search" in goal_lower or "bul" in goal_lower:
            sonuc_parts.append(
                f"  [Arama] '{baslik[:60]}' iÃ§in varsayÄ±lan arama yapÄ±ldÄ± (simÃ¼lasyon)"
            )
            sonuc_parts.append("  Durum: Veri bulundu â€” Ã¶rnek iÃ§erik Ã¼retildi")
        elif "yaz" in goal_lower or "write" in goal_lower or "oluÅŸtur" in goal_lower:
            sonuc_parts.append(
                f"  [Yazma] '{baslik[:60]}' iÃ§in iÃ§erik oluÅŸturuldu (simÃ¼lasyon)"
            )
            sonuc_parts.append("  Durum: Ä°Ã§erik hazÄ±r")
        elif "test" in goal_lower or "kontrol" in goal_lower or "check" in goal_lower:
            sonuc_parts.append(
                f"  [Kontrol] '{baslik[:60]}' iÃ§in test Ã§alÄ±ÅŸtÄ±rÄ±ldÄ± (simÃ¼lasyon)"
            )
            sonuc_parts.append("  Durum: Test baÅŸarÄ±lÄ±")
        elif "dÃ¼zelt" in goal_lower or "fix" in goal_lower or "dÃ¼zenle" in goal_lower:
            sonuc_parts.append(
                f"  [DÃ¼zeltme] '{baslik[:60]}' iÃ§in dÃ¼zenleme yapÄ±ldÄ± (simÃ¼lasyon)"
            )
            sonuc_parts.append("  Durum: DÃ¼zeltme uygulandÄ±")
        elif "analiz" in goal_lower or "analyze" in goal_lower or "rapor" in goal_lower:
            sonuc_parts.append(f"  [Analiz] '{baslik[:60]}' analiz edildi (simÃ¼lasyon)")
            sonuc_parts.append("  Durum: Analiz tamamlandÄ± â€” 3 bulgu tespit edildi")
        else:
            sonuc_parts.append(f"  [Genel] '{baslik[:60]}' iÅŸlendi (simÃ¼lasyon)")
            sonuc_parts.append("  Durum: VarsayÄ±lan iÅŸlem tamam")

        return {
            "status": "success",
            "result": "\n".join(sonuc_parts),
            "goal": goal,
            "context": context,
        }

    except Exception as e:
        return {
            "status": "error",
            "result": f"Hata: {type(e).__name__}: {e}\n{traceback.format_exc()}",
            "goal": goal,
            "context": context,
        }


def main():
    """Stdin'den JSON oku, iÅŸle, stdout'a JSON yaz."""
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            # HiÃ§ girdi yoksa hata dÃ¶ndÃ¼r
            print(
                json.dumps(
                    {
                        "status": "error",
                        "result": "Stdin boÅŸ â€” JSON giriÅŸi bekleniyordu",
                    }
                )
            )
            sys.exit(1)

        girdi = json.loads(raw)
        goal = girdi.get("goal", "")
        context = girdi.get("context", "")

        sonuc = run(goal, context)
        print(json.dumps(sonuc, ensure_ascii=False))

    except json.JSONDecodeError as e:
        print(
            json.dumps(
                {
                    "status": "error",
                    "result": f"JSON ayrÄ±ÅŸtÄ±rma hatasÄ±: {e}",
                }
            )
        )
        sys.exit(1)
    except Exception as e:
        print(
            json.dumps(
                {
                    "status": "error",
                    "result": f"Beklenmeyen hata: {type(e).__name__}: {e}",
                }
            )
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
