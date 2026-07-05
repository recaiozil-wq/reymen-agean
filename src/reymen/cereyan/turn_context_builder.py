# -*- coding: utf-8 -*-
"""Turn context builder — mesaj listesi insa + context kontrol.

ReYMeN'e ozgu, Hermes bagimliligi YOK.
conversation_loop_v2.py'den extract edilmistir:
- _api_mesajlari_olustur()
- _context_preflight()
"""
from __future__ import annotations

import logging
from typing import Any, Optional

logger = logging.getLogger("conversation_loop")


def mesajlari_olustur(
    sistem_prompt: str,
    hedef: str,
    gecmis_mesajlar: Optional[list[dict]] = None,
    ek_baglam: Optional[dict] = None,
    tool_schema: Optional[list] = None,
) -> list[dict]:
    """API'ye gonderilecek mesaj listesini olustur.

    Args:
        sistem_prompt: Sistem prompt metni.
        hedef: Kullanici hedefi.
        gecmis_mesajlar: Onceki konusma gecmisi.
        ek_baglam: Ek baglam dicti (varsa yoruma eklenir).
        tool_schema: Tool schema listesi (varsa).

    Returns:
        OpenAI-uyumlu mesaj listesi.
    """
    mesajlar: list[dict] = [{"role": "system", "content": sistem_prompt}]

    if gecmis_mesajlar:
        mesajlar.extend(gecmis_mesajlar)

    # Ek baglam varsa user mesajina ekle
    kullanici_mesaji = hedef
    if ek_baglam:
        baglam_metni = _baglam_to_string(ek_baglam)
        if baglam_metni:
            kullanici_mesaji = f"{hedef}\n\n[Baglam]\n{baglam_metni}"

    mesajlar.append({"role": "user", "content": kullanici_mesaji})

    return mesajlar


def _baglam_to_string(baglam: dict) -> str:
    """Baglam dict'ini metne cevir."""
    parcalar = []
    for anahtar, deger in baglam.items():
        if isinstance(deger, str):
            parcalar.append(f"{anahtar}: {deger[:200]}")
        elif isinstance(deger, (int, float, bool)):
            parcalar.append(f"{anahtar}: {deger}")
    return "\n".join(parcalar)


def context_preflight(
    mesajlar: list,
    sistem_prompt: str,
    provider_tipi: Optional[str] = None,
    *,
    provider_limits: Optional[dict[str, int]] = None,
    provider_limit_varsayilan: int = 128000,
    context_sikistirma_esigi: float = 0.50,
    compressor=None,
    hook_sikistirma_tetikle=None,
) -> list:
    """Context doluluk oranini kontrol et, asimi varsa sikistir.

    Args:
        mesajlar: Mevcut mesaj listesi.
        sistem_prompt: Sistem prompt metni.
        provider_tipi: Provider tipi (limit icin).
        provider_limits: Provider -> limit dict.
        provider_limit_varsayilan: Varsayilan token limiti.
        context_sikistirma_esigi: Sikistirma baslangic orani (0.0-1.0).
        compressor: ContextCompressor instance (opsiyonel).
        hook_sikistirma_tetikle: Hook callback (opsiyonel).

    Returns:
        Guncellenmis mesaj listesi.
    """
    if not mesajlar:
        return mesajlar

    limits = provider_limits or {}
    limit_token = provider_limit_varsayilan
    if provider_tipi:
        for anahtar, limit in limits.items():
            if anahtar in provider_tipi.lower():
                limit_token = limit
                break

    toplam_char = sum(len(m.get("content", "") or "") for m in mesajlar)
    toplam_char += len(sistem_prompt)
    limit_char = limit_token * 4
    oran = toplam_char / limit_char if limit_char else 0

    if oran < context_sikistirma_esigi:
        return mesajlar

    logger.info(
        "Context doluluk: %.0f%% (limit=%dK token, provider=%s) — sikistirma",
        oran * 100, limit_token // 1000, provider_tipi or "varsayilan",
    )

    if hook_sikistirma_tetikle is not None:
        try:
            hook_sikistirma_tetikle(
                mesaj_sayisi=len(mesajlar),
                token_tahmini=int(toplam_char / 4),
            )
        except Exception:
            pass

    if compressor is not None:
        try:
            return compressor.sikistir(mesajlar, max_token=limit_token)
        except Exception as e:
            logger.warning("Compressor hatasi: %s", e)

    if oran >= 0.85:
        koru = max(3, len(mesajlar) // 2)
        ozet = f"[Context sikistirildi — {len(mesajlar)} -> {koru} mesaj, doluluk: %{oran*100:.0f}]"
        return [mesajlar[0]] + [{"role": "user", "content": ozet}] + mesajlar[-koru:]
    elif oran >= 0.65:
        ozet = f"[Context sikistirildi - {len(mesajlar)} mesaj, doluluk: %{oran*100:.0f}]"
        return (
            mesajlar[:1]
            + [{"role": "user", "content": ozet}]
            + mesajlar[-(len(mesajlar) // 2):]
        )
    else:
        return mesajlar


def api_mesajlari_olustur(
    sistem_prompt: str,
    gecmis: list,
    provider_tipi: str,
) -> list[dict]:
    """Provider tipine gore API mesaj listesi olustur.

    - anthropic: sistem ayri, kullanici mesajlari listede
    - codex: responses API format
    - default: chat_completions (OpenAI, LM Studio, DeepSeek)
    """
    if provider_tipi == "anthropic":
        mesajlar = [{"role": "system", "content": sistem_prompt}]
        for m in gecmis:
            rol = m.get("role", "user")
            if rol == "system":
                continue
            mesajlar.append({"role": rol, "content": m.get("content", "")})
        return mesajlar

    if provider_tipi == "codex":
        mesajlar = [{"role": "system", "content": sistem_prompt}]
        for m in gecmis:
            rol = m.get("role", "user")
            if rol == "system":
                continue
            mesajlar.append({
                "role": "user" if rol not in ("assistant", "tool") else rol,
                "content": m.get("content", ""),
            })
        return mesajlar

    # Default: chat_completions
    mesajlar = [{"role": "system", "content": sistem_prompt}]
    for m in gecmis:
        rol = m.get("role", "user")
        if rol == "system":
            continue
        mesaj = {"role": rol, "content": m.get("content", "")}
        if m.get("tool_calls"):
            mesaj["tool_calls"] = m["tool_calls"]
        if m.get("tool_call_id"):
            mesaj["tool_call_id"] = m["tool_call_id"]
        mesajlar.append(mesaj)
    return mesajlar
