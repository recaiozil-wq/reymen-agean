# -*- coding: utf-8 -*-
"""
plugins/notion/__init__.py — Notion Entegrasyonu Plugin.

Araçlar: NOTION_YAZ, NOTION_OKU, NOTION_ARA, NOTION_SAYFA_OLUSTUR, NOTION_DOGRULA

.env'de:
  NOTION_API_TOKEN=secret_xxxx   veya   NOTION_API_KEY=secret_xxxx
  NOTION_DATABASE_ID=xxxxx       (NOTION_YAZ icin gerekli)
"""

__all__ = ['Path', 'kaydet']
import json
import os
import re
import sys
import urllib.request
import urllib.error
from pathlib import Path

PLUGIN_ADI       = "notion"
PLUGIN_VERSIYON  = "1.0.0"
PLUGIN_ACIKLAMA  = "Notion sayfası okuma, yazma, arama entegrasyonu"

NOTION_API_BASE = "https://api.notion.com/v1"
NOTION_VERSION  = "2022-06-28"


def _token() -> str:
    t = os.environ.get("NOTION_API_TOKEN", "") or os.environ.get("NOTION_API_KEY", "")
    return t.strip()


def _db_id() -> str:
    return os.environ.get("NOTION_DATABASE_ID", "").strip()


def _basliklar(headers_ek: dict = None) -> dict:
    h = {
        "Authorization": f"Bearer {_token()}",
        "Content-Type": "application/json",
        "Notion-Version": NOTION_VERSION,
    }
    if headers_ek:
        h.update(headers_ek)
    return h


def _istek(yontem: str, yol: str, veri: dict = None, timeout: int = 20) -> dict:
    url  = f"{NOTION_API_BASE}/{yol.lstrip('/')}"
    body = json.dumps(veri).encode() if veri else None
    req  = urllib.request.Request(url, data=body, headers=_basliklar(),
                                  method=yontem)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return {"ok": True, "data": json.loads(r.read())}
    except urllib.error.HTTPError as e:
        try:
            detay = json.loads(e.read())
        except Exception:
            detay = {}
        return {"ok": False, "status": e.code, "error": detay}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def _metin_blogu(icerik: str) -> list:
    """2000 karakter siniri olan rich_text blogu olustur."""
    return [{"text": {"content": icerik[:2000]}}]


def _sayfa_icerik_al(page_id: str) -> str:
    """Bir Notion sayfasinin icerigini blok olarak al."""
    r = _istek("GET", f"blocks/{page_id}/children")
    if not r["ok"]:
        return f"[Notion] Icerik alinmadi: {r.get('error', '')}"
    satirlar = []
    for blok in r["data"].get("results", []):
        tip  = blok.get("type", "")
        veri = blok.get(tip, {})
        rts  = veri.get("rich_text", [])
        metin = "".join(rt.get("plain_text", "") for rt in rts)
        if metin:
            satirlar.append(metin)
    return "\n".join(satirlar) or "(bos sayfa)"


# ── Araç fonksiyonlari ────────────────────────────────────────────────────────

def _notion_yaz(ham: str) -> str:
    """NOTION_YAZ "baslik" "icerik" — veritabanina yeni kayit ekle."""
    if not _token():
        return "[Notion] NOTION_API_TOKEN ayarli degil."
    if not _db_id():
        return "[Notion] NOTION_DATABASE_ID ayarli degil."
    params = re.findall(r'"((?:[^"\\]|\\.)*)"', ham)
    baslik  = params[0] if params else ham.strip('"')
    icerik  = params[1] if len(params) > 1 else ""
    payload = {
        "parent": {"database_id": _db_id()},
        "properties": {
            "Name": {"title": _metin_blogu(baslik)},
        },
    }
    if icerik:
        payload["children"] = [{
            "object": "block",
            "type": "paragraph",
            "paragraph": {"rich_text": _metin_blogu(icerik)},
        }]
    r = _istek("POST", "pages", payload)
    if r["ok"]:
        url = r["data"].get("url", "")
        return f"[Notion] Sayfa olusturuldu: {baslik}\n{url}"
    return f"[Notion] Hata: {r.get('error', r)}"


