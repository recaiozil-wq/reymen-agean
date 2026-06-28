---
title: Ekran Otomasyonu
description: pyautogui ile mouse/klavye kontrolü, ekran görüntüsü
tags: [otomasyon, pyautogui, mouse, klavye, ekran]
---

## Fare tıklama
PYTHON_CALISTIR "
import pyautogui, time
time.sleep(2)  # hazırlan
pyautogui.click(500, 400)  # x, y koordinatı
print('Tıklandı')
"

## Metin yaz
PYTHON_CALISTIR "
import pyautogui, time
time.sleep(1)
pyautogui.typewrite('Merhaba!', interval=0.05)
"

## Ekran görüntüsü al
PYTHON_CALISTIR "
import pyautogui
img = pyautogui.screenshot()
img.save('ekran.png')
print('Ekran görüntüsü kaydedildi: ekran.png')
"

## Belirli rengi bul
PYTHON_CALISTIR "
import pyautogui
# Ekranda kırmızı pixel ara
pixel = pyautogui.pixel(100, 100)
print(f'Pixel rengi (100,100): {pixel}')
"

## Güvenli mod: fail-safe
PYTHON_CALISTIR "
import pyautogui
pyautogui.FAILSAFE = True  # Köşeye götürünce dur
pyautogui.PAUSE = 0.5      # Her işlem arası 0.5s
print('Güvenli mod aktif')
"
