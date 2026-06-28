# Görev: ReYMeN'in Öğrenme Sürecine Katkı

ReYMeN'in artık bir Reinforcement Learning (Pekiştirmeli Öğrenme) altyapısı var. Sistemin daha akıllı kararlar alabilmesi için senin (kullanıcının) geri bildirimlerin, sistemin "dijital nöronlarını" eğiten ödül sinyalleri işlevi görüyor.

## Senden beklenen disiplin:

1. **Doğal Etkileşim:** ReYMeN'i normal şekilde kullanmaya devam et. Arka planda `rl_skill_logger.py` her skill kullanımını `log_id` ile kayıt altına alıyor.

2. **Ödül Sinyallerini Kullan (Çok Kritik):**
   - **İşlem Başarılıysa:** Cevabının sonuna veya araya "Teşekkürler", "Tamamdır", "Oldu", "Harika", "Çözüldü" gibi olumlu kelimeler ekle. Sistem bunu **+1** ödül olarak puanlar.
   - **İşlem Hatalıysa:** Cevabına "Yanlış", "Hayır", "Bunu istemedim", "Anlamadın", "Tekrar yap" gibi ifadeler ekle. Sistem bunu **-1** ceza olarak puanlar.

3. **Çeşitlilik:** Farklı konularda sorgular sorarak (kod, siber, araştırma, analiz) sistemin hangi skill'in hangi durumda daha iyi performans gösterdiğini öğrenmesini sağla.

## Neden yapıyoruz?

Şu an "Gözlem Fazı"ndayız. Senin bu sinyallerin, ReYMeN'in bir sonraki aşamada Thompson Sampling algoritması ile kendi kararlarını kendi kendine optimize etmesini sağlayacak.

## Yönetici Notu (Geliştirici İçin)

- **Otomasyon:** `auto_reward()` fonksiyonu bu kelimeleri otomatik yakaladığı için ekstra bir şey yapmana gerek yok, sadece bu sinyalleri kullanmaya alışman yeterli.
- **İzleme:** Sistem şu an stabil, hiçbir hata/exception yok. Veri toplama devam ediyor.
- **Süreç:** Önümüzdeki birkaç gün içinde veri seti olgunlaştığında "MAB Motorunu" devreye alacağız.
