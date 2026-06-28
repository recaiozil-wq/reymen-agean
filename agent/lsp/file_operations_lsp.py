# -*- coding: utf-8 -*-
"""file_operations_lsp.py — LSP diagnostik kontrollü dosya yazma modülü.

ReYMeN'te ``tools/file_operations.py`` içinde yapılan işlemin ReYMeN
karşılığıdır. Şu pattern'i uygular:

    1. Yazma öncesi: ``snapshot_baseline()`` → mevcut diagnostikleri kaydet
    2. Yazma işlemi: asıl dosyaya yaz
    3. Yazma sonrası: ``get_diagnostics_sync()`` → yeni diagnostikleri al
    4. Delta: baseline'da olmayan diagnostikleri döndür

Kullanıcıya dönen mesaja eklenir, yazma işlemini engellemez.
LSP servisi kapalı/broken ise sessizce atlanır (graceful degrade).
"""

from __future__ import annotations

import logging
import os
from typing import Any, Dict, List, Optional

logger = logging.getLogger("reymen.lsp.file_operations")


def lsp_diagnostics_before_write(file_path: str) -> None:
    """Yazma öncesi LSP baseline snapshot'ı alır.

    Best-effort: LSP kapalı/broken ise sessizce döner.
    """
    try:
        from agent.lsp import get_service

        svc = get_service()
        if svc is not None and svc.is_active():
            svc.snapshot_baseline(file_path)
    except Exception as e:
        logger.debug("LSP baseline snapshot atlanamadi (%s): %s", file_path, e)


def lsp_diagnostics_after_write(
    file_path: str,
    pre_text: Optional[str] = None,
    post_text: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Yazma sonrası LSP diagnostiklerini alır, baseline delta'ya göre filtreler.

    Args:
        file_path: Yazılan dosyanın yolu.
        pre_text: Varsa, satır kayması hesaplamak için eski içerik.
        post_text: Varsa, satır kayması hesaplamak için yeni içerik.

    Returns:
        Yeni (baseline'da olmayan) diagnostik listesi.
    """
    try:
        from agent.lsp import get_service
        from agent.lsp.range_shift import build_line_shift

        svc = get_service()
        if svc is None or not svc.is_active():
            return []

        line_shift = None
        if pre_text is not None and post_text is not None:
            line_shift = build_line_shift(pre_text, post_text)

        diags = svc.get_diagnostics_sync(
            file_path,
            delta=True,
            line_shift=line_shift,
        )
        return diags
    except Exception as e:
        logger.debug("LSP diagnostics alinamadi (%s): %s", file_path, e)
        return []


def lsp_write_with_check(
    path: str,
    content: str,
    encoding: str = "utf-8",
) -> Dict[str, Any]:
    """Dosyayı yazar ve LSP diagnostiklerini kontrol eder.

    Args:
        path: Dosya yolu.
        content: Yazılacak içerik.
        encoding: Dosya encoding'i (varsayılan: utf-8).

    Returns:
        ``{"yazildi": True, "karakter": N, "diagnostik": [...]}``
    """
    pre_text: Optional[str] = None
    # Yazma öncesi eski içeriği oku (delta hesaplama için)
    if os.path.exists(path):
        try:
            with open(path, "r", encoding=encoding) as f:
                pre_text = f.read()
        except Exception:
            pre_text = None

    # Baseline snapshot
    lsp_diagnostics_before_write(path)

    # Dosyayı yaz
    with open(path, "w", encoding=encoding) as f:
        f.write(content)

    # Diagnostik kontrol
    diags = lsp_diagnostics_after_write(path, pre_text=pre_text, post_text=content)

    return {
        "yazildi": True,
        "karakter": len(content),
        "diagnostik": format_diagnostics(diags),
    }


def format_diagnostics(diags: List[Dict[str, Any]]) -> str:
    """Diagnostik listesini okunabilir metne çevirir.

    Örnek çıktı::

        [LSP] 2 diagnostik:
        agent/lsp/client.py:42:23  hata  'foo' is not defined
        agent/lsp/client.py:87:5   uyari  Unused variable 'bar'
    """
    if not diags:
        return ""

    seviye_etiket = {1: "hata", 2: "uyari", 3: "bilgi", 4: "ipucu"}
    lines: list[str] = []
    for d in diags:
        pos = d.get("range", {}).get("start", {})
        satir = pos.get("line", 0) + 1  # LSP 0-index, kullanici 1-index
        sutun = pos.get("character", 0) + 1
        sev = d.get("severity", 1)
        etiket = seviye_etiket.get(sev, f"seviye{sev}")
        msg = d.get("message", "bilinmeyen diagnostik")
        source = d.get("source", "")
        kod = d.get("code", "")
        kod_str = f" [{source}/{kod}]" if source and kod else f" [{source}]" if source else ""
        lines.append(f"  {satir}:{sutun}  {etiket}{kod_str}  {msg}")

    if not lines:
        return ""

    return f"[LSP] {len(diags)} diagnostik:\n" + "\n".join(lines)
