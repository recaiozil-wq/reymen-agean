# -*- coding: utf-8 -*-
"""
langgraph_export.py â€” ReYMeN Konusma DÃ¶ngÃ¼sÃ¼ â†’ LangGraph StateGraph Export ModÃ¼lÃ¼.

conversation_loop.py'deki run_conversation() akÄ±ÅŸÄ±nÄ± analiz edip:
- LangGraph StateGraph JSON formatÄ±nda dÃ¼ÄŸÃ¼m/kenar/koÅŸul Ã§Ä±ktÄ±sÄ±
- Mermaid.js flowchart (```mermaid bloku)
- CLI Ã¼zerinden reymen --langgraph-export ile graph.json + graph.md

AkÄ±ÅŸ adÄ±mlarÄ± (run_conversation iÃ§indeki sÄ±ra):
  1. BASLA     â†’ task_id + session + budget + sistem_prompt oluÅŸtur
  2. HAFIZA_KONTROL â†’ OnceHafiza'da ara, session context injection
  3. WEB_ARA   â†’ web arama (gerekirse)
  4. SKILL_ARA â†’ skill tarama (FTS5) + ref_processor
  5. LLM_CAGIR â†’ API Ã§aÄŸrÄ±sÄ± (retry + fallback ile)
  6. TOOL_CALISTIR â†’ tool_calls varsa Ã§alÄ±ÅŸtÄ±r, sonuÃ§larÄ± ekle, loop
  7. YANIT_VER â†’ text response al, onayla
  8. BITIS     â†’ OnceHafiza'ya kaydet, session kapat, log

KoÅŸullar (conditional edges):
  - hafiza_var_mi:  Bellekte eÅŸleÅŸme var mÄ±?
  - web_gerekli_mi: Web arama gerekli mi?
  - skill_var_mi:   Skill eÅŸleÅŸmesi var mÄ±?
  - tool_gerekli_mi:LLM tool_calls dÃ¶ndÃ¼rdÃ¼ mÃ¼?
  - hata_var_mi:    Hata oluÅŸtu mu?
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


# â”€â”€ Sabitler â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

AKIS_ADIMLARI = [
    "basla",
    "hafiza_kontrol",
    "web_ara",
    "skill_ara",
    "llm_cagir",
    "tool_calistir",
    "yanit_ver",
    "bitis",
]

KOSULLAR = [
    "hafiza_var_mi",
    "web_gerekli_mi",
    "skill_var_mi",
    "tool_gerekli_mi",
    "hata_var_mi",
]

# Her dÃ¼ÄŸÃ¼mÃ¼n conversation_loop.py'deki karÅŸÄ±lÄ±k gelen kod bÃ¶lgesi
DUGUM_ACIKLAMA: Dict[str, str] = {
    "basla": (
        "Task ID oluÅŸtur, session baÅŸlat, budget (IterationBudget) kur, "
        "sistem prompt'u inÅŸa et (PromptBuilder + SOUL.md + durum.json)."
    ),
    "hafiza_kontrol": (
        "OnceHafiza'da arama (hafizada_ara), session context injection, "
        "Ã¶nceki konuÅŸma geÃ§miÅŸini yÃ¼kle, Ã¶nbellek (ONCELIK_CACHE) kontrolÃ¼."
    ),
    "web_ara": (
        "Web arama motoru (SearchDispatcher / DDGS) ile gÃ¼ncel bilgi topla, "
        "halÃ¼sinasyon Ã¶nleme iÃ§in gerÃ§ek veri ekle."
    ),
    "skill_ara": (
        "Skill tarama (FTS5 full-text search), konuÅŸmadan skill Ã§Ä±karma "
        "(konusmadan_skill_cikar), @file/@url referans iÅŸleme (ref_processor)."
    ),
    "llm_cagir": (
        "API Ã§aÄŸrÄ±sÄ± (direct_api_call): retry + fallback provider rotasyonu, "
        "streaming, circuit breaker, hata sÄ±nÄ±flandÄ±rma."
    ),
    "tool_calistir": (
        "LLM'den gelen tool_calls'larÄ± motor Ã¼zerinden Ã§alÄ±ÅŸtÄ±r "
        "(motor_tools_schema_al + _arac_calistir), sonuÃ§larÄ± messages'a ekle, "
        "tekrar LLM'e dÃ¶n (ReAct loop)."
    ),
    "yanit_ver": (
        "LLM'den text response al, doÄŸrulama (kÄ±sa yanÄ±t kontrolÃ¼), "
        "kullanÄ±cÄ±ya dÃ¶ndÃ¼r."
    ),
    "bitis": (
        "OnceHafiza'ya kaydet (ogrenme), session kapat, A2A broadcast, "
        "hook'larÄ± tetikle (tur_bitir, oturum_bitir), loglama."
    ),
}

KOSUL_ACIKLAMA: Dict[str, str] = {
    "hafiza_var_mi": "OnceHafiza'da eÅŸleÅŸen kayÄ±t var mÄ±? Varsa Ã¶n belleÄŸe al, yoksa normal akÄ±ÅŸ.",
    "web_gerekli_mi": "KullanÄ±cÄ± sorusu gÃ¼ncel bilgi/web aramasÄ± gerektiriyor mu?",
    "skill_var_mi": "FTS5 taramasÄ±nda eÅŸleÅŸen skill bulundu mu? Varsa context'e ekle.",
    "tool_gerekli_mi": "LLM tool_calls dÃ¶ndÃ¼rdÃ¼ mÃ¼? True â†’ araÃ§larÄ± Ã§alÄ±ÅŸtÄ±r, False â†’ yanÄ±t ver.",
    "hata_var_mi": "API veya araÃ§ Ã§aÄŸrÄ±sÄ±nda hata oluÅŸtu mu? True â†’ hata yÃ¶netimi.",
}


# â”€â”€ Graph TanÄ±mÄ± â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


def _graph_json_insa() -> dict:
    """LangGraph StateGraph formatÄ±nda JSON graph yapÄ±sÄ± oluÅŸtur.

    DÃ¼ÄŸÃ¼mler (nodes): her akÄ±ÅŸ adÄ±mÄ±
    Kenarlar (edges): sabit yÃ¶nlendirmeler
    KoÅŸullar (conditions): dallanma noktalarÄ±

    Returns:
        LangGraph StateGraph JSON dict.
    """
    nodes: List[Dict[str, Any]] = []
    for adim in AKIS_ADIMLARI:
        nodes.append(
            {
                "id": adim,
                "type": "node",
                "label": adim.replace("_", " ").title(),
                "description": DUGUM_ACIKLAMA.get(adim, ""),
                "entry": adim == "basla",
                "exit": adim == "bitis",
                "config": {
                    "max_retry": 3 if adim == "llm_cagir" else 0,
                    "timeout_ms": 30000 if adim == "llm_cagir" else 5000,
                },
            }
        )

    # Kenarlar (sabit akÄ±ÅŸ)
    edges: List[Dict[str, Any]] = [
        {"source": "basla", "target": "hafiza_kontrol", "type": "direct", "label": ""},
        {
            "source": "hafiza_kontrol",
            "target": "web_ara",
            "type": "direct",
            "label": "",
        },
        {"source": "web_ara", "target": "skill_ara", "type": "direct", "label": ""},
        {"source": "skill_ara", "target": "llm_cagir", "type": "direct", "label": ""},
        {
            "source": "llm_cagir",
            "target": "tool_calistir",
            "type": "direct",
            "label": "",
        },
        {
            "source": "tool_calistir",
            "target": "llm_cagir",
            "type": "direct",
            "label": "",
        },
        {
            "source": "tool_calistir",
            "target": "yanit_ver",
            "type": "direct",
            "label": "",
        },
        {"source": "yanit_ver", "target": "bitis", "type": "direct", "label": ""},
    ]

    # KoÅŸullu dallanmalar (conditional edges)
    conditions: List[Dict[str, Any]] = [
        {
            "id": "hafiza_var_mi",
            "source": "hafiza_kontrol",
            "branches": [
                {
                    "condition": True,
                    "target": "web_ara",
                    "label": "Hafiza yok â†’ normal akis",
                },
                {
                    "condition": False,
                    "target": "yanit_ver",
                    "label": "Hafiza var â†’ onbellekten yanit",
                },
            ],
            "default": "web_ara",
        },
        {
            "id": "web_gerekli_mi",
            "source": "web_ara",
            "branches": [
                {
                    "condition": True,
                    "target": "skill_ara",
                    "label": "Web sonucu eklendi â†’ devam",
                },
                {
                    "condition": False,
                    "target": "skill_ara",
                    "label": "Web gerekmez â†’ atla",
                },
            ],
            "default": "skill_ara",
        },
        {
            "id": "skill_var_mi",
            "source": "skill_ara",
            "branches": [
                {
                    "condition": True,
                    "target": "llm_cagir",
                    "label": "Skill bulundu â†’ context'e ekle",
                },
                {
                    "condition": False,
                    "target": "llm_cagir",
                    "label": "Skill yok â†’ dogrudan LLM",
                },
            ],
            "default": "llm_cagir",
        },
        {
            "id": "tool_gerekli_mi",
            "source": "tool_calistir",
            "branches": [
                {
                    "condition": True,
                    "target": "llm_cagir",
                    "label": "Tool sonucu var â†’ tekrar LLM (ReAct)",
                },
                {
                    "condition": False,
                    "target": "yanit_ver",
                    "label": "Tool yok â†’ yanit ver",
                },
            ],
            "default": "yanit_ver",
        },
        {
            "id": "hata_var_mi",
            "source": "llm_cagir",
            "branches": [
                {
                    "condition": True,
                    "target": "bitis",
                    "label": "Hata var â†’ hata yonetimi + bitis",
                },
                {
                    "condition": False,
                    "target": "tool_calistir",
                    "label": "Basarili â†’ tool/yanti kontrolu",
                },
            ],
            "default": "tool_calistir",
        },
    ]

    return {
        "graph": {
            "name": "ReYMeN Conversation StateGraph",
            "version": "1.0.0",
            "description": "ReYMeN Agent konusma dongusu LangGraph StateGraph exportu. "
            "conversation_loop.py:ConversationLoop.run_conversation() akisi.",
            "framework": "langgraph",
            "generated_at": datetime.now().isoformat(),
            "source_file": "reymen/cereyan/conversation_loop.py",
            "max_iterations": 30,
        },
        "nodes": nodes,
        "edges": edges,
        "conditions": conditions,
    }


def _mermaid_insa(graph_data: dict) -> str:
    """Graph JSON'dan Mermaid.js flowchart metni oluÅŸtur.

    Args:
        graph_data: _graph_json_insa() Ã§Ä±ktÄ±sÄ±.

    Returns:
        ```mermaid flowchart TD ... ``` bloku.
    """
    lines: List[str] = []
    lines.append("```mermaid")
    lines.append("flowchart TD")
    lines.append("")

    # Stil tanÄ±mlarÄ±
    lines.append("    %% Stiller")
    lines.append(
        "    classDef entry fill:#1a1a2e,stroke:#e94560,stroke-width:2px,color:#fff"
    )
    lines.append(
        "    classDef node fill:#16213e,stroke:#0f3460,stroke-width:1px,color:#a8d8ea"
    )
    lines.append(
        "    classDef exit fill:#1a1a2e,stroke:#00ff88,stroke-width:2px,color:#fff"
    )
    lines.append(
        "    classDef condition fill:#2d1b2e,stroke:#e94560,stroke-width:1px,color:#ff9a9e"
    )
    lines.append("")

    # DÃ¼ÄŸÃ¼mler
    for node in graph_data["nodes"]:
        node_id = node["id"]
        label = node["label"]
        # Mermaid'de yeni satÄ±r ve Ã¶zel karakterleri temizle
        desc = node.get("description", "")
        desc_short = desc.replace('"', "'")[:60]
        if desc_short:
            lines.append(f'    {node_id}["{label}<br/><small>{desc_short}</small>"]')
        else:
            lines.append(f'    {node_id}["{label}"]')

        # SÄ±nÄ±f ata
        if node.get("entry"):
            lines.append(f"    class {node_id} entry;")
        elif node.get("exit"):
            lines.append(f"    class {node_id} exit;")
        else:
            lines.append(f"    class {node_id} node;")
    lines.append("")

    # KoÅŸul dÃ¼ÄŸÃ¼mleri (diamond)
    condition_ids: set = set()
    for cond in graph_data["conditions"]:
        cid = cond["id"]
        condition_ids.add(cid)
        # KoÅŸul etiketini formatla
        label = cid.replace("_", " ").title()
        lines.append(f'    {cid}{{"{label}"}}')
        lines.append(f"    class {cid} condition;")

        # Kaynak dÃ¼ÄŸÃ¼m -> koÅŸul
        lines.append(f'    {cond["source"]} -->|"kosul"| {cid}')
        # KoÅŸul -> her dal
        for branch in cond["branches"]:
            target = branch["target"]
            lbl = branch.get("label", f"{branch['condition']}")
            if branch["condition"] is True:
                lines.append(f'    {cid} -->|"{lbl}"| {target}')
            else:
                lines.append(f'    {cid} -..->|"{lbl}"| {target}')
    lines.append("")

    # Direkt kenarlar (koÅŸul iÃ§ermeyen)
    for edge in graph_data["edges"]:
        src = edge["source"]
        tgt = edge["target"]
        # KoÅŸul tarafÄ±ndan zaten kapsanÄ±yorsa atla
        skip = False
        for cond in graph_data["conditions"]:
            if cond["source"] == src:
                skip = True
                break
        if not skip:
            lbl = edge.get("label", "")
            if lbl:
                lines.append(f'    {src} -->|"{lbl}"| {tgt}')
            else:
                lines.append(f"    {src} --> {tgt}")
    lines.append("")

    # Alt-graph: ReAct Loop
    lines.append("    subgraph ReAct_Loop[ReAct DÃ¶ngÃ¼sÃ¼]")
    lines.append("        direction LR")
    lines.append("        llm_cagir --> tool_calistir")
    lines.append("        tool_calistir --> llm_cagir")
    lines.append("    end")
    lines.append("")

    lines.append("```")
    return "\n".join(lines)


def _mermaid_readme_md_insa(graph_data: dict) -> str:
    """Ä°nsan-okunur Markdown belgesi oluÅŸtur (graph.md iÃ§in).

    Args:
        graph_data: _graph_json_insa() Ã§Ä±ktÄ±sÄ±.

    Returns:
        Markdown iÃ§eriÄŸi.
    """
    meta = graph_data["graph"]
    lines: List[str] = []
    lines.append(f"# {meta['name']}")
    lines.append("")
    lines.append(f"> **Versiyon:** {meta['version']}")
    lines.append(f"> **OluÅŸturulma:** {meta['generated_at']}")
    lines.append(f"> **Kaynak:** `{meta['source_file']}`")
    lines.append(f"> **Maksimum Iterasyon:** {meta['max_iterations']}")
    lines.append("")
    lines.append(meta["description"])
    lines.append("")
    lines.append("---")
    lines.append("")

    # AkÄ±ÅŸ ÅemasÄ±
    lines.append("## AkÄ±ÅŸ ÅemasÄ±")
    lines.append("")
    lines.append(_mermaid_insa(graph_data))
    lines.append("")
    lines.append("---")
    lines.append("")

    # DÃ¼ÄŸÃ¼m AÃ§Ä±klamalarÄ±
    lines.append("## DÃ¼ÄŸÃ¼mler (Nodes)")
    lines.append("")
    lines.append("| DÃ¼ÄŸÃ¼m | TÃ¼r | AÃ§Ä±klama |")
    lines.append("|-------|-----|----------|")
    for node in graph_data["nodes"]:
        node_type = (
            "GiriÅŸ" if node.get("entry") else ("Ã‡Ä±kÄ±ÅŸ" if node.get("exit") else "Ä°ÅŸlem")
        )
        desc = node.get("description", "").replace("\n", " ").strip()
        if len(desc) > 100:
            desc = desc[:97] + "..."
        lines.append(f"| `{node['id']}` | {node_type} | {desc} |")
    lines.append("")
    lines.append("---")
    lines.append("")

    # KoÅŸullar
    lines.append("## KoÅŸullar (Conditions)")
    lines.append("")
    lines.append("| KoÅŸul | Kaynak | AÃ§Ä±klama |")
    lines.append("|-------|--------|----------|")
    for cond in graph_data["conditions"]:
        desc = KOSUL_ACIKLAMA.get(cond["id"], "")
        branch_strs = [
            f"`{b['condition']}` â†’ `{b['target']}`" for b in cond["branches"]
        ]
        branches = " | ".join(branch_strs)
        lines.append(
            f"| `{cond['id']}` | `{cond['source']}` | {desc}<br/>({branches}) |"
        )
    lines.append("")
    lines.append("---")
    lines.append("")

    # ReAct DÃ¶ngÃ¼sÃ¼ DetayÄ±
    lines.append("## ReAct DÃ¶ngÃ¼sÃ¼")
    lines.append("")
    lines.append("```")
    lines.append("llm_cagir  â”€â”€(tool_calls)â”€â”€â–º  tool_calistir")
    lines.append("    â–²                              â”‚")
    lines.append("    â”‚                              â”‚")
    lines.append("    â””â”€â”€â”€â”€(tool sonucu)â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜")
    lines.append("              â”‚")
    lines.append("              â–¼")
    lines.append("         yanit_ver")
    lines.append("```")
    lines.append("")
    lines.append(
        "Bu dÃ¶ngÃ¼ max_iterations ({}) kadar tekrar eder. "
        "Her turda LLM tool_calls dÃ¶ndÃ¼rÃ¼rse araÃ§ Ã§alÄ±ÅŸtÄ±rÄ±lÄ±r "
        "ve sonuÃ§ tekrar LLM'e gÃ¶nderilir. Tool_calls yoksa "
        "doÄŸrudan yanÄ±t verilir.".format(meta["max_iterations"])
    )
    lines.append("")
    lines.append("---")
    lines.append("")

    # Hata YÃ¶netimi
    lines.append("## Hata YÃ¶netimi")
    lines.append("")
    lines.append(
        "- **Retry:** LLM Ã§aÄŸrÄ±sÄ± baÅŸarÄ±sÄ±z olursa 3 kez dene (exponential backoff)"
    )
    lines.append(
        "- **Fallback:** Provider Ã§Ã¶kerse, `_provider_rotate` ile alternatif provider'a geÃ§"
    )
    lines.append(
        "- **Circuit Breaker:** 3 ardÄ±ÅŸÄ±k hata â†’ circuit breaker aÃ§Ä±lÄ±r, kalÄ±cÄ± kilit"
    )
    lines.append("- **TakÄ±lma DedektÃ¶rÃ¼:** AynÄ± eylem 3x tekrar ederse loop sonlanÄ±r")
    lines.append("- **Budget:** IterationBudget aÅŸÄ±lÄ±rsa loop sonlanÄ±r")
    lines.append("- **Interrupt:** Ctrl+C ile kullanÄ±cÄ± iptali desteklenir")
    lines.append("")

    return "\n".join(lines)


# â”€â”€ Ana Export Fonksiyonu â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


def langgraph_export(
    output_dir: Optional[str] = None,
    cikti_ver: bool = False,
) -> Dict[str, Any]:
    """LangGraph export'unu oluÅŸturur ve dosyalara yazar.

    Args:
        output_dir: Ã‡Ä±ktÄ± dizini (None = proje kÃ¶kÃ¼).
        cikti_ver: True ise dict olarak dÃ¶ndÃ¼r (dosya yazmaz).

    Returns:
        {
            "graph": { ... },           # JSON graph verisi
            "graph_json_path": "...",    # graph.json yolu
            "graph_md_path": "...",      # graph.md yolu
            "basarili": True/False,
        }
    """
    graph_data = _graph_json_insa()
    graph_json = graph_data  # zaten dict

    sonuc: Dict[str, Any] = {
        "graph": graph_json,
        "basarili": True,
    }

    if cikti_ver:
        return sonuc

    # Ã‡Ä±ktÄ± dizini belirle
    if output_dir:
        cikti_dizini = Path(output_dir)
    else:
        # Proje kÃ¶kÃ¼: reymen/core/langgraph_export.py -> ../../
        cikti_dizini = Path(__file__).resolve().parent.parent.parent

    cikti_dizini.mkdir(parents=True, exist_ok=True)

    # graph.json
    json_yolu = cikti_dizini / "graph.json"
    try:
        json_icerik = json.dumps(graph_json, indent=2, ensure_ascii=False)
        json_yolu.write_text(json_icerik, encoding="utf-8")
        sonuc["graph_json_path"] = str(json_yolu.resolve())
    except Exception as e:
        sonuc["graph_json_path"] = None
        sonuc["basarili"] = False
        sonuc["json_hatasi"] = str(e)

    # graph.md
    md_yolu = cikti_dizini / "graph.md"
    try:
        md_icerik = _mermaid_readme_md_insa(graph_json)
        md_yolu.write_text(md_icerik, encoding="utf-8")
        sonuc["graph_md_path"] = str(md_yolu.resolve())
    except Exception as e:
        sonuc["graph_md_path"] = None
        sonuc["md_hatasi"] = str(e)

    return sonuc


# â”€â”€ CLI Entegrasyonu â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


def cmd_export(args) -> str:
    """CLI handler: ``reymen --langgraph-export`` Ã§aÄŸrÄ±sÄ±.

    Args:
        args: argparse.Namespace (output_dir varsa).

    Returns:
        KullanÄ±cÄ±ya gÃ¶sterilecek metin.
    """
    output_dir = getattr(args, "output_dir", None)
    sonuc = langgraph_export(output_dir=output_dir)

    if not sonuc["basarili"]:
        hata = sonuc.get("json_hatasi", "") or sonuc.get("md_hatasi", "Bilinmeyen hata")
        return f"\n  [HATA] LangGraph export basarisiz: {hata}"

    lines = ["", "  [OK] LangGraph StateGraph export tamamlandi:"]
    if sonuc.get("graph_json_path"):
        lines.append(f"         JSON: {sonuc['graph_json_path']}")
    if sonuc.get("graph_md_path"):
        lines.append(f"         MD:   {sonuc['graph_md_path']}")

    # DÃ¼ÄŸÃ¼m sayÄ±sÄ±
    node_sayisi = len(sonuc["graph"].get("nodes", []))
    edge_sayisi = len(sonuc["graph"].get("edges", []))
    cond_sayisi = len(sonuc["graph"].get("conditions", []))
    lines.append(
        f"         Dugum: {node_sayisi}, Kenar: {edge_sayisi}, Kosul: {cond_sayisi}"
    )

    # Mermaid Ã¶nizleme
    lines.append("")
    lines.append("  Akis semasi:")
    lines.append("")
    mermaid = _mermaid_insa(sonuc["graph"])
    for satir in mermaid.split("\n"):
        lines.append(f"    {satir}")
    lines.append("")

    return "\n".join(lines)


# â”€â”€ DoÄŸrudan Ã‡alÄ±ÅŸtÄ±rma â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

if __name__ == "__main__":
    """DoÄŸrudan Ã§alÄ±ÅŸtÄ±rma: python -m reymen.core.langgraph_export"""
    sonuc = langgraph_export(output_dir=os.getcwd())
    if sonuc["basarili"]:
        print(
            f"[OK] LangGraph export:\n  JSON: {sonuc.get('graph_json_path')}\n  MD:   {sonuc.get('graph_md_path')}"
        )
    else:
        print(f"[HATA] {sonuc}")
        sys.exit(1)
