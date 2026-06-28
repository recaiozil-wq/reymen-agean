#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
microsoft_graph_client.py — Microsoft Graph istemci.
E-posta, takvim, dosya API.
"""

import json
import urllib.request
import urllib.error


GRAPH_API = "https://graph.microsoft.com/v1.0"
CONTENT_TYPE_JSON = "application/json"


def _graph_istek(method, endpoint, token, data=None):
    """Microsoft Graph API'ye istek gönder."""
    url = f"{GRAPH_API}{endpoint}"
    try:
        req = urllib.request.Request(url, method=method)
        req.add_header("Authorization", f"Bearer {token}")
        req.add_header("Accept", "application/json")
        if data:
            req.add_header("Content-Type", "application/json")
            body = json.dumps(data).encode('utf-8')
            with urllib.request.urlopen(req, data=body, timeout=30) as yanit:
                return json.loads(yanit.read().decode())
        else:
            with urllib.request.urlopen(req, timeout=30) as yanit:
                icerik = yanit.read().decode()
                if icerik:
                    return json.loads(icerik)
                return {}
    except urllib.error.HTTPError as e:
        try:
            hata_icerik = e.read().decode()
            return {"hata": f"HTTP {e.code}: {hata_icerik[:500]}"}
        except Exception:
            return {"hata": f"HTTP {e.code}: {str(e)}"}
    except Exception as e:
        return {"hata": str(e)}


def _eposta_gonder(token, parametreler=None):
    """E-posta gönder."""
    if parametreler is None:
        parametreler = {}
    
    alici = parametreler.get("alici", "")
    konu = parametreler.get("konu", "Test Mesajı")
    icerik = parametreler.get("icerik", "Bu bir test mesajıdır.")
    
    eposta_data = {
        "message": {
            "subject": konu,
            "body": {
                "contentType": "Text",
                "content": icerik
            },
            "toRecipients": [
                {
                    "emailAddress": {
                        "address": alici
                    }
                }
            ]
        }
    }
    
    return _graph_istek("POST", "/me/sendMail", token, eposta_data)


def _takvim_oku(token, parametreler=None):
    """Takvim olaylarını oku."""
    if parametreler is None:
        parametreler = {}
    
    limit = parametreler.get("limit", 10)
    return _graph_istek("GET", f"/me/events?$top={limit}&$orderby=start/dateTime DESC", token)


def _dosya_listele(token, parametreler=None):
    """OneDrive dosyalarını listele."""
    if parametreler is None:
        parametreler = {}
    
    yol = parametreler.get("yol", "")
    if yol:
        return _graph_istek("GET", f"/me/drive/root:/{yol}:/children", token)
    else:
        return _graph_istek("GET", "/me/drive/root/children", token)


def run(islem="dosya_listele", token="", parametreler="{}"):
    """
    Microsoft Graph istemci.
    
    Parametreler:
        islem (str): eposta_gonder / takvim_oku / dosya_listele
        token (str): Access token
        parametreler (str): JSON parametreler
    
    Returns:
        str: API yanıtı JSON formatında
    """
    try:
        parsed_params = {}
        if parametreler:
            try:
                parsed_params = json.loads(parametreler) if isinstance(parametreler, str) else parametreler
            except json.JSONDecodeError:
                parsed_params = {"raw": parametreler}

        if not token:
            return json.dumps({"durum": "hata", "mesaj": "token parametresi gerekli"}, ensure_ascii=False)

        if islem == "eposta_gonder":
            sonuc = _eposta_gonder(token, parsed_params)
            if "hata" in sonuc:
                return json.dumps({"durum": "hata", "mesaj": sonuc["hata"]}, ensure_ascii=False)
            return json.dumps({"durum": "basarili", "mesaj": "E-posta gönderildi", "yanit": sonuc}, ensure_ascii=False, default=str)

        elif islem == "takvim_oku":
            sonuc = _takvim_oku(token, parsed_params)
            if "hata" in sonuc:
                return json.dumps({"durum": "hata", "mesaj": sonuc["hata"]}, ensure_ascii=False)
            olaylar = sonuc.get("value", [])
            return json.dumps({
                "durum": "basarili",
                "olay_sayisi": len(olaylar),
                "olaylar": [{
                    "konu": o.get("subject", ""),
                    "baslangic": o.get("start", {}).get("dateTime", ""),
                    "bitis": o.get("end", {}).get("dateTime", ""),
                    "konum": o.get("location", {}).get("displayName", "")
                } for o in olaylar]
            }, ensure_ascii=False, default=str)

        elif islem == "dosya_listele":
            sonuc = _dosya_listele(token, parsed_params)
            if "hata" in sonuc:
                return json.dumps({"durum": "hata", "mesaj": sonuc["hata"]}, ensure_ascii=False)
            dosyalar = sonuc.get("value", [])
            return json.dumps({
                "durum": "basarili",
                "dosya_sayisi": len(dosyalar),
                "dosyalar": [{
                    "ad": d.get("name", ""),
                    "boyut": d.get("size", 0),
                    "dizin_mi": "folder" in d,
                    "son_degistirme": d.get("lastModifiedDateTime", "")
                } for d in dosyalar]
            }, ensure_ascii=False, default=str)

        else:
            return json.dumps({"durum": "hata", "mesaj": f"bilinmeyen işlem: {islem}"}, ensure_ascii=False)

    except Exception as e:
        return json.dumps({"durum": "hata", "mesaj": str(e)}, ensure_ascii=False)


if __name__ == "__main__":
    print(run("dosya_listele", "test-token"))
