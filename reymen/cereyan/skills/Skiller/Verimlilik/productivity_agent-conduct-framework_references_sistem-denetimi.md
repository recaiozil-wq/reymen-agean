
> **Kategori:** Verimlilik

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Productivity_Agent Conduct Framework_References_Sistem Denetimi |
| **Nerede?** | Verimlilik/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# Sistem Denetimi: 13 Hata (5 Kategoride)

## K1 — Tetikleyici Hataları
| # | Hata | Çözüm |
|:-:|:-----|:------|
| 1A | T4 sadece tarihe bakar, tool versiyonunu kontrol etmez | `tool_version TEXT` kolonu ekle |
| 1B | T2 (guven<0.5) hiç ateşlenmez — tüm kayıtlar >=0.5 | `isle()` hata durumunda ogrenmeler.hata_sayisi++ |
| 1C | T3 (hata>=2) çalışmaz — hiç kayıtta hata>=2 yok | Retry sistemi eklenmeli |

## K2 — Puanlama Hataları
| # | Hata | Çözüm |
|:-:|:-----|:------|
| 2A | Puan kriterleri sabit, göreve göre değişmez | Kategori bazlı ağırlık: security→guvenlik(%40) |
| 2B | Puanlama kodu yok (AGENTS.md'de yazılı, kodlanmamış) | `_puanla()` fonksiyonu yaz |

## K3 — Hafıza Hataları
| # | Hata | Çözüm |
|:-:|:-----|:------|
| 3A | `kaynak_url` kolonu yok (URL'ler içeriğe gömülü) | ✅ Düzeltildi: kolon + migration eklendi |
| 3B | %90.7 kayıt guven=1.0 (42'si tek denemeli) | ✅ Düzeltildi: `_kademeli_guven()` sigmoid |
| 3C | Eski/kullanılmayan kayıt temizlenmez | Haftalık cron: guven<0.5 + gecerlilik>30gün → sil |

## K4 — Ajan İletişim Hataları
| # | Hata | Çözüm |
|:-:|:-----|:------|
| 4A | Cross-agent kodu yok (AGENTS.md'de protokol yazılı) | `_inter_agent_queue` + heartbeat |
| 4B | Timeout yok — ajan çökerse diğeri beklemez | ACK_TIMEOUT=30sn, retry 3 |
| 4C | Mesaj kaybı — gönderildi mi kontrolü yok | message_id UUID + requires_ack |

## K5 — Öğrenme Döngüsü Hataları
| # | Hata | Çözüm |
|:-:|:-----|:------|
| 5A | Zehirli hafıza — web'den yanlış kaynak guven=1.0 alır | Kaynak güven ağırlığı: islem_guven * kaynak_guven |
| 5B | 1 başarı = guven 1.0 çok yüksek | ✅ Düzeltildi: `_kademeli_guven()` → ilk başarı 0.5 |

## En Kritik 3
1. %90 kayıt guven=1.0 (şişirilmiş) → ✅ Sigmoid düzeltildi
2. Cross-agent kodu yok → Kod bekliyor
3. Puanlama kodu yok → Kod bekliyor
