# -*- coding: utf-8 -*-
"""
proaktif_kontrol.py — Her soru/cevap sonrası eksik kalan yönleri analiz eder.

Ne yapar:
  1. Verilen cevabı analiz eder: hangi açılardan eksik?
  2. Kullanıcı sorusuyla karşılaştırır: istenen her şey verilmiş mi?
  3. Eksik kategorileri tespit eder (kaynak, tablo, örnek, edge case, nicel veri)
  4. Öğrenir: hangi tip sorularda hangi eksikler tekrarlanıyor?
  5. Bir sonraki benzer soruda proaktif olarak eksikleri kapatır

Kullanım:
    denetci = ProaktifDenetci()
    analiz = denetci.soru_cevap_analiz(soru, cevap)
    eksikler = denetci.eksik_bul(analiz)
    denetci.ders_al(analiz)  # Gelecek için öğren

Entegrasyon:
    conversation_loop.coz() sonunda otomatik çağrılır.
"""

import json
import logging
import re
import sqlite3
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

log = logging.getLogger(__name__)

# ── Eksik kategorileri ─────────────────────────────────────────────────────
EKSIK_KATEGORILER = {
    "tablo":           r"(tablo|liste halinde|karşılaştır|özet tablosu)",
    "kaynak":          r"(kaynak|referans|link|adres|site)",
    "ornek":           r"(örnek|misal|demo|kod örneği)",
    "nicel_veri":      r"(kaç|ne kadar|yüzde|oran|istatistik|sayısal)",
    "edge_case":       r"(ya .+? ise|eğer .+? olmazsa|sınır durum|istisna)",
    "karsilastirma":   r"(fark|karşılaş|kıyasla|vs|versus|arasındaki fark)",
    "adim_adim":       r"(adım|sırayla|aşama|nasıl yapılır|prosedür)",
    "neden":           r"(neden|niçin|sebep|gerekçe|kök neden)",
    "ne_zaman":        r"(ne zaman|hangi durumda|hangi koşulda)",
    "nerede":          r"(nerede|hangi dizin|hangi klasör|nereden)",
}

# ── Cevap kalite kontrol listesi ───────────────────────────────────────────
CEVAP_KALITE_KONTROL = [
    ("basarisiz_hata", r"(hata|başarısız|çalışmadı|bulunamadı|yetki yok)\s", True),
    ("bos_cevap", r"^$", True),
    ("cok_kisa", r"^\s*\S+\s*$", True),  # tek kelime
    ("kaynak_yok", r"(bence|sanırım|muhtemelen|tahminen)", False),
    ("tavsiye_eksik", r"(tavsiye|öneri|öncelik|en iyi)", False),
]


