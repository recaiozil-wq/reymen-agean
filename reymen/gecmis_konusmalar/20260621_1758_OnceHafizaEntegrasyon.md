# OnceHafiza Entegrasyonu
**Tarih:** 2026-06-21 17:30-18:00
**Konu:** ogrenmeler tablosuna guven_skoru/kategori/gecerlilik_tarihi ekleme, hafizada_ara() kategori filtresi + guven<0.5 belirsiz kontrolü, kaydet()'te otomatik guven hesaplama, Kali nmap testi

## Yapılanlar

### 1. DB Şeması (reymen/cereyan/once_hafiza.py — zaten vardı ✅)
- `guven_skoru FLOAT DEFAULT 1.0` — basari/(basari+hata)
- `kategori TEXT` — "kali", "dron", "cad", "windows", "kali/network/nmap" vb.
- `son_kullanim TEXT` — son okuma zamanı
- `gecerlilik_tarihi TEXT DEFAULT (date('now', '+180 days'))` — 6 ay
- Migration: ALTER TABLE ile eski DB'ye kolon ekleme

### 2. hafizada_ara() / ara() (zaten vardı ✅)
- `kategori` parametresi → SQL WHERE ile filtrele
- `min_guven` parametresi → guven_skoru >= min_guven
- `gecerli_mi` parametresi → gecerlilik_tarihi >= date('now')
- `durum` alanı: "guvenilir" (>=0.5) / "belirsiz" (<0.5)

### 3. kaydet() (zaten vardı ✅)
- guven_skoru otomatik: basari_sayisi/(basari_sayisi+hata_sayisi)
- gecerlilik_tarihi = bugün + 180 gün
- kategori parametresi

### 4. Sistem/ sınıfına da eklendi
- `reymen/sistem/once_hafiza.py` — class OnceHafiza
- hafizada_ara(): kategori filtresi + guven<0.5 → "belirsiz" döndür
- kaydet(): guven_skoru hesapla, gecerlilik_tarihi = +6 ay
- hata_kaydet(): ogrenmeler.hata_sayisi++ + guven_skoru güncelle
- isle(): kategori parametresini hafizada_ara()/kaydet()'e passthrough

### 5. Kali Nmap Testi ✅
```bash
nmap -sV -sT -p 1-1000 127.0.0.1
```
- Port 135/tcp: msrpc (Microsoft Windows RPC)
- Port 445/tcp: microsoft-ds
- OS: Windows
- Kaydedildi: kali/network/nmap kategorisinde

### 6. Hermes YOLO Modu
- Hermes'te YOLO modu terminal onayını kaldırır ama secret redaction + Tirith güvenlik politikası + tool loop koruması çalışmaya devam eder
- Tam yetki için: approvals.mode: off + tirith_enabled: false

## Hafızaya Kaydedilenler
| Kategori | Hedef | İçerik | Güven |
|----------|-------|--------|-------|
| kali/network/nmap | localhost_port_taramasi_sV | Port 135/445, OS: Windows | 1.0 |
| kali/network/nmap/skills | nmap_servis_versiyon_tespiti | -sV flag'leri | 1.0 |

## Kararlar
1. **reymen/cereyan/once_hafiza.py** kanonik kaynak — zaten tüm özelliklere sahipti
2. **reymen/sistem/once_hafiza.py** class wrapper — agent'a entegre edilecek
3. Kategori hiyerarşisi: "kali/network/nmap" gibi slash'li yapı
4. Guven esigi: < 0.5 = "belirsiz", >= 0.5 = "guvenilir"
5. Gecerlilik: 180 gün, eski kayitlar guven < 0.8 ise temizlenir
