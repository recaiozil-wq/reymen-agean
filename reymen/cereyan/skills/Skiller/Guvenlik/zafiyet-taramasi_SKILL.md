--- 
title: Zafiyet Tarama Asistanı
name: zafiyet-taramasi
description: Sistemlerde ve ağlarda güvenlik açıklarını tespit eder, raporlar ve çözüm önerir
tags: [guvenlik, zafiyet, tarama, nmap, pentest]
---

# Zafiyet Tarama Asistanı

| 5N1K | Açıklama |
|------|----------|
| Kim | ReYMeN bot kullanıcıları |
| Ne | Hedef sistemlerde açık portları, zafiyetleri ve yanlış yapılandırmaları tespit eder |
| Nerede | reymen/cereyan/skills/Skiller/Guvenlik/ |
| Ne Zaman | Güvenlik denetimi, pentest veya rutin tarama gerektiğinde |
| Neden | Açık portlar ve zafiyetler tespit edilmeden güvenli bir sistem kurulamaz |
| Nasıl | nmap ile port tarama + CVE veritabanı sorgulama + raporlama ile yapılır |

## Tarama Seviyeleri

| Seviye | Kapsam | Süre | nmap Komutu |
|--------|--------|------|-------------|
| Hızlı | İlk 1000 port | ~30sn | `nmap -T4 -F <hedef>` |
| Standart | Tüm TCP portları | ~5dk | `nmap -sS -sV -T4 <hedef>` |
| Derin | TCP+UDP+OS tespiti | ~15dk | `nmap -sS -sU -sV -O -T4 <hedef>` |
| Full | Tümü + script | ~30dk | `nmap -sS -sU -sV -O -A -T4 <hedef>` |

## Rapor Formatı

| Alan | Açıklama |
|------|----------|
| Hedef IP | Taranan sistem |
| Açık Portlar | Port numarası + servis + versiyon |
| Zafiyetler | CVE ID + CVSS skoru + açıklama |
| Öneri | Kapatma, güncelleme veya yapılandırma değişikliği |

## Güvenlik

- Yalnızca yetkili olduğunuz sistemleri tarayın
- Tüm tarama sonuçları `guvenlik/tarama/` kategorisinde şifrelenmiş olarak saklanır
- Tarama logları 30 gün sonra otomatik temizlenir
