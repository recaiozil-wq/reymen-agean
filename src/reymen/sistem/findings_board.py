# -*- coding: utf-8 -*-
"""
findings_board.py â€” Ortak bulgu panosu (SQLite WAL modu)

3 profil (default/pasa_38, reymen, kiral38) ortak kullanimi icin.
SQLite WAL modu + busy_timeout ile eszamanli yazma guvenligi.

Kullanim:
    from reymen.sistem.findings_board import ekle_bulgu, bulgu_listele, bulgu_guncelle

    # Yeni bulgu ekle
    ekle_bulgu(bulan="reymen", konu="DB cogalmasi", onem="kritik")

    # Bulgulari listele
    bulgu_listele(durum="beklemede")

    # Bulgu guncelle
    bulgu_guncelle(bulgu_id=1, durum="duzeltildi", duzelten="kiral38")

    # Ozet
    bulgu_ozet()
"""

import sqlite3
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# â”€â”€ Sabitler â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

_PROJE_KOK = Path(__file__).resolve().parent.parent.parent.parent
_BOARD_DB = _PROJE_KOK / "shared_state" / "findings_board.db"

_KURULUM_SQL = """
CREATE TABLE IF NOT EXISTS findings (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    bulan_profil    TEXT NOT NULL,
    tarih           TEXT NOT NULL,
    konu            TEXT NOT NULL,
    dosya_yolu      TEXT DEFAULT '',
    onem_derecesi   TEXT NOT NULL CHECK(onem_derecesi IN ('kritik','orta','dusuk')),
    durum           TEXT NOT NULL DEFAULT 'yeni'
                    CHECK(durum IN ('yeni','inceleniyor','duzeltildi','reddedildi','beklemede')),
    aciklama        TEXT DEFAULT '',
    duzelten_profil TEXT DEFAULT '',
    dogrulayan_profil TEXT DEFAULT '',
    guncelleme_tarihi TEXT DEFAULT '',
    UNIQUE(konu, bulan_profil)
);
"""

_INDEX_SQL = """
CREATE INDEX IF NOT EXISTS idx_findings_durum ON findings(durum);
CREATE INDEX IF NOT EXISTS idx_findings_onem ON findings(onem_derecesi);
CREATE INDEX IF NOT EXISTS idx_findings_bulan ON findings(bulan_profil);
"""


# â”€â”€ Veritabani baglantisi â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


def _baglan() -> sqlite3.Connection:
    """SQLite baglantisi olustur (WAL modu + busy_timeout)."""
    _BOARD_DB.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(_BOARD_DB), timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA busy_timeout=5000;")
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn


def _kurulum():
    """Tablolari olustur (ilk calistirmada)."""
    conn = _baglan()
    try:
        conn.executescript(_KURULUM_SQL)
        conn.executescript(_INDEX_SQL)
        conn.commit()
    finally:
        conn.close()


# â”€â”€ Temel Islemler â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


