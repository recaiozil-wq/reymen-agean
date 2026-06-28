# -*- coding: utf-8 -*-
"""feishu_doc_tool.py — Feishu/Lark Dokuman Yonetimi.

Feishu Open Platform REST API ile dokuman listeleme, okuma,
yazma ve arama islemleri.
ENV: FEISHU_APP_ID, FEISHU_APP_SECRET
"""

import json
import os
import urllib.request
import urllib.parse

FEISHU_APP_ID = os.environ.get("FEISHU_APP_ID", "")
FEISHU_APP_SECRET = os.environ.get("FEISHU_APP_SECRET", "")
FEISHU_API_BASE = "https://open.feishu.cn/open-apis"


def _tenant_access_token_al() -> str:
    """Feishu Open Platform'dan tenant access token al."""
    if not FEISHU_APP_ID or not FEISHU_APP_SECRET:
        return ""
    try:
        veri = json.dumps({
            "app_id": FEISHU_APP_ID,
            "app_secret": FEISHU_APP_SECRET,
        }).encode("utf-8")
        req = urllib.request.Request(
            f"{FEISHU_API_BASE}/auth/v3/tenant_access_token/internal",
            data=veri,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            yanit = json.loads(r.read().decode("utf-8"))
            return yanit.get("tenant_access_token", "")
    except Exception:
        return ""


def _feishu_get(yol: str, token: str) -> dict:
    """Feishu API'ye GET istegi yap."""
    try:
        req = urllib.request.Request(
            f"{FEISHU_API_BASE}{yol}",
            headers={"Authorization": f"Bearer {token}"},
        )
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read().decode("utf-8"))
    except Exception as e:
        return {"error": str(e)}


def _feishu_post(yol: str, veri: dict, token: str) -> dict:
    """Feishu API'ye POST istegi yap."""
    try:
        data = json.dumps(veri).encode("utf-8")
        req = urllib.request.Request(
            f"{FEISHU_API_BASE}{yol}",
            data=data,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
        )
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read().decode("utf-8"))
    except Exception as e:
        return {"error": str(e)}


def run(**kwargs) -> str:
    """Feishu/Lark dokuman islemlerini yapar.

    Args:
        islem (zorunlu): "listele", "oku", "yaz", "ara"
        token: Mevcut access token (bos olabilir, otomatik alinir)
        doc_token: Dokuman ID
        icerik: Yazilacak icerik (yaz isleminde)

    Returns:
        Islem sonucu metin olarak
    """
    try:
        islem = kwargs.get("islem")
        if not islem:
            return "Hata: 'islem' parametresi zorunludur (listele, oku, yaz, ara)."

        # Token al
        token = kwargs.get("token") or _tenant_access_token_al()
        if not token:
            return "Hata: Feishu token alinamadi. FEISHU_APP_ID ve FEISHU_APP_SECRET kontrol edin."

        if islem == "listele":
            return _dokumanlari_listele(token)

        elif islem == "oku":
            doc_token = kwargs.get("doc_token")
            if not doc_token:
                return "Hata: 'doc_token' parametresi zorunludur."
            return _dokuman_oku(doc_token, token)

        elif islem == "yaz":
            doc_token = kwargs.get("doc_token", "")
            icerik = kwargs.get("icerik", "")
            if not icerik:
                return "Hata: 'icerik' parametresi zorunludur."
            return _dokuman_yaz(doc_token, icerik, token)

        elif islem == "ara":
            sorgu = kwargs.get("icerik", "")
            if not sorgu:
                return "Hata: 'icerik' (sorgu) parametresi zorunludur."
            return _dokuman_ara(sorgu, token)

        else:
            return f"Hata: Gecersiz islem '{islem}'. Secenekler: listele, oku, yaz, ara."

    except Exception as e:
        return f"Hata: {e}"


def _dokumanlari_listele(token: str) -> str:
    """Kullanicinin dokumanlarini listele."""
    yanit = _feishu_get("/drive/v1/files?page_size=20", token)
    if "error" in yanit:
        return f"Feishu listeleme hatasi: {yanit['error']}"

    data = yanit.get("data", {})
    dosyalar = data.get("files", [])
    if not dosyalar:
        return "Dokuman bulunamadi."

    satirlar = [f"Feishu Dokumanlari ({len(dosyalar)}):"]
    for d in dosyalar:
        satirlar.append(
            f"  [{d.get('token','')}] {d.get('name','')} "
            f"({d.get('type','')})"
        )
    return "\n".join(satirlar)


def _dokuman_oku(doc_token: str, token: str) -> str:
    """Belirtilen dokumanin icerigini oku."""
    yanit = _feishu_get(f"/docx/v1/documents/{doc_token}/raw_content", token)
    if "error" in yanit:
        return f"Feishu okuma hatasi: {yanit['error']}"

    data = yanit.get("data", {})
    icerik = data.get("content", "") or data.get("raw_content", "")
    if not icerik:
        return f"Dokuman bulunamadi veya bos: {doc_token}"

    return f"[Feishu Dokuman: {doc_token}]\n{icerik[:5000]}"


def _dokuman_yaz(doc_token: str, icerik: str, token: str) -> str:
    """Dokuman olustur veya var olana icerik ekle."""
    if not doc_token:
        # Yeni dokuman olustur
        yanit = _feishu_post("/docx/v1/documents", {"title": icerik[:50]}, token)
        if "error" in yanit:
            return f"Feishu dokuman olusturma hatasi: {yanit['error']}"
        data = yanit.get("data", {}).get("document", {})
        yeni_id = data.get("document_id", "")
        return f"Yeni dokuman olusturuldu: {yeni_id}"
    else:
        # Mevcut dokumana icerik ekle (block ekleme)
        block_veri = {
            "block_type": 1,
            "text": {
                "elements": [{"text_run": {"content": icerik}}],
            },
        }
        yanit = _feishu_post(
            f"/docx/v1/documents/{doc_token}/blocks/{doc_token}/children",
            {"children": [block_veri]},
            token,
        )
        if "error" in yanit:
            return f"Feishu dokuman yazma hatasi: {yanit['error']}"
        return f"Icerik eklendi: {doc_token}"


def _dokuman_ara(sorgu: str, token: str) -> str:
    """Dokumanlarda metin ara."""
    yanit = _feishu_post(
        "/search/v1/pattern",
        {"query": sorgu, "page_size": 10},
        token,
    )
    if "error" in yanit:
        return f"Feishu arama hatasi: {yanit['error']}"

    data = yanit.get("data", {})
    items = data.get("items", [])
    if not items:
        return f"'{sorgu}' ile ilgili sonuc bulunamadi."

    satirlar = [f"Feishu Arama Sonuclari ('{sorgu}'):"]
    for i in items:
        satirlar.append(
            f"  [{i.get('token','')}] {i.get('title','')} "
            f"- {i.get('summary','')[:100]}"
        )
    return "\n".join(satirlar)


if __name__ == "__main__":
    print(f"FEISHU_APP_ID: {'✓' if FEISHU_APP_ID else '✗'}")
    print(f"FEISHU_APP_SECRET: {'✓' if FEISHU_APP_SECRET else '✗'}")
    print(run(islem="listele"))
