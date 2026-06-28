# -*- coding: utf-8 -*-
"""
plugins/kanban/__init__.py — Kanban Plugin.

ReYMeN motoruna KANBAN_EKLE, KANBAN_LISTE, KANBAN_GUNCELLE, KANBAN_OZET
araclarini ekler. motor.py'ye kaydet() ile entegre olur.
"""

__all__ = ['AdvancedKanbanOrchestrator', 'Path', 'kanban_ekle', 'kanban_guncelle', 'kanban_liste', 'kanban_ozet', 'kanban_tamamla', 'kaydet', 'yeni_calistir']
from pathlib import Path

PLUGIN_ADI = "kanban"
PLUGIN_VERSIYON = "1.0.0"
PLUGIN_ACIKLAMA = "SQLite tabanli Kanban gorev tahtasi"

_ORCHS = None


def _orch():
    global _ORCHS
    if _ORCHS is None:
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent.parent))
        from kanban_orchestrator import AdvancedKanbanOrchestrator
        _ORCHS = AdvancedKanbanOrchestrator()
    return _ORCHS


def kaydet(motor):
    """motor.py'ye araclari kaydet."""

    def kanban_ekle(ham: str) -> str:
        import re
        params = re.findall(r'"((?:[^"\\]|\\.)*)"', ham)
        baslik = params[0] if params else ham.strip('"')
        oncelik = int(params[1]) if len(params) > 1 and params[1].isdigit() else 2
        g = _orch().ekle(baslik, oncelik=oncelik)
        return f"[Kanban] Eklendi: #{g['id']} — {g['baslik']}"

    def kanban_liste(ham: str) -> str:
        import re
        params = re.findall(r'"((?:[^"\\]|\\.)*)"', ham)
        durum = params[0] if params else ""
        gorevler = _orch().liste(durum=durum, limit=20)
        if not gorevler:
            return "[Kanban] Bos."
        satirlar = [f"#{g['id']} [{g['durum']}] {g['baslik']}" for g in gorevler]
        return "[Kanban]\n" + "\n".join(satirlar)

    def kanban_guncelle(ham: str) -> str:
        import re
        params = re.findall(r'"((?:[^"\\]|\\.)*)"', ham)
        if not params:
            return "[Kanban] Hata: id ve durum gerekli."
        try:
            gorev_id = int(params[0])
        except ValueError:
            return f"[Kanban] Hata: gecersiz id: {params[0]}"
        yeni_durum = params[1] if len(params) > 1 else "done"
        g = _orch().guncelle(gorev_id, durum=yeni_durum)
        return f"[Kanban] Guncellendi: #{gorev_id} → {yeni_durum}" if g else f"[Kanban] Bulunamadi: #{gorev_id}"

    def kanban_ozet(ham: str) -> str:
        oz = _orch().ozet()
        satirlar = [f"Toplam: {oz['toplam']}"]
        for durum, sayi in oz.get("kolonlar", {}).items():
            satirlar.append(f"  {durum}: {sayi}")
        return "[Kanban Ozet]\n" + "\n".join(satirlar)

    def kanban_tamamla(ham: str) -> str:
        import re
        params = re.findall(r'"((?:[^"\\]|\\.)*)"', ham)
        try:
            gorev_id = int(params[0]) if params else int(ham.strip())
        except Exception:
            return "[Kanban] Hata: gecersiz id."
        g = _orch().tamamla(gorev_id)
        return f"[Kanban] Tamamlandi: #{gorev_id}" if g else f"[Kanban] Bulunamadi: #{gorev_id}"

    # Motor'a kaydet
    _plugin_arac_kaydet(motor, "KANBAN_EKLE",     kanban_ekle)
    _plugin_arac_kaydet(motor, "KANBAN_LISTE",    kanban_liste)
    _plugin_arac_kaydet(motor, "KANBAN_GUNCELLE", kanban_guncelle)
    _plugin_arac_kaydet(motor, "KANBAN_OZET",     kanban_ozet)
    _plugin_arac_kaydet(motor, "KANBAN_TAMAMLA",  kanban_tamamla)
    print(f"[Plugin:{PLUGIN_ADI}] 5 arac kayit edildi.")


def _plugin_arac_kaydet(motor, arac_adi: str, fn):
    """Motor'a dinamik araç ekle — calistir() dispatch tablosuna yazar."""
    if not hasattr(motor, "_plugin_araclar"):
        motor._plugin_araclar = {}
        _patch_motor(motor)
    motor._plugin_araclar[arac_adi] = fn


def _patch_motor(motor):
    """motor.calistir() metodunu plugin araclarini destekleyecek sekilde sar."""
    orijinal = motor.calistir.__func__ if hasattr(motor.calistir, "__func__") else None
    if orijinal is None:
        return
    import types

    def yeni_calistir(self, arac, ham_param):
        plugin_araclar = getattr(self, "_plugin_araclar", {})
        if arac in plugin_araclar:
            return plugin_araclar[arac](ham_param)
        return orijinal(self, arac, ham_param)

    motor.calistir = types.MethodType(yeni_calistir, motor)
