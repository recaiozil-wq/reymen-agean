#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
microsoft_graph_auth.py — Microsoft Graph kimlik doğrulama.
OAuth 2.0 device code flow.
"""

import json
import time
import urllib.parse
import urllib.request


AUTHORITY = "https://login.microsoftonline.com/common"
GRAPH_SCOPE = "https://graph.microsoft.com/.default"


def _device_code_al(client_id, tenant="common"):
    """Device code al."""
    url = f"https://login.microsoftonline.com/{tenant}/oauth2/v2.0/devicecode"
    data = urllib.parse.urlencode({
        "client_id": client_id,
        "scope": GRAPH_SCOPE
    }).encode()
    
    try:
        req = urllib.request.Request(url, data=data, method="POST")
        req.add_header("Accept", "application/json")
        with urllib.request.urlopen(req, timeout=30) as yanit:
            return json.loads(yanit.read().decode())
    except Exception as e:
        return {"hata": str(e)}


def _token_al(client_id, device_code, tenant="common"):
    """Device code ile token al."""
    url = f"https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token"
    data = urllib.parse.urlencode({
        "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
        "client_id": client_id,
        "device_code": device_code
    }).encode()
    
    try:
        req = urllib.request.Request(url, data=data, method="POST")
        req.add_header("Accept", "application/json")
        with urllib.request.urlopen(req, timeout=30) as yanit:
            return json.loads(yanit.read().decode())
    except Exception as e:
        return {"hata": str(e)}


def _token_yenile(client_id, refresh_token, tenant="common"):
    """Refresh token ile token yenile."""
    url = f"https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token"
    data = urllib.parse.urlencode({
        "grant_type": "refresh_token",
        "client_id": client_id,
        "refresh_token": refresh_token,
        "scope": GRAPH_SCOPE
    }).encode()
    
    try:
        req = urllib.request.Request(url, data=data, method="POST")
        req.add_header("Accept", "application/json")
        with urllib.request.urlopen(req, timeout=30) as yanit:
            return json.loads(yanit.read().decode())
    except Exception as e:
        return {"hata": str(e)}


def run(islem="giris_yap", client_id="", refresh_token=""):
    """
    Microsoft Graph kimlik doğrulama.
    
    Parametreler:
        islem (str): giris_yap / token_al / token_yenile / cikis_yap
        client_id (str): Azure AD uygulama client ID
        refresh_token (str): Refresh token (token_yenile işleminde)
    
    Returns:
        str: Kimlik doğrulama sonucu
    """
    try:
        if islem == "giris_yap":
            if not client_id:
                return json.dumps({"durum": "hata", "mesaj": "client_id parametresi gerekli"}, ensure_ascii=False)
            
            device_code_response = _device_code_al(client_id)
            if "hata" in device_code_response:
                return json.dumps({
                    "durum": "hata",
                    "mesaj": f"Device code alınamadı: {device_code_response['hata']}"
                }, ensure_ascii=False)
            
            return json.dumps({
                "durum": "basarili",
                "mesaj": "Lütfen tarayıcınızda aşağıdaki URL'yi açın ve kodu girin",
                "device_code": device_code_response.get("device_code", ""),
                "user_code": device_code_response.get("user_code", ""),
                "verification_uri": device_code_response.get("verification_uri", ""),
                "expires_in": device_code_response.get("expires_in", 900),
                "interval": device_code_response.get("interval", 5),
                "sonraki_adim": "token_al işlemini device_code ile çağırın"
            }, ensure_ascii=False)

        elif islem == "token_al":
            if not client_id or not refresh_token:
                return json.dumps({"durum": "hata", "mesaj": "client_id ve device_code parametreleri gerekli"}, ensure_ascii=False)
            
            device_code = refresh_token  # refresh_token parametresi device_code olarak kullanılır
            token_response = _token_al(client_id, device_code)
            
            if "hata" in token_response:
                if "authorization_pending" in str(token_response.get("hata", "")):
                    return json.dumps({
                        "durum": "beklemede",
                        "mesaj": "Kullanıcı henüz onaylamadı, lütfen bekleyin"
                    }, ensure_ascii=False)
                return json.dumps({
                    "durum": "hata",
                    "mesaj": f"Token alınamadı: {token_response['hata']}"
                }, ensure_ascii=False)
            
            return json.dumps({
                "durum": "basarili",
                "access_token": token_response.get("access_token", ""),
                "refresh_token": token_response.get("refresh_token", ""),
                "expires_in": token_response.get("expires_in", 3600),
                "scope": token_response.get("scope", "")
            }, ensure_ascii=False)

        elif islem == "token_yenile":
            if not client_id or not refresh_token:
                return json.dumps({"durum": "hata", "mesaj": "client_id ve refresh_token parametreleri gerekli"}, ensure_ascii=False)
            
            token_response = _token_yenile(client_id, refresh_token)
            
            if "hata" in token_response:
                return json.dumps({
                    "durum": "hata",
                    "mesaj": f"Token yenilenemedi: {token_response['hata']}"
                }, ensure_ascii=False)
            
            return json.dumps({
                "durum": "basarili",
                "access_token": token_response.get("access_token", ""),
                "refresh_token": token_response.get("refresh_token", refresh_token),
                "expires_in": token_response.get("expires_in", 3600)
            }, ensure_ascii=False)

        elif islem == "cikis_yap":
            return json.dumps({
                "durum": "basarili",
                "mesaj": "Oturum kapatıldı. Token'ları temizlemek için mcp_oauth.py kullanın."
            }, ensure_ascii=False)

        else:
            return json.dumps({"durum": "hata", "mesaj": f"bilinmeyen işlem: {islem}"}, ensure_ascii=False)

    except Exception as e:
        return json.dumps({"durum": "hata", "mesaj": str(e)}, ensure_ascii=False)


if __name__ == "__main__":
    print(run("giris_yap", "test-client-id"))
