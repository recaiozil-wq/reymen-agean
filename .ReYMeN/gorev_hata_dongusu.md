# Python Hata Döngüsü İnceleme

## NE
ReYMeN'in Python hata çözme döngüsünü incele, hata/eksik/iyleştirme öner.

## İNCELENECEK DOSYALAR
- reymen/core/ogrenme.py (SQLite hafıza, TTL, imza, doğrulama)
- reymen/cereyan/motor.py içindeki:
  - script_calistir() metodu
  - _llm_fix_iste() metodu
  - _fix_dogrula() metodu
  - ogren() metodu

## SORULAR
1. Hata imzası (imza_uret) yeterince sağlam mı?
2. TTL mantığı doğru çalışıyor mu?
3. Doğrulamalı kayıt yeterli mi?
4. 3 retry yeterli mi, backoff eklenmeli mi?
5. Concurrent write riski var mı?
6. SQLite WAL mode yeterli mi?
7. Hangi edge case'ler atlanmış?

## İSTENEN
- Kritik hata varsa DÜZELT
- İyileştirme önerilerini raporla
- Act modunda çalıştır
