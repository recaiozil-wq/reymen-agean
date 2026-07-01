# -*- coding: utf-8 -*-
"""
langgraph_export.py — ReYMeN Konusma Döngüsü → LangGraph StateGraph Export Modülü.

conversation_loop.py'deki run_conversation() akışını analiz edip:
- LangGraph StateGraph JSON formatında düğüm/kenar/koşul çıktısı
- Mermaid.js flowchart (```mermaid bloku)
- CLI üzerinden reymen --langgraph-export ile graph.json + graph.md

Akış adımları (run_conversation içindeki sıra):
  1. BASLA     → task_id + session + budget + sistem_prompt oluştur
  2. HAFIZA_KONTROL → OnceHafiza'da ara, session context injection
  3. WEB_ARA   → web arama (gerekirse)
  4. SKILL_ARA → skill tarama (FTS5) + ref_processor
  5. LLM_CAGIR → API çağrısı (retry + fallback ile)
  6. TOOL_CALISTIR → tool_calls varsa çalıştır, sonuçları ekle, loop
  7. YANIT_VER → text response al, onayla
  8. BITIS     → OnceHafiza'ya kaydet, session kapat, log

Koşullar (conditional edges):
  - hafiza_var_mi:  Bellekte eşleşme var mı?
  - web_gerekli_mi: Web arama gerekli mi?
  - skill_var_mi:   Skill eşleşmesi var mı?
  - tool_gerekli_mi:LLM tool_calls döndürdü mü?
  - hata_var_mi:    Hata oluştu mu?
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


# ── Sabitler ────────────────────────────────────────────────────────────────────

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

# Her düğümün conversation_loop.py'deki karşılık gelen kod bölgesi
DUGUM_ACIKLAMA: Dict[str, str] = {
    "basla": (
        "Task ID oluştur, session başlat, budget (IterationBudget) kur, "
        "sistem prompt'u inşa et (PromptBuilder + SOUL.md + durum.json)."
    ),
    "hafiza_kontrol": (
        "OnceHafiza'da arama (hafizada_ara), session context injection, "
        "önceki konuşma geçmişini yükle, önbellek (ONCELIK_CACHE) kontrolü."
    ),
    "web_ara": (
        "Web arama motoru (SearchDispatcher / DDGS) ile güncel bilgi topla, "
        "halüsinasyon önleme için gerçek veri ekle."
    ),
    "skill_ara": (
        "Skill tarama (FTS5 full-text search), konuşmadan skill çıkarma "
        "(konusmadan_skill_cikar), @file/@url referans işleme (ref_processor)."
    ),
    "llm_cagir": (
        "API çağrısı (direct_api_call): retry + fallback provider rotasyonu, "
        "streaming, circuit breaker, hata sınıflandırma."
    ),
    "tool_calistir": (
        "LLM'den gelen tool_calls'ları motor üzerinden çalıştır "
        "(motor_tools_schema_al + _arac_calistir), sonuçları messages'a ekle, "
        "tekrar LLM'e dön (ReAct loop)."
    ),
    "yanit_ver": (
        "LLM'den text response al, doğrulama (kısa yanıt kontrolü), "
        "kullanıcıya döndür."
    ),
    "bitis": (
        "OnceHafiza'ya kaydet (ogrenme), session kapat, A2A broadcast, "
        "hook'ları tetikle (tur_bitir, oturum_bitir), loglama."
    ),
}

KOSUL_ACIKLAMA: Dict[str, str] = {
    "hafiza_var_mi": "OnceHafiza'da eşleşen kayıt var mı? Varsa ön belleğe al, yoksa normal akış.",
    "web_gerekli_mi": "Kullanıcı sorusu güncel bilgi/web araması gerektiriyor mu?",
    "skill_var_mi": "FTS5 taramasında eşleşen skill bulundu mu? Varsa context'e ekle.",
    "tool_gerekli_mi": "LLM tool_calls döndürdü mü? True → araçları çalıştır, False → yanıt ver.",
    "hata_var_mi": "API veya araç çağrısında hata oluştu mu? True → hata yönetimi.",
}


# ── Graph Tanımı ───────────────────────────────────────────────────────────────

def _graph_json_insa() -> dict:
    """LangGraph StateGraph formatında JSON graph yapısı oluştur.

    Düğümler (nodes): her akış adımı
    Kenarlar (edges): sabit yönlendirmeler
    Koşullar (conditions): dallanma noktaları

    Returns:
        LangGraph StateGraph JSON dict.
    """
    nodes: List[Dict[str, Any]] = []
    for adim in AKIS_ADIMLARI:
        nodes.append({
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
        })

    # Kenarlar (sabit akış)
    edges: List[Dict[str, Any]] = [
        {"source": "basla",         "target": "hafiza_kontrol", "type": "direct",  "label": ""},
        {"source": "hafiza_kontrol","target": "web_ara",        "type": "direct",  "label": ""},
        {"source": "web_ara",       "target": "skill_ara",      "type": "direct",  "label": ""},
        {"source": "skill_ara",     "target": "llm_cagir",      "type": "direct",  "label": ""},
        {"source": "llm_cagir",     "target": "tool_calistir",  "type": "direct",  "label": ""},
        {"source": "tool_calistir", "target": "llm_cagir",      "type": "direct",  "label": ""},
        {"source": "tool_calistir", "target": "yanit_ver",      "type": "direct",  "label": ""},
        {"source": "yanit_ver",     "target": "bitis",          "type": "direct",  "label": ""},
    ]

    # Koşullu dallanmalar (conditional edges)
    conditions: List[Dict[str, Any]] = [
        {
            "id": "hafiza_var_mi",
            "source": "hafiza_kontrol",
            "branches": [
                {"condition": True,  "target": "web_ara",       "label": "Hafiza yok → normal akis"},
                {"condition": False, "target": "yanit_ver",     "label": "Hafiza var → onbellekten yanit"},
            ],
            "default": "web_ara",
        },
        {
            "id": "web_gerekli_mi",
            "source": "web_ara",
            "branches": [
                {"condition": True,  "target": "skill_ara",     "label": "Web sonucu eklendi → devam"},
                {"condition": False, "target": "skill_ara",     "label": "Web gerekmez → atla"},
            ],
            "default": "skill_ara",
        },
        {
            "id": "skill_var_mi",
            "source": "skill_ara",
            "branches": [
                {"condition": True,  "target": "llm_cagir",     "label": "Skill bulundu → context'e ekle"},
                {"condition": False, "target": "llm_cagir",     "label": "Skill yok → dogrudan LLM"},
            ],
            "default": "llm_cagir",
        },
        {
            "id": "tool_gerekli_mi",
            "source": "tool_calistir",
            "branches": [
                {"condition": True,  "target": "llm_cagir",     "label": "Tool sonucu var → tekrar LLM (ReAct)"},
                {"condition": False, "target": "yanit_ver",     "label": "Tool yok → yanit ver"},
            ],
            "default": "yanit_ver",
        },
        {
            "id": "hata_var_mi",
            "source": "llm_cagir",
            "branches": [
                {"condition": True,  "target": "bitis",         "label": "Hata var → hata yonetimi + bitis"},
                {"condition": False, "target": "tool_calistir", "label": "Basarili → tool/yanti kontrolu"},
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
    """Graph JSON'dan Mermaid.js flowchart metni oluştur.

    Args:
        graph_data: _graph_json_insa() çıktısı.

    Returns:
        ```mermaid flowchart TD ... ``` bloku.
    """
    lines: List[str] = []
    lines.append("```mermaid")
    lines.append("flowchart TD")
    lines.append("")

    # Stil tanımları
    lines.append("    %% Stiller")
    lines.append("    classDef entry fill:#1a1a2e,stroke:#e94560,stroke-width:2px,color:#fff")
    lines.append("    classDef node fill:#16213e,stroke:#0f3460,stroke-width:1px,color:#a8d8ea")
    lines.append("    classDef exit fill:#1a1a2e,stroke:#00ff88,stroke-width:2px,color:#fff")
    lines.append("    classDef condition fill:#2d1b2e,stroke:#e94560,stroke-width:1px,color:#ff9a9e")
    lines.append("")

    # Düğümler
    for node in graph_data["nodes"]:
        node_id = node["id"]
        label = node["label"]
        # Mermaid'de yeni satır ve özel karakterleri temizle
        desc = node.get("description", "")
        desc_short = desc.replace('"', "'")[:60]
        if desc_short:
            lines.append(f'    {node_id}["{label}<br/><small>{desc_short}</small>"]')
        else:
            lines.append(f'    {node_id}["{label}"]')

        # Sınıf ata
        if node.get("entry"):
            lines.append(f'    class {node_id} entry;')
        elif node.get("exit"):
            lines.append(f'    class {node_id} exit;')
        else:
            lines.append(f'    class {node_id} node;')
    lines.append("")

    # Koşul düğümleri (diamond)
    condition_ids: set = set()
    for cond in graph_data["conditions"]:
        cid = cond["id"]
        condition_ids.add(cid)
        # Koşul etiketini formatla
        label = cid.replace("_", " ").title()
        lines.append(f'    {cid}{{"{label}"}}')
        lines.append(f'    class {cid} condition;')

        # Kaynak düğüm -> koşul
        lines.append(f'    {cond["source"]} -->|"kosul"| {cid}')
        # Koşul -> her dal
        for branch in cond["branches"]:
            target = branch["target"]
            lbl = branch.get("label", f"{branch['condition']}")
            if branch["condition"] is True:
                lines.append(f'    {cid} -->|"{lbl}"| {target}')
            else:
                lines.append(f'    {cid} -..->|"{lbl}"| {target}')
    lines.append("")

    # Direkt kenarlar (koşul içermeyen)
    for edge in graph_data["edges"]:
        src = edge["source"]
        tgt = edge["target"]
        # Koşul tarafından zaten kapsanıyorsa atla
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
                lines.append(f'    {src} --> {tgt}')
    lines.append("")

    # Alt-graph: ReAct Loop
    lines.append("    subgraph ReAct_Loop[ReAct Döngüsü]")
    lines.append("        direction LR")
    lines.append("        llm_cagir --> tool_calistir")
    lines.append("        tool_calistir --> llm_cagir")
    lines.append("    end")
    lines.append("")

    lines.append("```")
    return "\n".join(lines)


def _mermaid_readme_md_insa(graph_data: dict) -> str:
    """İnsan-okunur Markdown belgesi oluştur (graph.md için).

    Args:
        graph_data: _graph_json_insa() çıktısı.

    Returns:
        Markdown içeriği.
    """
    meta = graph_data["graph"]
    lines: List[str] = []
    lines.append(f"# {meta['name']}")
    lines.append("")
    lines.append(f"> **Versiyon:** {meta['version']}")
    lines.append(f"> **Oluşturulma:** {meta['generated_at']}")
    lines.append(f"> **Kaynak:** `{meta['source_file']}`")
    lines.append(f"> **Maksimum Iterasyon:** {meta['max_iterations']}")
    lines.append("")
    lines.append(meta["description"])
    lines.append("")
    lines.append("---")
    lines.append("")

    # Akış Şeması
    lines.append("## Akış Şeması")
    lines.append("")
    lines.append(_mermaid_insa(graph_data))
    lines.append("")
    lines.append("---")
    lines.append("")

    # Düğüm Açıklamaları
    lines.append("## Düğümler (Nodes)")
    lines.append("")
    lines.append("| Düğüm | Tür | Açıklama |")
    lines.append("|-------|-----|----------|")
    for node in graph_data["nodes"]:
            node_type = "Giriş" if node.get("entry") else ("Çıkış" if node.get("exit") else "İşlem")
            desc = node.get("description", "").replace("\n", " ").strip()
            if len(desc) > 100:
                desc = desc[:97] + "..."
            lines.append(f"| `{node['id']}` | {node_type} | {desc} |")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Koşullar
    lines.append("## Koşullar (Conditions)")
    lines.append("")
    lines.append("| Koşul | Kaynak | Açıklama |")
    lines.append("|-------|--------|----------|")
    for cond in graph_data["conditions"]:
        desc = KOSUL_ACIKLAMA.get(cond["id"], "")
        branch_strs = [f"`{b['condition']}` → `{b['target']}`" for b in cond["branches"]]
        branches = " | ".join(branch_strs)
        lines.append(f"| `{cond['id']}` | `{cond['source']}` | {desc}<br/>({branches}) |")
    lines.append("")
    lines.append("---")
    lines.append("")

    # ReAct Döngüsü Detayı
    lines.append("## ReAct Döngüsü")
    lines.append("")
    lines.append("```")
    lines.append("llm_cagir  ──(tool_calls)──►  tool_calistir")
    lines.append("    ▲                              │")
    lines.append("    │                              │")
    lines.append("    └────(tool sonucu)─────────────┘")
    lines.append("              │")
    lines.append("              ▼")
    lines.append("         yanit_ver")
    lines.append("```")
    lines.append("")
    lines.append("Bu döngü max_iterations ({}) kadar tekrar eder. "
                 "Her turda LLM tool_calls döndürürse araç çalıştırılır "
                 "ve sonuç tekrar LLM'e gönderilir. Tool_calls yoksa "
                 "doğrudan yanıt verilir.".format(meta["max_iterations"]))
    lines.append("")
    lines.append("---")
    lines.append("")

    # Hata Yönetimi
    lines.append("## Hata Yönetimi")
    lines.append("")
    lines.append("- **Retry:** LLM çağrısı başarısız olursa 3 kez dene (exponential backoff)")
    lines.append("- **Fallback:** Provider çökerse, `_provider_rotate` ile alternatif provider'a geç")
    lines.append("- **Circuit Breaker:** 3 ardışık hata → circuit breaker açılır, kalıcı kilit")
    lines.append("- **Takılma Dedektörü:** Aynı eylem 3x tekrar ederse loop sonlanır")
    lines.append("- **Budget:** IterationBudget aşılırsa loop sonlanır")
    lines.append("- **Interrupt:** Ctrl+C ile kullanıcı iptali desteklenir")
    lines.append("")

    return "\n".join(lines)


# ── Ana Export Fonksiyonu ─────────────────────────────────────────────────────

def langgraph_export(
    output_dir: Optional[str] = None,
    cikti_ver: bool = False,
) -> Dict[str, Any]:
    """LangGraph export'unu oluşturur ve dosyalara yazar.

    Args:
        output_dir: Çıktı dizini (None = proje kökü).
        cikti_ver: True ise dict olarak döndür (dosya yazmaz).

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

    # Çıktı dizini belirle
    if output_dir:
        cikti_dizini = Path(output_dir)
    else:
        # Proje kökü: reymen/core/langgraph_export.py -> ../../
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


