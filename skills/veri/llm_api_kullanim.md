---
title: LM Studio / OpenAI API Kullanımı
description: Yerel LLM veya OpenAI API çağrıları, prompt mühendisliği
tags: [llm, openai, lmstudio, api, prompt]
---

## LM Studio ile yerel LLM çağrısı
PYTHON_CALISTIR "
import urllib.request, json
veri = json.dumps({
    'model': 'cognitivecomputations.dolphin3.0-llama3.1-8b',
    'messages': [{'role': 'user', 'content': 'Merhaba, nasılsın?'}],
    'temperature': 0.7,
    'max_tokens': 200
}).encode()
req = urllib.request.Request('http://localhost:1234/v1/chat/completions',
    data=veri, headers={'Content-Type': 'application/json'})
with urllib.request.urlopen(req, timeout=30) as r:
    cevap = json.loads(r.read())
print(cevap['choices'][0]['message']['content'])
"

## Mevcut modelleri listele
PYTHON_CALISTIR "
import urllib.request, json
with urllib.request.urlopen('http://localhost:1234/v1/models', timeout=5) as r:
    for m in json.loads(r.read())['data']:
        print(m['id'])
"

## Sistem prompt ile kullan
PYTHON_CALISTIR "
import urllib.request, json
mesajlar = [
    {'role': 'system', 'content': 'Sen yardımcı bir asistansın.'},
    {'role': 'user', 'content': 'Python nedir?'}
]
veri = json.dumps({'model': 'auto', 'messages': mesajlar}).encode()
req = urllib.request.Request('http://localhost:1234/v1/chat/completions',
    data=veri, headers={'Content-Type': 'application/json'})
with urllib.request.urlopen(req, timeout=30) as r:
    print(json.loads(r.read())['choices'][0]['message']['content'])
"
