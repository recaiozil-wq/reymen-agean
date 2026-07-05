# -*- coding: utf-8 -*-
"""Tool execution — sequential and concurrent dispatch.

Hermes agent/tool_executor.py + ReYMeN _arac_calistir birlesimi.
ReYMeN'e ozgu: Rules Engine, MCP tools, internal tools, motor.
"""
from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger("conversation_loop")


def execute_tool(
    eylem: dict,
    *,
    # ReYMeN baglamlari
    motor=None,
    web_ara_fn=None,
    once_hafiza_fn=None,
    oncelik_cache=None,
    mcp_catalog_run=None,
    mcp_client_listele=None,
    mcp_client_baglan=None,
    mcp_catalog_aktif=False,
    mcp_client_aktif=False,
    once_hafiza_aktif=False,
    rules_engine=None,
    rules_aktif=False,
    hata_cozumle_fn=None,
) -> dict:
    """Bir araci calistir ve sonucu dondur.

    Args:
        eylem: {"arac": str, "parametreler": dict}
        motor: Motor instance (opsiyonel)
        web_ara_fn: _web_ara fonksiyonu
        once_hafiza_fn: hafizada_ara fonksiyonu
        oncelik_cache: ONCELIK_CACHE dict
        mcp_catalog_run: MCP catalog run fonksiyonu
        mcp_client_listele: MCP client listele fonksiyonu
        mcp_client_baglan: MCP client baglan fonksiyonu
        mcp_catalog_aktif: MCP catalog aktif mi
        mcp_client_aktif: MCP client aktif mi
        once_hafiza_aktif: OnceHafiza aktif mi
        rules_engine: RulesEngine instance
        rules_aktif: Rules Engine aktif mi
        hata_cozumle_fn: Hata cozumleme fonksiyonu

    Returns:
        {"basarili": bool, "cikti": str, "tamamlandi": bool, "hata": str}
    """
    arac = eylem.get("arac", "")
    parametreler = eylem.get("parametreler", {})
    if isinstance(parametreler, str):
        try:
            parametreler = json.loads(parametreler)
        except Exception:
            parametreler = {}

    # ── Rules Engine kontrolu ────────────────────────────────────────
    if rules_aktif and rules_engine is not None:
        try:
            kategori = _tool_kategori_bul(arac)
            hedef_str = arac
            if parametreler:
                try:
                    param_str = json.dumps(parametreler, ensure_ascii=False)
                    hedef_str = f"{arac} {param_str[:200]}"
                except Exception:
                    hedef_str = f"{arac} {str(parametreler)[:200]}"

            kural_sonuc = rules_engine.kontrol(kategori, hedef_str)
            if not kural_sonuc.get("izin"):
                logger.warning("[Rules] ENGEL: %s (%s) — %s", arac, kategori, kural_sonuc.get("sebep", ""))
                return {
                    "basarili": False,
                    "cikti": f"[ENGELLENDI] {kural_sonuc.get('sebep', 'Kural ihlali')}",
                    "tamamlandi": False,
                    "hata": f"Kural engeli: {kural_sonuc.get('sebep', '')}",
                    "kural": kural_sonuc,
                }
        except Exception as _re:
            logger.debug("[Rules] Kontrol hatasi: %s", _re)

    # ── Internal tools ──────────────────────────────────────────────
    # File safety + guardrails
    try:
        from reymen.guvenlik.file_safety import guvenli_mi
        if not guvenli_mi(arac, parametreler):
            return {"basarili": False, "cikti": "[GUVENLIK] Engellendi: " + arac, "tamamlandi": False}
    except Exception:
        pass

    if arac == "web_ara":
        sorgu = parametreler.get("sorgu") or parametreler.get("param", "")
        if web_ara_fn:
            sonuc = web_ara_fn(sorgu)
        else:
            sonuc = None
        return {"basarili": bool(sonuc), "cikti": sonuc or "Sonuc bulunamadi", "tamamlandi": True}

    if arac == "once_hafiza_ara":
        sorgu = parametreler.get("sorgu") or parametreler.get("param", "")
        if once_hafiza_aktif and once_hafiza_fn:
            sonuc = once_hafiza_fn(sorgu)
            return {"basarili": bool(sonuc), "cikti": str(sonuc or "Bulunamadi"), "tamamlandi": bool(sonuc)}
        return {"basarili": False, "cikti": "Hafiza aktif degil", "tamamlandi": False}

    if arac == "oncelik_cache_kontrol":
        anahtar = parametreler.get("anahtar") or parametreler.get("param", "")
        hedef_kucuk = anahtar.strip().lower()
        if oncelik_cache:
            for k, v in oncelik_cache.items():
                if k in hedef_kucuk:
                    return {"basarili": True, "cikti": v, "tamamlandi": True}
        return {"basarili": False, "cikti": "Cache'te yok", "tamamlandi": False}

    # ── MCP Tools ──────────────────────────────────────────────────
    if arac in ("MCP_CATALOG", "mcp_catalog"):
        if mcp_catalog_aktif and mcp_catalog_run:
            islem = parametreler.get("islem", "listele")
            sunucu_adi = parametreler.get("sunucu_adi", "")
            sonuc = mcp_catalog_run(islem=islem, sunucu_adi=sunucu_adi)
            return {"basarili": True, "cikti": str(sonuc), "tamamlandi": False}
        return {"basarili": False, "cikti": "MCP Catalog aktif degil", "tamamlandi": False}

    if arac in ("MCP_CLIENT", "mcp_client"):
        if mcp_client_aktif:
            islem = parametreler.get("islem", "listele")
            if islem == "listele" and mcp_client_listele:
                sonuc = mcp_client_listele()
                return {"basarili": True, "cikti": str(sonuc), "tamamlandi": False}
            elif islem == "baglan" and mcp_client_baglan:
                sunucu = parametreler.get("sunucu", "")
                if sunucu:
                    sonuc = mcp_client_baglan(sunucu)
                    return {"basarili": True, "cikti": str(sonuc), "tamamlandi": False}
                return {"basarili": False, "cikti": "MCP_CLIENT: 'sunucu' parametresi gerekli", "tamamlandi": False}
            return {"basarili": False, "cikti": f"MCP_CLIENT: bilinmeyen islem '{islem}'", "tamamlandi": False}
        return {"basarili": False, "cikti": "MCP Client aktif degil", "tamamlandi": False}

    # ── Motor ───────────────────────────────────────────────────────
    if motor and hasattr(motor, "arac_calistir"):
        try:
            return motor.arac_calistir(arac, **parametreler)
        except Exception as e:
            if hata_cozumle_fn:
                hata_cozumle_fn(f"Tool hatasi ({arac}): {e}", kaynak="tool")
            return {"basarili": False, "hata": str(e)}

    # ── Direkt tool modulu ──────────────────────────────────────────
    try:
        mod_ad = f"tools.{arac.lower()}"
        mod = __import__(mod_ad, fromlist=["run"])
        if hasattr(mod, "run"):
            sonuc = mod.run(**parametreler)
            return {"basarili": True, "cikti": str(sonuc), "tamamlandi": False}
    except ImportError:
        return {"basarili": False, "hata": f"Arac bulunamadi: {arac}"}
    except Exception as e:
        return {"basarili": False, "hata": str(e)}

    return {"basarili": False, "hata": "Motor kullanilamiyor"}


