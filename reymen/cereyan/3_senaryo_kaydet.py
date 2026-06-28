#!/usr/bin/env python3
"""3 Senaryo için hata tespit sürecini OnceHafiza'ya kaydet"""
import sys
sys.path.insert(0, r"C:\Users\marko\Desktop\Reymen Proje\hermes_projesi")
from reymen.cereyan.once_hafiza import kaydet, ara

# SENARYO 1 — Kod Hatası Düzeltme Süreci
kaydet(
    hedef="hata_tespit_kod_duzeltme_sureci",
    kategori="video/learning",
    icerik="""SENARYO 1 — Kod Hatasi Duzeltme Sureci:

1) TESPIT: Video'daki kodu hafizadaki dogru bilgiyle karsilastir
2) ANALIZ: Farki belirle (ornek: nm.scan 2.parametre vs ports=)
3) DUZELT: Dogru kodu yaz
4) DOGRULA:
   a) Sandbox'ta calistir (terminal)
   b) Cikti beklendigi gibi mi?
   c) Calismazsa: 3 retry (3 farkli alternatif dene)
   d) Hala calismazsa: circuit breaker + kullaniciya bildir
5) BASARILI: kaydet(..., basari=True) -> guven artar
6) BASARISIZ: kaydet(..., basari=False) -> guven duser
   Kullaniciya: "[HATA]. 3 denemede cozulemedi. Ne yapmami istersin?"
7) SONUC: Skill'e dogru+yanlis versiyonlari ekle""",
    basari=True,
)
print("✅ SENARYO 1 kaydedildi")

# SENARYO 2 — Çelişkili Bilgi Süreci
kaydet(
    hedef="hata_tespit_celiski_cozme_sureci",
    kategori="video/learning",
    icerik="""SENARYO 2 — Celiskili Bilgi Cozme Sureci:

1) TESPIT: Hafizada eski bilgi var, video farkli gosteriyor
2) KARSILASTIR: Ikisini de hafizaya cek
   a) Eski: ID=X guven=Y basari_sayisi=Z
   b) Video: yeni bilgi (guven=1.0 yeni)
3) DOGRULA (3 kaynak):
   a) Web: PyPI/github/doc sayfasindan dogrula
   b) OnceHafiza: guven_skoru karsilastir
   c) Test: Sandbox'ta ikisini de calistir
4) KARAR KRITERI (siralama):
   - Web kaynagi > hafiza (web en guncel)
   - guven_skoru > 0.8 VE basari_sayisi > 3 ise eski guvenilir
   - Test sonucu: hangisi calisiyorsa o dogru
5) YANLIS OLANI ISARETLE:
   eski_kayit = ara(eski_hedef, ...)
   kaydet(eski_hedef + "_YANLIS", kategori, icerik="ESKI/YANLIS", basari=False)
   -> guven_skoru duser, bir daha kullanilmaz
6) DOGRU OLANI KAYDET:
   kaydet(yeni_hedef, kategori, icerik, basari=True)
7) SKILL GUNCELLE:
   - Her iki versiyonu da skill'e ekle (hangisi dogru etiketiyle)""",
    basari=True,
)
print("✅ SENARYO 2 kaydedildi")

# SENARYO 3 — Bilinmeyen Hata Süreci
kaydet(
    hedef="hata_tespit_bilinmeyen_hata_sureci",
    kategori="video/learning",
    icerik="""SENARYO 3 — Bilinmeyen Hata Sureci:

1) TESPIT: Hata bulundu ama anlasilamadi
2) HAFIZA KONTROL:
   ara(hedef='hata_mesajinin_kelime_parcalari', min_guven=0.3)
   -> Bulunamadi (None) -> devam
3) WEB KONTROL (3 farkli kaynak):
   a) Resmi dokumantasyon (PyPI, npm, github)
   b) StackOverflow / GitHub Issues
   c) LLM yorumu (en son care)
   Her kaynak->farkli cozum->max 3 deneme
4) MAX DENEME: 3 (her denemede farkli yaklasim)
5) 3 DENEMEDE BULUNAMAZSA:
   - circuit breaker (3 basarisiz -> kalici dur)
   - Kullaniciya bildir:
     "Su hatayi cozemedim: [HATA]. Ne yapmami istersin?"
   - Bekle (diger gorevler devam edebilir)
6) KULLANICI CEVAP VERINCE:
   - Verilen cozumu hafizaya kaydet
   - kaydet(hedef='cozum_KULLANICININ_COZUMU', kategori='video/learning', basari=True)
7) GUNCELLEME:
   - Session_search ile sonraki benzer hatada getir
   - Cozum basarili oldukca guven_skoru yukselir
   - Skill'e ekle: 'kullanici_cozumu' etiketiyle""",
    basari=True,
)
print("✅ SENARYO 3 kaydedildi")

# Dogrula
print("\n=== DOGRULAMA ===")
for h in ["hata_tespit_kod_duzeltme_sureci", "hata_tespit_celiski_cozme_sureci", "hata_tespit_bilinmeyen_hata_sureci"]:
    r = ara(h, kategori="video/learning", min_guven=0.0)
    if r:
        print(f"  ✅ {h}: ID={r[0]['id']} guven={r[0]['guven_skoru']}")
    else:
        print(f"  ❌ {h}: bulunamadi")
