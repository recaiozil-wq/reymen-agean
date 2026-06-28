# -*- coding: utf-8 -*-
"""plugins/kanban_plugin/__init__.py — Kanban Plugin.

Kanban gorev yonetimini plugin olarak sarar.
"""


__all__ = ['KanbanOrchestrator', 'kanban_ekle', 'kanban_listele', 'kaydet']
plugin_adi = "kanban"
plugin_aciklamasi = "Kanban gorev takip sistemi - ekle, listele, tamamla, sil"


def kaydet(motor):
    try:
        from kanban_orchestrator import KanbanOrchestrator
        k = KanbanOrchestrator()

        def kanban_listele(args=""):
            return k.listele() or "[Kanban] Gorev yok."

        def kanban_ekle(args):
            parts = args.split("|")
            baslik = parts[0].strip()
            aciklama = parts[1].strip() if len(parts) > 1 else ""
            return k.ekle(baslik, aciklama)

        if hasattr(motor, "_registry") and motor._registry:
            motor._registry.kaydet("KANBAN_LISTELE", kanban_listele)
            motor._registry.kaydet("KANBAN_EKLE", kanban_ekle)
    except Exception:
        pass
