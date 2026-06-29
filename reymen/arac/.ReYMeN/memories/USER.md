# ReYMeN Kullanıcı Profili — USER.md

## İletişim Tarzı
- Çok kısa direkt komutlar ("Yap", "Kontrol et", "Ok", "Dur")
- Türkçe konuşur, İngilizce cevap istemez
- Açıklama/dekorasyon istemez, direkt sonuç
- Tablo + emoji + kısa öz formatını tercih eder
- Hata durumunda "Olmadi hata devam etme" (direkt durdur)
- "Hey" = dikkat çekme, "salak" = sinirli/hata uyarısı
- Sessiz onay: soru sorunca 3dk bekle, cevap yoksa onay say

## Teknik Bilgiler
- ReYMeN Agent proje sahibi (Hermes fork'u)
- GitHub: asdafgf (Watcher-Hermes organizasyonu)
- Python bilgisi ileri seviye
- Windows 10 kullanıcısı
- Kali Linux VM kullanıyor (192.168.56.103)
- VS Code + Cline (GLM 5.2) ikincil kodlama aracı
- DeepSeek API birincil provider
- 3 Telegram botu yönetiyor

## Proje Tercihleri
- ReYMeN-Ajan projesi: C:\Users\marko\Desktop\Reymen Proje\ReYMeN-Ajan
- Türkçe dokümantasyon öncelikli
- Açık kaynak (MIT lisansı)
- GitHub'da Watcher-Hermes organizasyonu altında
- Kod kalitesi: shell=True yasak, except:pass yasak, CLI < 2000 satır
- Batch fix'ler Python script'i ile yapılır (manuel edit yasak)
- Cline kod çalıştırıcı, Hermes planlayıcı/yönetici

## Karar Mekanizması
- Pragmatik: fayda yoksa yapma
- ÖNCE/SONRA metrikleri ister
- Hata durumunda 3 deneme sonra raporla
- Belirsiz görevde tahminle devam et (soru sorma)