def _tool_kategori_bul(arac: str) -> str:
    """Arac adina gore kategori belirle."""
    arac_lower = arac.lower()
    if any(k in arac_lower for k in ["oku", "yaz", "sil", "dosya", "file", "read", "write", "path"]):
        return "dosya_erisim"
    if any(k in arac_lower for k in ["web", "http", "api", "curl", "get", "post", "fetch", "download"]):
        return "ag"
    if any(k in arac_lower for k in ["terminal", "bash", "sh", "cmd", "komut", "run", "exec", "shell"]):
        return "komut"
    if any(k in arac_lower for k in ["llm", "beyin", "model", "provider", "ai"]):
        return "api_cagrisi"
    return "komut"


def execute_tool_calls_sequential(
    tool_calls: List[dict],
    messages: List[dict],
    *,
    motor=None,
    web_ara_fn=None,
    once_hafiza_fn=None,
    oncelik_cache=None,
    mcp_catalog_run=None,
    mcp_client_listele=None,
    mcp_client_baglan=None,
    mcp_catalog_aktif=False,
    mcp_client_aktif=False,
    once_hafiza_aktif=False,
    rules_engine=None,
    rules_aktif=False,
    hata_cozumle_fn=None,
) -> List[dict]:
    """Tool call'lari sirali olarak calistir ve sonuclari topla.

    Args:
        tool_calls: [{"name": str, "arguments": dict}, ...]
        messages: Mevcut mesaj listesi (tool sonuclari eklenir)
        Diger parametreler: execute_tool ile ayni

    Returns:
        Tool sonuclari ile guncellenmis messages
    """
    for tc in tool_calls:
        arac = tc.get("name", "")
        args = tc.get("arguments", {})
        if isinstance(args, str):
            try:
                args = json.loads(args)
            except Exception:
                args = {}

        eylem = {"arac": arac, "parametreler": args}
        sonuc = execute_tool(
            eylem,
            motor=motor,
            web_ara_fn=web_ara_fn,
            once_hafiza_fn=once_hafiza_fn,
            oncelik_cache=oncelik_cache,
            mcp_catalog_run=mcp_catalog_run,
            mcp_client_listele=mcp_client_listele,
            mcp_client_baglan=mcp_client_baglan,
            mcp_catalog_aktif=mcp_catalog_aktif,
            mcp_client_aktif=mcp_client_aktif,
            once_hafiza_aktif=once_hafiza_aktif,
            rules_engine=rules_engine,
            rules_aktif=rules_aktif,
            hata_cozumle_fn=hata_cozumle_fn,
        )

        messages.append({
            "role": "tool",
            "content": json.dumps(sonuc, ensure_ascii=False),
            "name": arac,
        })

    return messages