def _notion_oku(ham: str) -> str:
    """NOTION_OKU "page_id" — sayfa icerigini al."""
    if not _token():
        return "[Notion] NOTION_API_TOKEN ayarli degil."
    params  = re.findall(r'"((?:[^"\\]|\\.)*)"', ham)
    page_id = params[0] if params else ham.strip().strip('"')
    page_id = page_id.replace("-", "").strip()
    if not page_id:
        return "[Notion] page_id gerekli."
    r = _istek("GET", f"pages/{page_id}")
    if not r["ok"]:
        return f"[Notion] Sayfa bulunamadi: {r.get('error', '')}"
    props  = r["data"].get("properties", {})
    baslik = ""
    for p in props.values():
        if p.get("type") == "title":
            baslik = "".join(t.get("plain_text", "") for t in p.get("title", []))
            break
    icerik = _sayfa_icerik_al(page_id)
    return f"[Notion] {baslik}\n\n{icerik[:2000]}"


def _notion_ara(ham: str) -> str:
    """NOTION_ARA "sorgu" — Notion'da sayfa/veritabani ara."""
    if not _token():
        return "[Notion] NOTION_API_TOKEN ayarli degil."
    params = re.findall(r'"((?:[^"\\]|\\.)*)"', ham)
    sorgu  = params[0] if params else ham.strip('"')
    r = _istek("POST", "search", {"query": sorgu, "page_size": 5})
    if not r["ok"]:
        return f"[Notion] Arama hatasi: {r.get('error', '')}"
    sonuclar = r["data"].get("results", [])
    if not sonuclar:
        return f"[Notion] '{sorgu}' icin sonuc yok."
    satirlar = [f"[Notion] '{sorgu}' sonuclari ({len(sonuclar)}):"]
    for s in sonuclar:
        obj_tip = s.get("object", "")
        props   = s.get("properties", {})
        baslik  = ""
        for p in props.values():
            tip_ = p.get("type", "")
            if tip_ == "title":
                baslik = "".join(t.get("plain_text", "") for t in p.get("title", []))
                break
        url = s.get("url", "")
        satirlar.append(f"  [{obj_tip}] {baslik or '(isimsiz)'}\n  {url}")
    return "\n".join(satirlar)


def _notion_sayfa_olustur(ham: str) -> str:
    """NOTION_SAYFA_OLUSTUR "baslik" "parent_page_id" "icerik" — standalone sayfa."""
    if not _token():
        return "[Notion] NOTION_API_TOKEN ayarli degil."
    params    = re.findall(r'"((?:[^"\\]|\\.)*)"', ham)
    baslik    = params[0] if params else "Yeni Sayfa"
    parent_id = params[1] if len(params) > 1 else ""
    icerik    = params[2] if len(params) > 2 else ""
    if not parent_id:
        return "[Notion] parent_page_id gerekli."
    payload = {
        "parent": {"page_id": parent_id},
        "properties": {
            "title": {"title": _metin_blogu(baslik)},
        },
    }
    if icerik:
        payload["children"] = [{
            "object": "block",
            "type": "paragraph",
            "paragraph": {"rich_text": _metin_blogu(icerik)},
        }]
    r = _istek("POST", "pages", payload)
    if r["ok"]:
        url = r["data"].get("url", "")
        return f"[Notion] Sayfa olusturuldu: {baslik}\n{url}"
    return f"[Notion] Hata: {r.get('error', r)}"


def _notion_dogrula(ham: str) -> str:
    """NOTION_DOGRULA — API baglantisini test et."""
    if not _token():
        return "[Notion] NOTION_API_TOKEN ayarli degil."
    r = _istek("GET", "users/me")
    if r["ok"]:
        ad = r["data"].get("name", "") or r["data"].get("bot", {}).get("workspace_name", "")
        return f"[Notion] Baglanti basarili. Bot: {ad}"
    return f"[Notion] Baglanti basarisiz: {r.get('error', r.get('status', ''))}"


# ── Plugin kayit ──────────────────────────────────────────────────────────────

def kaydet(motor):
    """motor.py'ye Notion araclarini kaydet."""
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from plugins.kanban import _plugin_arac_kaydet

    _plugin_arac_kaydet(motor, "NOTION_YAZ",            _notion_yaz)
    _plugin_arac_kaydet(motor, "NOTION_OKU",            _notion_oku)
    _plugin_arac_kaydet(motor, "NOTION_ARA",            _notion_ara)
    _plugin_arac_kaydet(motor, "NOTION_SAYFA_OLUSTUR",  _notion_sayfa_olustur)
    _plugin_arac_kaydet(motor, "NOTION_DOGRULA",        _notion_dogrula)
    print(f"[Plugin:{PLUGIN_ADI}] 5 arac kayit edildi.")
