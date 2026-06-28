#!/bin/bash
# Eski kayit temizleme cron - her gun 04:00'te calisir
DB="reymen/cereyan/.ReYMeN/ogrenmeler.db"

echo "=== Kayit Temizlik $(date) ==="

# 1. Gecerlilik tarihi gecmis kayitlari sil
SILINEN=$(sqlite3 "$DB" "DELETE FROM ogrenmeler WHERE gecerlilik_tarihi < date('now');" 2>&1)
echo "Tarihi gecmis: $(sqlite3 "$DB" "SELECT changes();") kayit silindi"

# 2. Guven skoru < 0.2 VE hata_sayisi > 5 olan kayitlari sil
SILINEN2=$(sqlite3 "$DB" "DELETE FROM ogrenmeler WHERE guven_skoru < 0.2 AND hata_sayisi > 5;" 2>&1)
echo "Dusuk guven: $(sqlite3 "$DB" "SELECT changes();") kayit silindi"

# 3. 6 aydir kullanilmayan kayitlari sil (son_kullanim > 180 gun)
SILINEN3=$(sqlite3 "$DB" "DELETE FROM ogrenmeler WHERE son_kullanim < date('now', '-180 days');" 2>&1)
echo "Kullanilmayan: $(sqlite3 "$DB" "SELECT changes();") kayit silindi"

# 4. ajan_mesaj tablosunda 7 gunden eski mesajlari temizle
sqlite3 "$DB" "DELETE FROM ajan_mesaj WHERE olusturulma < datetime('now', '-7 days');" 2>&1
echo "Eski mesaj: $(sqlite3 "$DB" "SELECT changes();") mesaj silindi"

# 5. Kalan kayit sayisi
KALAN=$(sqlite3 "$DB" "SELECT COUNT(*) FROM ogrenmeler;")
echo "Kalan kayit: $KALAN"

echo "=== Tamam ==="
