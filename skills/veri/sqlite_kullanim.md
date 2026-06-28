---
title: SQLite Veritabanı
description: SQLite ile tablo oluşturma, veri ekleme, sorgulama
tags: [sqlite, veritabani, sql, python]
---

## Bağlantı ve tablo oluştur
PYTHON_CALISTIR "
import sqlite3
con = sqlite3.connect('veri.db')
con.execute('CREATE TABLE IF NOT EXISTS kayitlar (id INTEGER PRIMARY KEY, ad TEXT, tarih TEXT)')
con.commit()
print('Tablo hazır')
"

## Veri ekle
PYTHON_CALISTIR "
import sqlite3
from datetime import datetime
con = sqlite3.connect('veri.db')
con.execute('INSERT INTO kayitlar (ad, tarih) VALUES (?,?)', ('Test', datetime.now().isoformat()))
con.commit()
print(f'{con.total_changes} satır eklendi')
"

## Sorgula
PYTHON_CALISTIR "
import sqlite3
con = sqlite3.connect('veri.db')
for row in con.execute('SELECT * FROM kayitlar ORDER BY id DESC LIMIT 10'):
    print(row)
"

## FTS5 ile tam metin arama
PYTHON_CALISTIR "
import sqlite3
con = sqlite3.connect(':memory:')
con.execute('CREATE VIRTUAL TABLE icerik USING fts5(baslik, metin)')
con.execute('INSERT INTO icerik VALUES (?,?)', ('Python Rehberi', 'asyncio coroutine await'))
for row in con.execute(\"SELECT * FROM icerik WHERE icerik MATCH 'asyncio'\"):
    print(row)
"