def ekle_bulgu(
    bulan: str,
    konu: str,
    onem: str = "orta",
    dosya_yolu: str = "",
    aciklama: str = "",
    durum: str = "yeni",
) -> dict:
    """Yeni bir bulgu ekle.

    Args:
        bulan: Profil adi (reymen, pasa_38, kiral38)
        konu: Bulgu konusu (benzersiz olmali)
        onem: kritik / orta / dusuk
        dosya_yolu: Ilgili dosya/konum
        aciklama: Detayli aciklama
        durum: yeni / inceleniyor / duzeltildi / reddedildi / beklemede

    Returns:
        Eklenen bulgu (id dahil)
    """
    _kurulum()
    conn = _baglan()
    try:
        bugun = datetime.now().strftime("%Y-%m-%d %H:%M")
        conn.execute(
            """INSERT OR REPLACE INTO findings
               (bulan_profil, tarih, konu, dosya_yolu, onem_derecesi, durum, aciklama, guncelleme_tarihi)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (bulan, bugun, konu, dosya_yolu, onem, durum, aciklama, bugun),
        )
        conn.commit()

        # Eklenen kaydi geri oku
        cursor = conn.execute(
            "SELECT * FROM findings WHERE konu = ? AND bulan_profil = ? ORDER BY id DESC LIMIT 1",
            (konu, bulan),
        )
        satir = cursor.fetchone()
        return dict(satir) if satir else {}
    finally:
        conn.close()


def bulgu_guncelle(
    bulgu_id: int,
    durum: str = "",
    duzelten: str = "",
    dogrulayan: str = "",
    aciklama: str = "",
) -> bool:
    """Bir bulgunun durumunu guncelle.

    Args:
        bulgu_id: Bulgu ID'si
        durum: yeni / inceleniyor / duzeltildi / reddedildi / beklemede
        duzelten: Duzelten profil adi
        dogrulayan: Dogrulayan profil adi
        aciklama: Eklenecek aciklama

    Returns:
        Basarili mi
    """
    _kurulum()
    conn = _baglan()
    try:
        set_ifadeleri = []
        parametreler = []

        if durum:
            set_ifadeleri.append("durum = ?")
            parametreler.append(durum)
        if duzelten:
            set_ifadeleri.append("duzelten_profil = ?")
            parametreler.append(duzelten)
        if dogrulayan:
            set_ifadeleri.append("dogrulayan_profil = ?")
            parametreler.append(dogrulayan)
        if aciklama:
            set_ifadeleri.append("aciklama = ?")
            parametreler.append(aciklama)

        if not set_ifadeleri:
            return False

        set_ifadeleri.append("guncelleme_tarihi = ?")
        parametreler.append(datetime.now().strftime("%Y-%m-%d %H:%M"))
        parametreler.append(bulgu_id)

        conn.execute(
            f"UPDATE findings SET {', '.join(set_ifadeleri)} WHERE id = ?",
            parametreler,
        )
        conn.commit()
        return conn.total_changes > 0
    finally:
        conn.close()


def bulgu_listele(
    durum: str = "",
    onem: str = "",
    bulan: str = "",
    limit: int = 50,
    offset: int = 0,
) -> list[dict]:
    """Bulgulari filtreleyerek listele.

    Args:
        durum: Filtre (yeni/inceleniyor/duzeltildi/reddedildi/beklemede)
        onem: Filtre (kritik/orta/dusuk)
        bulan: Filtre (profil adi)
        limit: Maks sonuc
        offset: Sayfa baslangici

    Returns:
        Filtrelenmis bulgu listesi
    """
    _kurulum()
    conn = _baglan()
    try:
        kosullar = []
        parametreler = []

        if durum:
            kosullar.append("durum = ?")
            parametreler.append(durum)
        if onem:
            kosullar.append("onem_derecesi = ?")
            parametreler.append(onem)
        if bulan:
            kosullar.append("bulan_profil = ?")
            parametreler.append(bulan)

        where = f"WHERE {' AND '.join(kosullar)}" if kosullar else ""

        cursor = conn.execute(
            f"SELECT * FROM findings {where} ORDER BY id DESC LIMIT ? OFFSET ?",
            parametreler + [limit, offset],
        )
        return [dict(satir) for satir in cursor.fetchall()]
    finally:
        conn.close()


def bulgu_sayilari() -> dict:
    """Durum ve oneme gore bulgu sayilari."""
    _kurulum()
    conn = _baglan()
    try:
        # Durum dagilimi
        durumlar = {}
        for satir in conn.execute(
            "SELECT durum, COUNT(*) as cnt FROM findings GROUP BY durum"
        ).fetchall():
            durumlar[satir["durum"]] = satir["cnt"]

        # Onem dagilimi
        onemler = {}
        for satir in conn.execute(
            "SELECT onem_derecesi, COUNT(*) as cnt FROM findings GROUP BY onem_derecesi"
        ).fetchall():
            onemler[satir["onem_derecesi"]] = satir["cnt"]

        toplam = conn.execute("SELECT COUNT(*) as cnt FROM findings").fetchone()["cnt"]

        return {
            "toplam": toplam,
            "durum": durumlar,
            "onem": onemler,
        }
    finally:
        conn.close()


def bulgu_ozet() -> str:
    """Insan tarafindan okunabilir ozet rapor."""
    sayilar = bulgu_sayilari()
    toplam = sayilar["toplam"]
    durumlar = sayilar["durum"]
    onemler = sayilar["onem"]

    satirlar = [
        "=== ORTAK BULGU PANOSU (SQLite WAL) ===",
        f"Toplam: {toplam} bulgu",
        f"  Kritik: {onemler.get('kritik', 0)} | Orta: {onemler.get('orta', 0)} | Dusuk: {onemler.get('dusuk', 0)}",
        f"  Yeni: {durumlar.get('yeni', 0)} | Inceleniyor: {durumlar.get('inceleniyor', 0)}",
        f"  Duzeltildi: {durumlar.get('duzeltildi', 0)} | Beklemede: {durumlar.get('beklemede', 0)} | Red: {durumlar.get('reddedildi', 0)}",
        "",
        "Son 5 bulgu:",
    ]

    son_bulgu = bulgu_listele(limit=5)
    for b in son_bulgu:
        durum_simge = {
            "yeni": "ğŸ†•",
            "inceleniyor": "ğŸ”",
            "duzeltildi": "âœ…",
            "reddedildi": "âŒ",
            "beklemede": "â³",
        }.get(b.get("durum", ""), "â“")
        onem_simge = {"kritik": "ğŸ”´", "orta": "ğŸŸ ", "dusuk": "ğŸŸ¢"}.get(
            b.get("onem_derecesi", ""), "âšª"
        )
        satirlar.append(
            f"  {durum_simge}{onem_simge} #{b['id']} [{b['bulan_profil']}] "
            f"{b['konu'][:60]}"
        )

    return "\n".join(satirlar)


# â”€â”€ Audit Toplu Bulgu Ekleme (K1-K4 guvenlik) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


def audit_tamamla(bulan: str, bulgular_listesi: list[dict]) -> list[dict]:
    """Bir denetim/tarama gorevi sonucunda bulunan tum bulgulari ayri ayri kaydet.

    Bu fonksiyon bulgulari asla OZETLEMEZ, birlestirmez. Her bulgu
    ayri bir satir olarak DB'ye yazilir.

    Args:
        bulan: Profil adi (reymen, pasa_38, kiral38)
        bulgular_listesi: Her biri su anahtarlari iceren dict listesi:
            - konu (str, zorunlu)
            - onem (str, zorunlu: kritik/orta/dusuk)
            - dosya_yolu (str, opsiyonel)
            - aciklama (str, opsiyonel)
            - durum (str, opsiyonel, varsayilan: yeni)

    Returns:
        Eklenen bulgularin listesi (her biri id dahil)

    Ornek:
        audit_tamamla("kiral38", [
            {"konu": "XYZ hatasi", "onem": "kritik", "aciklama": "..."},
            {"konu": "ABC uyarisi", "onem": "orta", "aciklama": "..."},
        ])
    """
    eklenenler = []
    for bulgu in bulgular_listesi:
        if "konu" not in bulgu or "onem" not in bulgu:
            continue  # gecersiz kayit atlanir
        b = ekle_bulgu(
            bulan=bulan,
            konu=bulgu["konu"],
            onem=bulgu["onem"],
            dosya_yolu=bulgu.get("dosya_yolu", ""),
            aciklama=bulgu.get("aciklama", ""),
            durum=bulgu.get("durum", "yeni"),
        )
        eklenenler.append(b)
    return eklenenler


def check_findings_board_health() -> dict:
    """Bulgu panosunun saglik kontrolu.

    Kontroller:
    1. "yeni" durumunda 7 gunden eski bulgu var mi? (ilgilenilmemis)
    2. "inceleniyor" durumunda 14 gunden eski bulgu var mi? (tikanmis)
    3. Toplam bulgu sayisi 500'u gecti mi? (asiri sisisme uyarisi)
    4. Ayni konuda 3+ farkli profil bulgusu var mi? (cakisma)

    Returns:
        {
            "saglikli": True/False,
            "kontroller": [...],
            "ozet": "..."
        }
    """
    _kurulum()
    conn = _baglan()
    try:
        sonuc = {"saglikli": True, "kontroller": [], "uyarilar": []}

        # Kontrol 1: "yeni" durumunda 7 gunden eski bulgular
        eski_yeni = conn.execute("""
            SELECT id, konu, bulan_profil, tarih FROM findings
            WHERE durum = 'yeni' AND tarih < date('now', '-7 days')
            ORDER BY tarih
        """).fetchall()
        if eski_yeni:
            sonuc["saglikli"] = False
            sonuc["kontroller"].append(
                {
                    "kontrol": "yeni_bulgu_bekliyor",
                    "sayi": len(eski_yeni),
                    "en_eskisi": dict(eski_yeni[0]),
                    "aciiklama": f"{len(eski_yeni)} bulgu 7+ gundur 'yeni' durumunda, hic ilgilenilmemis",
                }
            )
        else:
            sonuc["kontroller"].append(
                {"kontrol": "yeni_bulgu_bekliyor", "durum": "temiz"}
            )

        # Kontrol 2: "inceleniyor" durumunda 14 gunden eski bulgular
        tikanmis = conn.execute("""
            SELECT id, konu, bulan_profil, tarih FROM findings
            WHERE durum = 'inceleniyor' AND tarih < date('now', '-14 days')
            ORDER BY tarih
        """).fetchall()
        if tikanmis:
            sonuc["saglikli"] = False
            sonuc["kontroller"].append(
                {
                    "kontrol": "tikanmis_inceleme",
                    "sayi": len(tikanmis),
                    "en_eskisi": dict(tikanmis[0]),
                    "aciiklama": f"{len(tikanmis)} bulgu 14+ gundur 'inceleniyor', cozulmemis",
                }
            )
        else:
            sonuc["kontroller"].append(
                {"kontrol": "tikanmis_inceleme", "durum": "temiz"}
            )

        # Kontrol 3: Toplam bulgu sayisi siniri
        toplam = conn.execute("SELECT COUNT(*) as cnt FROM findings").fetchone()["cnt"]
        if toplam > 500:
            sonuc["saglikli"] = False
            sonuc["kontroller"].append(
                {
                    "kontrol": "asiri_sisme",
                    "sayi": toplam,
                    "aciiklama": f"{toplam} bulgu (esik: 500). improvements.db senaryosu tekrarlaniyor olabilir",
                }
            )
        else:
            sonuc["kontroller"].append(
                {"kontrol": "asiri_sisme", "durum": f"temiz ({toplam} bulgu)"}
            )

        # Kontrol 4: Ayni konuda cakisan bulgular
        cakisan = conn.execute("""
            SELECT konu, COUNT(DISTINCT bulan_profil) as profil_sayisi, GROUP_CONCAT(DISTINCT bulan_profil) as profiller
            FROM findings
            WHERE durum NOT IN ('reddedildi', 'duzeltildi')
            GROUP BY konu
            HAVING profil_sayisi >= 3
            LIMIT 10
        """).fetchall()
        if cakisan:
            sonuc["saglikli"] = False
            sonuc["kontroller"].append(
                {
                    "kontrol": "cakisan_bulgu",
                    "sayi": len(cakisan),
                    "ornek": dict(cakisan[0]),
                    "aciiklama": f"{len(cakisan)} konuda 3+ profil ayni bulguyu ayri ayri girmis",
                }
            )
        else:
            sonuc["kontroller"].append({"kontrol": "cakisan_bulgu", "durum": "temiz"})

        sonuc["ozet"] = "âœ… Saglikli" if sonuc["saglikli"] else "âš ï¸ Sorun var"
        return sonuc
    finally:
        conn.close()


# â”€â”€ Veritabani dogrudan erisim (acil durumlar icin) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


def baglanti_al() -> sqlite3.Connection:
    """Dis baglanti al (ozel sorgular icin)."""
    return _baglan()


# â”€â”€ CLI â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


def _cli():
    import argparse

    parser = argparse.ArgumentParser(description="Ortak Bulgu Panosu (SQLite WAL)")
    parser.add_argument(
        "--ekle", nargs=3, metavar=("BULAN", "KONU", "ONEM"), help="Yeni bulgu ekle"
    )
    parser.add_argument(
        "--guncelle", nargs=2, metavar=("ID", "DURUM"), help="Bulgu durumu guncelle"
    )
    parser.add_argument("--liste", action="store_true", help="Bulgulari listele")
    parser.add_argument("--ozet", action="store_true", help="Ozet rapor")
    parser.add_argument("--durum", default="", help="Filtre: durum")
    parser.add_argument("--onem", default="", help="Filtre: onem")
    parser.add_argument("--bulan", default="", help="Filtre: profil")
    parser.add_argument("--limit", type=int, default=20, help="Maks sonuc")
    parser.add_argument(
        "--audit-tamamla",
        nargs="+",
        metavar=("BULAN", "KONU_ONEM..."),
        help="Toplu audit bulgusu ekle. Format: --audit-tamamla reymen 'konu1:kritik' 'konu2:orta'",
    )
    parser.add_argument(
        "--audit-from-file",
        type=str,
        metavar="JSON_DOSYASI",
        help='JSON dosyasindan audit bulgularini oku. Dosya formati: [{"konu":"...","onem":"kritik"}]',
    )

    args = parser.parse_args()

    _kurulum()

    if args.ekle:
        b = ekle_bulgu(bulan=args.ekle[0], konu=args.ekle[1], onem=args.ekle[2])
        print(f"âœ… #{b['id']} eklendi: {b['konu']}")
    elif args.guncelle:
        basarili = bulgu_guncelle(
            bulgu_id=int(args.guncelle[0]), durum=args.guncelle[1]
        )
        print(f"{'âœ…' if basarili else 'âŒ'} #{args.guncelle[0]} -> {args.guncelle[1]}")
    elif args.ozet:
        print(bulgu_ozet())
    elif args.liste:
        bulgular = bulgu_listele(
            durum=args.durum, onem=args.onem, bulan=args.bulan, limit=args.limit
        )
        if not bulgular:
            print("Bulgu yok.")
        else:
            for b in bulgular:
                print(f"#{b['id']} [{b['bulan_profil']}] {b['konu'][:60]}")
                print(
                    f"    Onem: {b['onem_derecesi']} | Durum: {b['durum']} | Tarih: {b['tarih']}"
                )
                if b.get("duzelten_profil"):
                    print(
                        f"    Duzelten: {b['duzelten_profil']} | Dogrulayan: {b.get('dogrulayan_profil','')}"
                    )
                print()
    elif args.audit_tamamla:
        bulan = args.audit_tamamla[0]
        bulgular = []
        for item in args.audit_tamamla[1:]:
            if ":" in item:
                konu, onem = item.split(":", 1)
                bulgular.append({"konu": konu, "onem": onem})
        if bulgular:
            eklenen = audit_tamamla(bulan, bulgular)
            print(f"âœ… {len(eklenen)} bulgu kaydedildi ({bulan})")
            for b in eklenen:
                print(f"  #{b['id']}: {b['konu'][:60]}")
    elif args.audit_from_file:
        import json as _json

        try:
            with open(args.audit_from_file, "r", encoding="utf-8") as _f:
                _data = _json.load(_f)
            if isinstance(_data, list):
                eklenen = audit_tamamla("reymen", _data)
                print(
                    f"âœ… {len(eklenen)} bulgu kaydedildi (dosya: {args.audit_from_file})"
                )
            elif isinstance(_data, dict) and "bulgular" in _data:
                bulan = _data.get("bulan", "reymen")
                eklenen = audit_tamamla(bulan, _data["bulgular"])
                print(
                    f"âœ… {len(eklenen)} bulgu kaydedildi ({bulan}, dosya: {args.audit_from_file})"
                )
        except Exception as _e:
            print(f"âŒ Dosya okunamadi: {_e}")
    else:
        parser.print_help()


if __name__ == "__main__":
    _cli()
