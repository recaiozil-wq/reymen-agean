---
title: GitHub Araştırma
description: GitHub API ile repo araştırma, README okuma, issue takibi
tags: [github, api, arastirma, kod]
---

## GitHub API ile repo bilgisi
PYTHON_CALISTIR "
import urllib.request, json
url = 'https://api.github.com/repos/microsoft/vscode'
with urllib.request.urlopen(url) as r:
    d = json.loads(r.read())
print(f'Stars: {d[\"stargazers_count\"]:,}')
print(f'Forks: {d[\"forks_count\"]:,}')
print(f'Açık issue: {d[\"open_issues_count\"]:,}')
"

## Repo README oku
PYTHON_CALISTIR "
import urllib.request, json, base64
url = 'https://api.github.com/repos/KULLANICI/REPO/readme'
with urllib.request.urlopen(url) as r:
    d = json.loads(r.read())
print(base64.b64decode(d['content']).decode('utf-8')[:1000])
"

## Repo ara
WEB_ARA "github.com python web scraping stars:>1000"
