# -*- coding: utf-8 -*-
"""plugins/notion_plugin/__init__.py — Notion Gelismis Plugin.

Sayfa olusturma, veritabani sorgulama, medya yukleme.
"""


__all__ = ['kaydet', 'notion_medya_yukle', 'notion_veritabani_sorgula', 'notion_yaz']
plugin_adi = "notion"
plugin_aciklamasi = "Notion sayfa olusturma, veritabani sorgulama ve medya yukleme"


def kaydet(motor):
    try:
        import os
        import json
        import requests

        def _notion_headers():
            token = os.environ.get("NOTION_API_TOKEN", "")
            if not token:
                raise ValueError("[Notion] Token ayarlanmamis. NOTION_API_TOKEN ortam degiskeni gerekli.")
            return {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "Notion-Version": "2022-06-28",
            }

        def notion_yaz(args):
            """Notion sayfasina veri yaz."""
            token = os.environ.get("NOTION_API_TOKEN", "")
            db_id = os.environ.get("NOTION_DATABASE_ID", "")
            if not token:
                return "[Notion] Token ayarlanmamis."
            if not db_id:
                return "[Notion] Database ID ayarlanmamis."
            parts = args.split("|")
            baslik = parts[0].strip()
            icerik = parts[1].strip() if len(parts) > 1 else ""
            r = requests.post(
                "https://api.notion.com/v1/pages",
                headers=_notion_headers(),
                json={
                    "parent": {"database_id": db_id},
                    "properties": {
                        "title": {"title": [{"text": {"content": baslik}}]},
                    },
                    "children": [{"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"type": "text", "text": {"content": icerik}}]}}] if icerik else [],
                },
                timeout=10,
            )
            if r.status_code == 200:
                return f"[Notion] '{baslik}' kaydedildi."
            return f"[Notion] Hata {r.status_code}: {r.text[:200]}"

        def notion_veritabani_sorgula(args):
            """Notion veritabaninda sorgu yap."""
            db_id = os.environ.get("NOTION_DATABASE_ID", "")
            if not db_id:
                return "[Notion] Database ID ayarlanmamis."
            try:
                filt = json.loads(args) if args.strip() else {}
            except Exception:
                filt = {}
            r = requests.post(
                f"https://api.notion.com/v1/databases/{db_id}/query",
                headers=_notion_headers(),
                json=filt,
                timeout=10,
            )
            if r.status_code == 200:
                veri = r.json()
                sayfa_sayisi = len(veri.get("results", []))
                return f"[Notion] Sorgu tamam: {sayfa_sayisi} sonuc"
            return f"[Notion] Sorgu hatasi {r.status_code}: {r.text[:200]}"

        def notion_medya_yukle(args):
            """Notion sayfasina medya yukle (gorsel/ses)."""
            parts = args.split("|")
            sayfa_id = parts[0].strip()
            medya_url = parts[1].strip() if len(parts) > 1 else ""
            if not sayfa_id or not medya_url:
                return "[Notion] Sayfa ID ve medya URL'si gerekli (sayfa_id|url)"
            r = requests.patch(
                f"https://api.notion.com/v1/blocks/{sayfa_id}/children",
                headers=_notion_headers(),
                json={
                    "children": [{
                        "object": "block",
                        "type": "image",
                        "image": {"type": "external", "external": {"url": medya_url}},
                    }]
                },
                timeout=10,
            )
            if r.status_code == 200:
                return f"[Notion] Medya yuklendi: {medya_url[:50]}"
            return f"[Notion] Medya yukleme hatasi {r.status_code}: {r.text[:200]}"

        if hasattr(motor, "_registry") and motor._registry:
            motor._registry.kaydet("NOTION_YAZ", notion_yaz)
            motor._registry.kaydet("NOTION_VERITABANI_SORGULA", notion_veritabani_sorgula)
            motor._registry.kaydet("NOTION_MEDYA_YUKLE", notion_medya_yukle)
    except Exception:
        pass