class ProaktifDenetci:
    """Her soru/cevap sonrası eksikleri analiz eder ve öğrenir."""

    def __init__(self, db_yol: Optional[Path] = None):
        ROOT = Path(__file__).resolve().parent.parent.parent.parent
        koku = ROOT / "src" if (ROOT / "src").exists() else ROOT
        self._db = db_yol or Path(str(koku.parent if (koku / "src").exists() else koku)) / ".ReYMeN" / "proaktif_ogrenme.db"
        self._db.parent.mkdir(parents=True, exist_ok=True)
        self._vt_kur()
        self._son_analiz: Optional[dict] = None
        self._eksik_ornekleri: dict[str, list[str]] = {}

    def _vt_kur(self):
        with sqlite3.connect(self._db) as vt:
            vt.execute("""
                CREATE TABLE IF NOT EXISTS analiz_gecmisi (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    soru TEXT,
                    cevap_ozeti TEXT,
                    eksik_kategorileri TEXT,
                    kalite_puani INTEGER,
                    sure_ms INTEGER,
                    ts TEXT DEFAULT (datetime('now'))
                )
            """)
            vt.execute("""
                CREATE TABLE IF NOT EXISTS ogrenilen_dersler (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    kategori TEXT,
                    desen TEXT,
                    cozum TEXT,
                    basari_sayisi INTEGER DEFAULT 0,
                    ts TEXT DEFAULT (datetime('now'))
                )
            """)
            vt.execute("""
                CREATE TABLE IF NOT EXISTS eksik_takip (
                    kategori TEXT PRIMARY KEY,
                    toplam_eksik INTEGER DEFAULT 0,
                    son_tarih TEXT
                )
            """)

    def soru_cevap_analiz(self, soru: str, cevap: str) -> dict:
        """Bir soru/cevap çiftini analiz eder ve eksikleri döndürür."""
        baslama = time.time()

        # Soruda hangi kategoriler talep edilmiş?
        talep_edilen = []
        for kat, desen in EKSIK_KATEGORILER.items():
            if re.search(desen, soru, re.IGNORECASE):
                talep_edilen.append(kat)

        # Cevapta hangi kategoriler var?
        cevapta_var = []
        for kat, desen in EKSIK_KATEGORILER.items():
            if re.search(desen, cevap, re.IGNORECASE):
                cevapta_var.append(kat)

        # Talep edilip cevapta olmayan = EKSIK
        eksikler = [k for k in talep_edilen if k not in cevapta_var]

        # Kalite kontrol
        kalite_sorunlari = []
        for ad, desen, hata_mi in CEVAP_KALITE_KONTROL:
            if re.search(desen, cevap, re.IGNORECASE):
                kalite_sorunlari.append(ad)

        # Cevap uzunluğu kontrolü
        kelime_sayisi = len(cevap.split())
        if kelime_sayisi < 10 and len(soru.split()) > 3:
            eksikler.append("cok_kisa_cevap")
        elif kelime_sayisi > 500 and "tablo" not in cevapta_var:
            eksikler.append("tablo_eklenebilir")

        # Puan hesapla
        talep_sayisi = len(talep_edilen) or 1
        eksik_orani = len(eksikler) / talep_sayisi
        kalite_cezasi = len(kalite_sorunlari) * 10
        puan = max(0, min(100, 100 - (eksik_orani * 50) - kalite_cezasi))

        sure = int((time.time() - baslama) * 1000)

        self._son_analiz = {
            "talep_edilen": talep_edilen,
            "cevapta_var": cevapta_var,
            "eksikler": eksikler,
            "kalite_sorunlari": kalite_sorunlari,
            "puan": int(puan),
            "sure_ms": sure,
            "kelime_sayisi": kelime_sayisi,
        }
        return self._son_analiz

    def eksik_bul(self, analiz: Optional[dict] = None) -> list[str]:
        """Mevcut analizdeki eksikleri döndürür."""
        a = analiz or self._son_analiz or {}
        return a.get("eksikler", [])

    def ders_al(self, analiz: Optional[dict] = None):
        """Analizden ders çıkarır, tekrarlanan eksikleri takip eder."""
        a = analiz or self._son_analiz
        if not a:
            return

        eksikler = a.get("eksikler", [])
        with sqlite3.connect(self._db) as vt:
            for eksik in eksikler:
                vt.execute("""
                    INSERT INTO eksik_takip (kategori, toplam_eksik, son_tarih)
                    VALUES (?, 1, datetime('now'))
                    ON CONFLICT(kategori) DO UPDATE SET
                        toplam_eksik = toplam_eksik + 1,
                        son_tarih = datetime('now')
                """, (eksik,))

        # Düşük puanlı cevapları kaydet
        puan = a.get("puan", 100)
        if puan < 60 and analiz:
            with sqlite3.connect(self._db) as vt:
                vt.execute("""
                    INSERT INTO analiz_gecmisi (soru, cevap_ozeti, eksik_kategorileri, kalite_puani, sure_ms)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    a.get("soru", "")[:200],
                    a.get("cevap", "")[:200],
                    ",".join(eksikler),
                    puan,
                    a.get("sure_ms", 0),
                ))

    def en_sik_eksikler(self, limit: int = 5) -> list[tuple]:
        """En sık tekrarlanan eksik kategorilerini döndürür."""
        with sqlite3.connect(self._db) as vt:
            cur = vt.execute(
                "SELECT kategori, toplam_eksik FROM eksik_takip ORDER BY toplam_eksik DESC LIMIT ?",
                (limit,)
            )
            return cur.fetchall()

    def proaktif_uyari(self, soru: str) -> Optional[str]:
        """Benzer sorular için geçmiş eksiklerden uyarı üretir."""
        en_sik = self.en_sik_eksikler(3)
        if not en_sik:
            return None

        uyarilar = []
        for kat, sayi in en_sik:
            if sayi >= 3:  # En az 3 kere aynı eksik
                uyarilar.append(f"⚠️ {kat} (son {sayi} cevapta {sayi} kez eksik)")

        if uyarilar:
            return "Dikkat edilmesi gerekenler:\n" + "\n".join(uyarilar)
        return None

    def durum_raporu(self) -> str:
        """Kısa durum raporu üretir."""
        en_sik = self.en_sik_eksikler(5)
        with sqlite3.connect(self._db) as vt:
            cur = vt.execute("SELECT COUNT(*) FROM analiz_gecmisi")
            toplam_analiz = cur.fetchone()[0]

        lines = [f"📊 Toplam analiz: {toplam_analiz}", f"\nEn sık eksikler:"]
        for kat, sayi in en_sik:
            lines.append(f"  ❌ {kat}: {sayi} kez")
        return "\n".join(lines) if en_sik else "Henüz yeterli veri yok."


# ── conversation_loop entegrasyonu ──────────────────────────────────────────
_proaktif_ornegi: Optional[ProaktifDenetci] = None


def proaktif_baslat() -> ProaktifDenetci:
    """Singleton ProaktifDenetci başlatır."""
    global _proaktif_ornegi
    if _proaktif_ornegi is None:
        _proaktif_ornegi = ProaktifDenetci()
    return _proaktif_ornegi


def soru_sonrasi_kontrol(soru: str, cevap: str) -> dict:
    """Her soru/cevap sonrası çağrılacak ana fonksiyon."""
    denetci = proaktif_baslat()
    analiz = denetci.soru_cevap_analiz(soru, cevap)

    # Eksik varsa ders al
    if analiz.get("eksikler"):
        denetci.ders_al(analiz)
        log.info("[PROAKTIF] Eksikler: %s (puan: %d)", 
                 ", ".join(analiz["eksikler"]), analiz.get("puan", 0))

    # Proaktif uyarı kontrolü
    uyari = denetci.proaktif_uyari(soru)
    if uyari:
        log.info("[PROAKTIF] Uyari: %s", uyari)

    return analiz


if __name__ == "__main__":
    # Test
    denetci = ProaktifDenetci()
    test_soru = "Bana Linux komutlarını tablo halinde sırala, örneklerle göster"
    test_cevap = "ls komutu dizin listeler. cd ile dizin değiştirilir."
    analiz = denetci.soru_cevap_analiz(test_soru, test_cevap)
    print(f"Soru: {test_soru}")
    print(f"Analiz: {json.dumps(analiz, indent=2, ensure_ascii=False)}")
    denetci.ders_al(analiz)
    print(f"\nEn sik eksikler: {denetci.en_sik_eksikler()}")
