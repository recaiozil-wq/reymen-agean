---
title: REST API Entegrasyonu
description: HTTP GET/POST istekleri, JSON parse, auth header kullanımı
tags: [api, rest, http, json, requests]
---

## GET isteği
PYTHON_CALISTIR "
import urllib.request, json
url = 'https://api.example.com/endpoint'
with urllib.request.urlopen(url, timeout=10) as r:
    veri = json.loads(r.read())
print(json.dumps(veri, indent=2, ensure_ascii=False)[:500])
"

## POST isteği (JSON body)
PYTHON_CALISTIR "
import urllib.request, json
url = 'https://api.example.com/create'
body = json.dumps({'ad': 'test', 'deger': 42}).encode()
req = urllib.request.Request(url, data=body,
    headers={'Content-Type': 'application/json',
             'Authorization': 'Bearer TOKEN'})
with urllib.request.urlopen(req, timeout=10) as r:
    print(json.loads(r.read()))
"

## API key ile kimlik doğrulama
PYTHON_CALISTIR "
import os, urllib.request, json
api_key = os.environ.get('API_KEY', '')
req = urllib.request.Request('https://api.example.com/me',
    headers={'X-API-Key': api_key})
with urllib.request.urlopen(req) as r:
    print(json.loads(r.read()))
"
