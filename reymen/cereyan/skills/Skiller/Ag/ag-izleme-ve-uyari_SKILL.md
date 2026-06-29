--- 
title: Ağ İzleme ve Uyarı Sistemi
name: ag-izleme-ve-uyari
description: Ağ trafiğini izler, anomali tespit eder ve güvenlik uyarıları üretir
tags: [ag, izleme, uyari, trafik, anomaly, sniffer]
---

# Ağ İzleme ve Uyarı Sistemi

| 5N1K | Açıklama |
|------|----------|
| Kim | ReYMeN bot kullanıcıları |
| Ne | Ağ trafiğini gerçek zamanlı izler, anomali ve şüpheli aktiviteleri tespit ederek uyarı üretir |
| Nerede | reymen/cereyan/skills/Skiller/Ag/ |
| Ne Zaman | Ağ güvenliği, trafik analizi veya performans izleme gerektiğinde |
| Neden | Anomali tespiti yapılmazsa saldırılar fark edilmeden devam edebilir |
| Nasıl | tcpdump/tshark ile paket yakalama, desen eşleştirme ve threshold kontrolleri ile yapılır |

## İzleme Metrikleri

| Metrik | Normal Eşik | Uyarı Eşiği | Kritik Eşik |
|--------|-------------|-------------|-------------|
| Bağlantı/sn | <100 | 100-500 | >500 |
| Bant genişliği | <%30 | %30-70 | >%70 |
| SYN paketi/sn | <50 | 50-200 | >200 |
| Farklı IP/sn | <20 | 20-50 | >50 |

## Tespit Edilen Anomaliler

| Anomali | Desen | Aksiyon |
|---------|-------|---------|
| Port tarama | Aynı IP'den farklı portlara SYN | IP'yi blokla |
|DoS saldırısı | Tek hedefe yüksek SYN | Rate limit uygula |
| DNS tunneling | Anormal büyüklükte DNS sorguları | Sorguyu logla, analiz et |
| ARP spoofing | MAC adresi çakışması | Static ARP ekle |

## Raporlama

- Uyarılar `ag/izleme/uyari` kategorisine kaydedilir
- Kritik uyarılarda kullanıcıya anlık bildirim gönderilir
- Haftalık trafik özeti otomatik oluşturulur
