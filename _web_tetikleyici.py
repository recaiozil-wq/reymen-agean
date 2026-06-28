"""
WEB TETIKLEYICI SISTEMI — 5 Tetikleyici + Test
"""
import sqlite3
from datetime import datetime, date, timedelta
import logging
logger = logging.getLogger(__name__)

DB = 'reymen/cereyan/.ReYMeN/ogrenmeler.db'

# ── VERITABANI KURULUMU ───────────────────────────────────
def db_kur():
    con = sqlite3.connect(DB)
    con.execute("PRAGMA journal_mode=WAL")
    # web_arama_sebebi kolonunu ekle (varsa hata yut)
    try:
        con.execute("ALTER TABLE ogrenmeler ADD COLUMN web_arama_sebebi TEXT DEFAULT ''")
        con.commit()
        print("✅ web_arama_sebebi kolonu eklendi")
    except sqlite3.OperationalError:
        print("⚠️ web_arama_sebebi zaten var")
    con.close()

# ── TETIKLEYICI FONKSIYONLARI ────────────────────────────

def tetikleyici_1_hafiza_bos(hedef):
    """Hafizada kayit yoksa -> direkt web."""
    con = sqlite3.connect(DB)
    var = con.execute(
        "SELECT COUNT(*) FROM ogrenmeler WHERE hedef LIKE ? LIMIT 1",
        (f"%{hedef[:30]}%",)
    ).fetchone()[0]
    con.close()
    if var == 0:
        return (True, "T1: Hafiza bos", 1.0)
    return (False, "", 0)

def tetikleyici_2_guven_dusuk(hedef):
    """guven_skoru < 0.5 -> web'den dogrula."""
    con = sqlite3.connect(DB)
    row = con.execute(
        "SELECT guven_skoru FROM ogrenmeler WHERE hedef LIKE ? ORDER BY guven_skoru ASC LIMIT 1",
        (f"%{hedef[:30]}%",)
    ).fetchone()
    con.close()
    if row and row[0] < 0.5:
        return (True, f"T2: Guven dusuk ({row[0]:.2f})", row[0])
    return (False, "", 0)

def tetikleyici_3_gorev_basarisiz(hata_sayisi):
    """2+ hata -> web'e git."""
    if hata_sayisi >= 2:
        return (True, f"T3: {hata_sayisi} hata", hata_sayisi / 10)
    return (False, "", 0)

def tetikleyici_4_gecerlilik_asmis(hedef):
    """gecerlilik_tarihi < bugun -> web'ten tazele."""
    con = sqlite3.connect(DB)
    bugun = date.today().isoformat()
    row = con.execute(
        "SELECT gecerlilik_tarihi, guven_skoru FROM ogrenmeler WHERE hedef LIKE ? AND gecerlilik_tarihi < ? LIMIT 1",
        (f"%{hedef[:30]}%", bugun)
    ).fetchone()
    con.close()
    if row:
        return (True, f"T4: Gecerlilik asmis (tarih={row[0]}, guven={row[1]})", 0.3)
    return (False, "", 0)

def tetikleyici_5_celiski(hafiza_icerik, video_icerik):
    """Iki kaynak farkli sey soyluyor -> web hakem."""
    if hafiza_icerik and video_icerik and hafiza_icerik != video_icerik:
        return (True, "T5: Celiski - iki kaynak farkli", 0.6)
    return (False, "", 0)

# ── ANA KARAR FONKSIYONU ─────────────────────────────────

def web_gerekli_mi(hedef, hata_sayisi=0, hafiza_icerik="", video_icerik=""):
    """
    5 tetikleyiciyi sirayla kontrol et.
    Ilk ateslenen kazanir.
    """
    tetikleyiciler = [
        ("T1: Hafiza bos",     tetikleyici_1_hafiza_bos(hedef)),
        ("T3: Gorev basarisiz", tetikleyici_3_gorev_basarisiz(hata_sayisi)),
        ("T2: Guven dusuk",    tetikleyici_2_guven_dusuk(hedef)),
        ("T4: Gecerlilik asmis", tetikleyici_4_gecerlilik_asmis(hedef)),
        ("T5: Celiski",        tetikleyici_5_celiski(hafiza_icerik, video_icerik)),
    ]
    
    # Sirala: once yuksek puanli tetikleyiciler
    tetikleyiciler.sort(key=lambda t: -t[1][2])  # puana gore sirala
    
    for ad, (ateslendi, sebep, puan) in tetikleyiciler:
        if ateslendi:
            return (True, sebep, puan)
    
    return (False, "Web gerekmiyor", 1.0)

# ── TEST: 5 Senaryo ───────────────────────────────────────

print("=" * 70)
print("WEB TETIKLEYICI SISTEMI — 5 Senaryo Testi")
print("=" * 70)

# Once DB'yi kur
db_kur()

