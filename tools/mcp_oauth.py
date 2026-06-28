#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mcp_oauth.py — MCP OAuth yönetimi.
OAuth 2.0 token alma, yenileme, saklama.
"""

import json
import os
import time
import base64
import hashlib
import urllib.parse
import urllib.request
import logging
logger = logging.getLogger(__name__)


OAUTH_DOSYASI = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'mcp_oauth.json')


def _oauth_oku():
    """OAuth token'larını oku."""
    if not os.path.exists(OAUTH_DOSYASI):
        return {}
    try:
        with open(OAUTH_DOSYASI, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}


def _oauth_yaz(veri):
    """OAuth token'larını yaz."""
    try:
        with open(OAUTH_DOSYASI, 'w', encoding='utf-8') as f:
            json.dump(veri, f, indent=2, ensure_ascii=False)
        try:
            os.chmod(OAUTH_DOSYASI, 0o600)
        except Exception:
            logger.warning("[fix_01_sessiz_except] Exception")
        return True
    except Exception:
        return False


def _token_al(saglayici, yetki_kodu, redirect_uri="http://localhost", client_id="", client_secret=""):
    """OAuth token'ı al."""
    # Token endpoint'ini belirle
    endpoints = {
        "github": "https://github.com/login/oauth/access_token",
        "google": "https://oauth2.googleapis.com/token",
        "microsoft": "https://login.microsoftonline.com/common/oauth2/v2.0/token",
    }
    
    token_url = endpoints.get(saglayici)
    if not token_url:
        # Özel sağlayıcı
        token_url = f"https://{saglayici}.auth/token"
    
    # Token isteği
    data = urllib.parse.urlencode({
        "grant_type": "authorization_code",
        "code": yetki_kodu,
        "redirect_uri": redirect_uri,
        "client_id": client_id,
        "client_secret": client_secret
    }).encode()
    
    try:
        req = urllib.request.Request(token_url, data=data, method="POST")
        req.add_header("Accept", "application/json")
        with urllib.request.urlopen(req, timeout=30) as yanit:
            yanit_data = json.loads(yanit.read().decode())
        
        token_bilgisi = {
            "saglayici": saglayici,
            "access_token": yanit_data.get("access_token", ""),
            "refresh_token": yanit_data.get("refresh_token", ""),
            "token_type": yanit_data.get("token_type", "bearer"),
            "expires_in": yanit_data.get("expires_in", 3600),
            "alim_zamani": time.time(),
            "scope": yanit_data.get("scope", "")
        }
        
        # Kaydet
        veri = _oauth_oku()
        veri[saglayici] = token_bilgisi
        _oauth_yaz(veri)
        
        return {"durum": "basarili", "token": token_bilgisi}
    except Exception as e:
        return {"durum": "hata", "mesaj": str(e)}


def _token_yenile(saglayici, client_id="", client_secret=""):
    """OAuth token'ını yenile."""
    veri = _oauth_oku()
    if saglayici not in veri:
        return {"durum": "hata", "mesaj": f"'{saglayici}' için token bulunamadı"}
    
    mevcut = veri[saglayici]
    refresh_token = mevcut.get("refresh_token", "")
    if not refresh_token:
        return {"durum": "hata", "mesaj": "Refresh token mevcut değil"}
    
    endpoints = {
        "github": "https://github.com/login/oauth/access_token",
        "google": "https://oauth2.googleapis.com/token",
        "microsoft": "https://login.microsoftonline.com/common/oauth2/v2.0/token",
    }
    token_url = endpoints.get(saglayici)
    if not token_url:
        token_url = f"https://{saglayici}.auth/token"
    
    data = urllib.parse.urlencode({
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": client_id,
        "client_secret": client_secret
    }).encode()
    
    try:
        req = urllib.request.Request(token_url, data=data, method="POST")
        req.add_header("Accept", "application/json")
        with urllib.request.urlopen(req, timeout=30) as yanit:
            yanit_data = json.loads(yanit.read().decode())
        
        veri[saglayici].update({
            "access_token": yanit_data.get("access_token", ""),
            "refresh_token": yanit_data.get("refresh_token", refresh_token),
            "expires_in": yanit_data.get("expires_in", 3600),
            "alim_zamani": time.time()
        })
        _oauth_yaz(veri)
        
        return {"durum": "basarili", "token": veri[saglayici]}
    except Exception as e:
        return {"durum": "hata", "mesaj": str(e)}


def _kaydet(saglayici, token_verisi):
    """Token'ı doğrudan kaydet."""
    veri = _oauth_oku()
    veri[saglayici] = token_verisi
    if _oauth_yaz(veri):
        return {"durum": "basarili", "mesaj": f"'{saglayici}' token'ı kaydedildi"}
    return {"durum": "hata", "mesaj": "OAuth dosyası yazılamadı"}


def _temizle(saglayici=None):
    """Token'ları temizle."""
    if saglayici:
        veri = _oauth_oku()
        if saglayici in veri:
            del veri[saglayici]
            _oauth_yaz(veri)
            return {"durum": "basarili", "mesaj": f"'{saglayici}' temizlendi"}
        return {"durum": "hata", "mesaj": f"'{saglayici}' bulunamadı"}
    else:
        _oauth_yaz({})
        return {"durum": "basarili", "mesaj": "Tüm token'lar temizlendi"}


def run(islem="token_al", saglayici="", yetki_kodu="", client_id="", client_secret=""):
    """
    MCP OAuth yönetimi.
    
    Parametreler:
        islem (str): token_al / token_yenile / kaydet / temizle
        saglayici (str): OAuth sağlayıcı adı (github, google, microsoft)
        yetki_kodu (str): Yetkilendirme kodu (token_al işleminde)
        client_id (str): OAuth client ID
        client_secret (str): OAuth client secret
    
    Returns:
        str: İşlem sonucu JSON formatında
    """
    try:
        if islem == "token_al":
            if not saglayici or not yetki_kodu:
                return json.dumps({"durum": "hata", "mesaj": "saglayici ve yetki_kodu parametreleri gerekli"}, ensure_ascii=False)
            sonuc = _token_al(saglayici, yetki_kodu, client_id=client_id, client_secret=client_secret)

        elif islem == "token_yenile":
            if not saglayici:
                return json.dumps({"durum": "hata", "mesaj": "saglayici parametresi gerekli"}, ensure_ascii=False)
            sonuc = _token_yenile(saglayici, client_id=client_id, client_secret=client_secret)

        elif islem == "kaydet":
            if not saglayici:
                return json.dumps({"durum": "hata", "mesaj": "saglayici parametresi gerekli"}, ensure_ascii=False)
            token_verisi = {
                "access_token": yetki_kodu if yetki_kodu else "",
                "saglayici": saglayici,
                "alim_zamani": time.time()
            }
            sonuc = _kaydet(saglayici, token_verisi)

        elif islem == "temizle":
            sonuc = _temizle(saglayici if saglayici else None)

        else:
            return json.dumps({"durum": "hata", "mesaj": f"bilinmeyen işlem: {islem}"}, ensure_ascii=False)

        return json.dumps(sonuc, ensure_ascii=False, default=str)

    except Exception as e:
        return json.dumps({"durum": "hata", "mesaj": str(e)}, ensure_ascii=False)


if __name__ == "__main__":
    print(run("temizle"))
