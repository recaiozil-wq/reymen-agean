---
title: Tarayıcı Otomasyonu
description: Playwright ile web sayfası açma, tıklama, form doldurma
tags: [playwright, tarayici, web, otomasyon, scraping]
---

## Sayfa aç ve oku
BROWSER_HEADLESS "https://example.com"

## Screenshot al
BROWSER_SCREENSHOT "https://example.com" "ekran.png"

## JavaScript çalıştır
BROWSER_JS "https://example.com" "document.title"

## Form doldurma (Playwright ile)
PYTHON_CALISTIR "
from playwright.sync_api import sync_playwright
with sync_playwright() as pw:
    b = pw.chromium.launch(headless=True)
    p = b.new_page()
    p.goto('https://form-site.com')
    p.fill('#email', 'kullanici@email.com')
    p.fill('#password', 'sifre')
    p.click('#submit')
    p.wait_for_load_state('networkidle')
    print(p.title())
    b.close()
"

## Tablo verisi çek
PYTHON_CALISTIR "
from playwright.sync_api import sync_playwright
with sync_playwright() as pw:
    b = pw.chromium.launch(headless=True)
    p = b.new_page()
    p.goto('https://tablo-site.com')
    satirlar = p.query_selector_all('table tr')
    for satir in satirlar[:5]:
        hucreler = satir.query_selector_all('td')
        print([h.inner_text() for h in hucreler])
    b.close()
"
