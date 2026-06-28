---
title: Python Veri Analizi
description: CSV, Excel okuma, pandas kullanımı, istatistik hesaplama
tags: [python, veri, pandas, csv, analiz]
---

## CSV oku (pandas olmadan)
PYTHON_CALISTIR "
import csv
with open('veri.csv', newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for i, row in enumerate(reader):
        print(row)
        if i >= 4: break
"

## Pandas ile analiz
PYTHON_CALISTIR "
import pandas as pd
df = pd.read_csv('veri.csv')
print(df.describe())
print(f'Satır: {len(df)}, Sütun: {len(df.columns)}')
print(df.head())
"

## Temel istatistik (pandas olmadan)
PYTHON_CALISTIR "
sayilar = [10, 20, 30, 40, 50]
ort = sum(sayilar) / len(sayilar)
print(f'Ortalama: {ort}, Min: {min(sayilar)}, Max: {max(sayilar)}')
"

## Excel oku
PYTHON_CALISTIR "
import openpyxl
wb = openpyxl.load_workbook('belge.xlsx')
ws = wb.active
for row in ws.iter_rows(max_row=5, values_only=True):
    print(row)
"
