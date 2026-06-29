---
name: software-development_ai-fullstack-kodlamiyoruz_references_video-3-ten-kar-mlar-production-launch-ger-ek-d-nya
description: Video #3'ten Çıkarımlar — Production Launch & Gerçek Dünya
title: "Software Development Ai Fullstack Kodlamiyoruz References Video 3 Ten Kar Mlar Production Launch Ger Ek D Nya"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Video |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

## Video #3'ten Çıkarımlar — Production Launch & Gerçek Dünya

### Nihai İstatistikler
| Metrik | Değer |
|--------|-------|
| Toplam Kod | **~400.000 satır** |
| Toplam Süre | **3-4 hafta** |
| Toplam Issue | **~284+** (117 açık, 167 kapalı) |
| Manual Kod | **Sıfıra yakın** |
| Production URL | prototip.com (canlıda) |

### En Büyük Teknik Karar: Unified Post Model
HER ŞEYİN post olduğu tek tablo modeli. Comment, reply, repost, quote — hepsi aynı model.
- **Öncesi:** Ayrı tablolar → gündem hesaplama çalışmıyor, reply chain bozuk
- **Sonrası:** Tree yapısında posts, her şey aynı model
- AI bu refaktörü "kılçıksız" halletti. Bu en kritik karardı.

### Feed Algorithm (Production)
4 sekme:
1. **Yeniler** — kronolojik
2. **Trend** — algoritmik: engagement score × time decay × new account penalty
3. **Takip** — takip edilenler
4. **Sana Özel** — kişiselleştirilmiş (ortak araçlar, ortak tartışmalar, takip edilenlerin etkileşimi)

**Trend skoru formülü:**
```
ham_score = begeni_sayisi × (takipci_icerki_0.7 : dis_cevre_1.3)
zaman_cezasi = time_decay(post_yasi)
yeni_hesap_cezasi = (hesap < 7_gun) ? × 0.5 : × 1.0
final_score = ham_score × zaman_cezasi × yeni_hesap_cezasi
```

### AI ile Kör Geliştirme (Önemli Deney)
- **Kör mod:** Prompt ver, sonucu kontrol etmeden devam et → işe yarıyor
- **Full kontrol mod:** Her adımı izle, test et → daha kaliteli
- Projenin yarısı kör geliştirildi (çocukla ilgilenirken aralarda prompt gönderdi)
- AI "yorulmuyor" — uzun süreli kör geliştirmelerde bile tutarlı

### UI Detayları — AI'ın Zayıf Noktası
- 400K satırlık projede en çok zorlanılan kısım UI detayları
- Editör, thread çizgileri, görsel hizalama gibi konular
- **Çözüm:** Çizerek anlatmak. AI görsel talimatları iyi anlıyor.
- "400K satır yazdırdım o kadar uğraşmadım ama editör için gerçekten çizdim"

### Admin Panel — Kullanıcı Yönetimi (Production)
Her kullanıcı için:
- Post/beğeni/takipçi/DM/genel istatistikler
- R2 depolama kullanımı
- Kalite/güvenlik skoru
- Not yazma, işlem geçmişi
- Şifre sıfırlama, manuel onay

### Security & API
- API token yönetimi (kullanıcıya özel)
- Rate limiting
- E2E encryption (plan aşaması)

### PERFORMANCE
- SSR'ye geçilen sayfalar anında yükleniyor
- Lighthouse: Mobil 93, Desktop 86 (bazen 100)
- Accessibility: 100

### BONUS: Native iOS (Codex ile)
- Araç: Codex CLI ($200/ay)
- Dil: Swift (native, React Native değil)
- Status: Başlangıç aşaması, temel API entegrasyonu çalışıyor
- Web API kodlarını inceletti → iOS'a uyarladı

### Kapanış Dersi
> "Herkesin yapabileceğini iddia ediyorum ama herkesin bu seviyede yapabileceğini zannetmiyorum. Doğru soruyu kurabilmek, doğru iletişimi kurabilmek, onunla aynı düşünebilmek çok önemli."

Teknik bilgi + AI iletişim becerisi = production-ready ürün.