# ── CLI Entegrasyonu ──────────────────────────────────────────────────────────

def cmd_export(args) -> str:
    """CLI handler: ``reymen --langgraph-export`` çağrısı.

    Args:
        args: argparse.Namespace (output_dir varsa).

    Returns:
        Kullanıcıya gösterilecek metin.
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

    # Düğüm sayısı
    node_sayisi = len(sonuc["graph"].get("nodes", []))
    edge_sayisi = len(sonuc["graph"].get("edges", []))
    cond_sayisi = len(sonuc["graph"].get("conditions", []))
    lines.append(f"         Dugum: {node_sayisi}, Kenar: {edge_sayisi}, Kosul: {cond_sayisi}")

    # Mermaid önizleme
    lines.append("")
    lines.append("  Akis semasi:")
    lines.append("")
    mermaid = _mermaid_insa(sonuc["graph"])
    for satir in mermaid.split("\n"):
        lines.append(f"    {satir}")
    lines.append("")

    return "\n".join(lines)


# ── Doğrudan Çalıştırma ───────────────────────────────────────────────────────

if __name__ == "__main__":
    """Doğrudan çalıştırma: python -m reymen.core.langgraph_export"""
    sonuc = langgraph_export(output_dir=os.getcwd())
    if sonuc["basarili"]:
        print(f"[OK] LangGraph export:\n  JSON: {sonuc.get('graph_json_path')}\n  MD:   {sonuc.get('graph_md_path')}")
    else:
        print(f"[HATA] {sonuc}")
        sys.exit(1)