print(f"\n{'SENARYO':40s} {'ATESLENDI?':15s} {'SEBEP':40s} {'PUAN':>5s}")
print("-" * 100)

senaryolar = [
    # (hedef, hata_sayisi, hafiza_icerik, video_icerik)
    ("selam_merhaba_test",     0, "",            ""),  # T1: Hafiza bos
    ("nmap_port_tarama_test",  3, "",            ""),  # T3: 3 hata (eski kayit var ama hata cok)
    ("python_nmap_video_ogrenme", 0, "yavas yontem", "hizli yontem"),  # T5: Celiski
]

for hedef, hata, h_icerik, v_icerik in senaryolar:
    ateslendi, sebep, puan = web_gerekli_mi(hedef, hata, h_icerik, v_icerik)
    
    # Senaryo adini formatla
    senaryo_adi = f"{hedef[:35]:35s} (hata={hata})"
    
    durum = "✅ ATESLENDI" if ateslendi else "❌ GEREKMIYOR"
    print(f"{senaryo_adi:40s} {durum:15s} {sebep:40s} {puan:>5.2f}")

print("\n" + "=" * 70)
print("5 TETIKLEYICI SIRALAMASI (Oncelik sirasiyla)")
print("=" * 70)
print("""
| # | Tetikleyici | Kosul | Puan | Ne Zaman? |
|:-:|:------------|:------|:----|:----------|
| 1 | T1: Hafiza bos | COUNT=0 | 1.0 | Yeni tool/kategori hic bilinmiyor |
| 2 | T3: Gorev basarisiz | hata >= 2 | 0.8 | 2. hatadan sonra web'de cozum ara |
| 3 | T2: Guven dusuk | guven < 0.5 | 0.5-0.3 | 1 basari 3 hata = guven 0.25 |
| 4 | T4: Gecerlilik asmis | tarih < bugun | 0.3 | 6+ ay once ogrenilmis bilgi |
| 5 | T5: Celiski | icerik1 != icerik2 | 0.6-0.4 | Video/Kullanici farkli soyluyor |
""")

# Detayli test
print("=" * 70)
print("DETAYLI TEST — Her Senaryo Ayri Ayri")
print("=" * 70)

# SENARYO 1: Hafiza bos
print("\n[TEST 1] T1: Hafiza bos")
print("  Hedef: 'selam_merhaba_test' (hic kayit yok)")
ates, sebep, puan = tetikleyici_1_hafiza_bos("selam_merhaba_test")
print(f"  {'✅ ATESLENDI' if ates else '❌ ATESLENMEDI'} -> {sebep}")

# SENARYO 2: Guven dusuk
print("\n[TEST 2] T2: Guven dusuk")
print("  Hedef: 'bilinmeyen_hata_test' (yok, gormez)")
ates, sebep, puan = tetikleyici_2_guven_dusuk("bilinmeyen_hata_test")
print(f"  {'✅ ATESLENDI' if ates else '❌ ATESLENMEDI'} -> {sebep}")

# SENARYO 3: Gorev basarisiz
print("\n[TEST 3] T3: Gorev basarisiz (3 hata)")
ates, sebep, puan = tetikleyici_3_gorev_basarisiz(3)
print(f"  {'✅ ATESLENDI' if ates else '❌ ATESLENMEDI'} -> {sebep}")

# SENARYO 4: Gecerlilik asmis
print("\n[TEST 4] T4: Gecerlilik asmis")
print("  Hedef: 'nmap_port_tarama_test' (ID=12, gecerlilik=2026-12-18)")
ates, sebep, puan = tetikleyici_4_gecerlilik_asmis("nmap_port_tarama_test")
print(f"  {'✅ ATESLENDI' if ates else '❌ ATESLENMEDI'} -> {sebep}")

# SENARYO 5: Celiski
print("\n[TEST 5] T5: Celiski")
ates, sebep, puan = tetikleyici_5_celiski("UDP yavas", "UDP hizli")
print(f"  {'✅ ATESLENDI' if ates else '❌ ATESLENMEDI'} -> {sebep}")

# Tum ayni anda
print("\n" + "=" * 70)
print("TOP LU TEST — Tum tetikleyiciler ayni anda")
print("=" * 70)
for hedef, hata, h_icerik, v_icerik in [
    ("selam_merhaba_test",     0, "",            ""),
    ("nmap_port_tarama_test",  3, "",            ""),
    ("python_nmap_video_ogrenme", 0, "yavas yontem", "hizli yontem"),
    ("yeni_tool_bilinmiyor",   2, "",            "farkli_yontem"),
]:
    ateslendi, sebep, puan = web_gerekli_mi(hedef, hata, h_icerik, v_icerik)
    durum = "✅ WEB" if ateslendi else "❌ HAFIZA"
    print(f"  {hedef:40s} {durum:10s} | {sebep:40s} | puan={puan:.2f}")
