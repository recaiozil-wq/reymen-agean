# -*- coding: utf-8 -*-
"""feishu_drive_tool.py — Feishu/Lark Drive Yonetimi.

Feishu Drive API v4 ile dosya listeleme, indirme ve yukleme.
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
    """Feishu/Lark Drive islemlerini yapar.

    Args:
        islem (zorunlu): "listele", "indir", "yukle"
        folder_token: Klasor token (listeleme icin)
        dosya_yolu: Indirilecek/yuklenecek dosya yolu

    Returns:
        Islem sonucu metin olarak
    """
    try:
        islem = kwargs.get("islem")
        if not islem:
            return "Hata: 'islem' parametresi zorunludur (listele, indir, yukle)."

        token = _tenant_access_token_al()
        if not token:
            return "Hata: Feishu token alinamadi. FEISHU_APP_ID ve FEISHU_APP_SECRET kontrol edin."

        if islem == "listele":
            folder_token = kwargs.get("folder_token", "")
            return _dosyalari_listele(folder_token, token)

        elif islem == "indir":
            file_token = kwargs.get("dosya_yolu", kwargs.get("folder_token", ""))
            if not file_token:
                return "Hata: 'folder_token' (file_token) parametresi zorunludur."
            return _dosya_indir(file_token, token)

        elif islem == "yukle":
            dosya_yolu = kwargs.get("dosya_yolu", "")
            if not dosya_yolu:
                return "Hata: 'dosya_yolu' parametresi zorunludur."
            folder_token = kwargs.get("folder_token", "")
            return _dosya_yukle(dosya_yolu, folder_token, token)

        else:
            return f"Hata: Gecersiz islem '{islem}'. Secenekler: listele, indir, yukle."

    except Exception as e:
        return f"Hata: {e}"


def _dosyalari_listele(folder_token: str, token: str) -> str:
    """Klasordeki dosyalari listele."""
    yol = "/drive/v1/files?page_size=50"
    if folder_token:
        yol += f"&folder_token={urllib.parse.quote(folder_token)}"

    yanit = _feishu_get(yol, token)
    if "error" in yanit:
        return f"Drive listeleme hatasi: {yanit['error']}"

    data = yanit.get("data", {})
    dosyalar = data.get("files", [])
    if not dosyalar:
        return "Dosya bulunamadi."

    satirlar = [f"Feishu Drive Dosyalari ({len(dosyalar)}):"]
    for d in dosyalar:
        satirlar.append(
            f"  [{d.get('token','')}] {d.get('name','')} "
            f"({d.get('type','')}) - {d.get('size',0)} byte"
        )
    return "\n".join(satirlar)


def _dosya_indir(file_token: str, token: str) -> str:
    """Dosyayi indir (indirme linki olustur)."""
    yanit = _feishu_get(f"/drive/v1/files/{file_token}/download", token)
    if "error" in yanit:
        return f"Dosya indirme hatasi: {yanit['error']}"

    data = yanit.get("data", {})
    url = data.get("download_url", "")
    if url:
        return f"Indirme linki: {url}"

    return f"Dosya icin indirme bilgisi alindi: {file_token}"


def _dosya_yukle(dosya_yolu: str, folder_token: str, token: str) -> str:
    """Dosyayi Drive'a yukle."""
    if not os.path.exists(dosya_yolu):
        return f"Dosya bulunamadi: {dosya_yolu}"

    dosya_adi = os.path.basename(dosya_yolu)
    try:
        with open(dosya_yolu, "rb") as f:
            dosya_verisi = f.read()
    except Exception as e:
        return f"Dosya okuma hatasi: {e}"

    # Yukleme icin multipart form-data (upload_all)
    import uuid
    boundary = uuid.uuid4().hex

    body_parts = []
    body_parts.append(f"--{boundary}")
    body_parts.append('Content-Disposition: form-data; name="file_name"')
    body_parts.append("")
    body_parts.append(dosya_adi)

    body_parts.append(f"--{boundary}")
    body_parts.append(f'Content-Disposition: form-data; name="file"; filename="{dosya_adi}"')
    body_parts.append("Content-Type: application/octet-stream")
    body_parts.append("")
    body_parts.append("")  # placeholder for binary data
    body_parts.append(f"--{boundary}--")

    # Build body with binary data
    body_str = "\r\n".join(body_parts[:-3]) + "\r\n"
    body_close = "\r\n" + "--" + boundary + "--\r\n"

    body = body_str.encode("utf-8") + dosya_verisi + body_close.encode("utf-8")

    try:
        req = urllib.request.Request(
            f"{FEISHU_API_BASE}/drive/v1/files/upload_all",
            data=body,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": f"multipart/form-data; boundary={boundary}",
            },
        )
        with urllib.request.urlopen(req, timeout=30) as r:
            yanit = json.loads(r.read().decode("utf-8"))
    except Exception as e:
        return f"Dosya yukleme hatasi: {e}"

    if "error" in yanit:
        return f"Feishu yukleme hatasi: {yanit['error']}"

    data = yanit.get("data", {})
    file_token = data.get("file_token", "")
    return f"Dosya yuklendi: {dosya_adi} -> token: {file_token}"


if __name__ == "__main__":
    print(f"FEISHU_APP_ID: {'✓' if FEISHU_APP_ID else '✗'}")
    print(f"FEISHU_APP_SECRET: {'✓' if FEISHU_APP_SECRET else '✗'}")
    print(run(islem="listele"))
