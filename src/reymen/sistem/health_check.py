# -*- coding: utf-8 -*-
"""health_check.py - ReYMeN Calisma Zamani Saglik Kontrolu.

Kullanim:
    from reymen.sistem.health_check import saglik_kontrolu
    rapor = saglik_kontrolu()
    from reymen.sistem.health_check import HealthChecker
    hc = HealthChecker()
    hc.tam_kontrol()
"""

import importlib
import os
import shutil
import time
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class HealthDurum:
    IYI = "iyi"
    UYARI = "uyari"
    KRITIK = "kritik"
    HATA = "hata"


class HealthChecker:
    KRITIK_MODULLER = [
        "reymen.sistem.config_loader",
        "reymen.sistem.state_machine",
        "reymen.sistem.circuit_breaker",
        "reymen.guvenlik.security_engine",
        "reymen.hafiza",
    ]
    API_SAGLIK_URLS = {
        "ollama": "http://localhost:11434/api/tags",
        "lmstudio": "http://localhost:1234/v1/models",
    }
    DISK_UYARI_ESIGI_GB = 2.0
    DISK_KRITIK_ESIGI_GB = 0.5
    BELLEK_UYARI_ESIGI_MB = 200

    def __init__(self, base_dir=None):
        self.base_dir = base_dir or Path(__file__).resolve().parent.parent.parent
        self.sorunlar = []
        self.rapor = {
            "zaman": time.strftime("%Y-%m-%d %H:%M:%S"),
            "durum": HealthDurum.IYI,
            "kontroller": {},
            "sorunlar": [],
        }

    def _sorun_ekle(self, seviye, alan, mesaj):
        sorun = {"seviye": seviye, "alan": alan, "mesaj": mesaj}
        self.sorunlar.append(sorun)
        if seviye == HealthDurum.KRITIK:
            if self.rapor["durum"] != HealthDurum.HATA:
                self.rapor["durum"] = HealthDurum.KRITIK
        elif seviye == HealthDurum.UYARI and self.rapor["durum"] == HealthDurum.IYI:
            self.rapor["durum"] = HealthDurum.UYARI
        elif seviye == HealthDurum.HATA:
            self.rapor["durum"] = HealthDurum.HATA

    def disk_kontrol(self):
        try:
            yol = str(self.base_dir)
            if not os.path.exists(yol):
                yol = str(Path.home())
            toplam, bos, kullanilabilir = shutil.disk_usage(yol)
            bos_gb = bos / (1024**3)
            kullanilabilir_gb = kullanilabilir / (1024**3)
            toplam_gb = toplam / (1024**3)
            kullanilma_orani = ((toplam - bos) / toplam) * 100
            sonuc = {
                "toplam_gb": round(toplam_gb, 2),
                "bos_gb": round(bos_gb, 2),
                "kullanilabilir_gb": round(kullanilabilir_gb, 2),
                "kullanim_orani": round(kullanilma_orani, 1),
            }
            if kullanilabilir_gb < self.DISK_KRITIK_ESIGI_GB:
                self._sorun_ekle(
                    HealthDurum.KRITIK,
                    "disk",
                    "Kritik: {:.1f}GB disk kaldi".format(kullanilabilir_gb),
                )
            elif kullanilabilir_gb < self.DISK_UYARI_ESIGI_GB:
                self._sorun_ekle(
                    HealthDurum.UYARI,
                    "disk",
                    "Dusuk disk: {:.1f}GB kaldi".format(kullanilabilir_gb),
                )
            self.rapor["kontroller"]["disk"] = sonuc
            return sonuc
        except Exception as e:
            self._sorun_ekle(HealthDurum.HATA, "disk", str(e))
            return {"hata": str(e)}

    def bellek_kontrol(self):
        try:
            try:
                import psutil

                bellek = psutil.virtual_memory()
                sonuc = {
                    "toplam_mb": round(bellek.total / (1024**2), 1),
                    "kullanilabilir_mb": round(bellek.available / (1024**2), 1),
                    "kullanim_orani": bellek.percent,
                }
                if bellek.available / (1024**2) < self.BELLEK_UYARI_ESIGI_MB:
                    self._sorun_ekle(
                        HealthDurum.UYARI,
                        "bellek",
                        "Dusuk bellek: {:.0f}MB kaldi".format(
                            bellek.available / (1024**2)
                        ),
                    )
                self.rapor["kontroller"]["bellek"] = sonuc
                return sonuc
            except ImportError as _e:
                logger.warning(
                    "[HealthCheck] Modul yuklenemedi (L106): %s", ImportError
                )
                pass
            if os.path.exists("/proc/meminfo"):
                meminfo = {}
                with open("/proc/meminfo", "r") as f:
                    for satir in f:
                        parcalar = satir.split(":")
                        if len(parcalar) == 2:
                            anahtar = parcalar[0].strip()
                            deger = parcalar[1].strip().split()[0]
                            meminfo[anahtar] = int(deger)
                toplam = meminfo.get("MemTotal", 0) / 1024
                bos = meminfo.get("MemAvailable", 0) / 1024
                sonuc = {
                    "toplam_mb": round(toplam, 1),
                    "kullanilabilir_mb": round(bos, 1),
                    "kullanim_orani": round(((toplam - bos) / toplam) * 100, 1),
                }
                if bos < self.BELLEK_UYARI_ESIGI_MB:
                    self._sorun_ekle(
                        HealthDurum.UYARI,
                        "bellek",
                        "Dusuk bellek: {:.0f}MB kaldi".format(bos),
                    )
                self.rapor["kontroller"]["bellek"] = sonuc
                return sonuc
            sonuc = {"not": "bellek bilgisi mevcut degil"}
            self.rapor["kontroller"]["bellek"] = sonuc
            return sonuc
        except Exception as e:
            self._sorun_ekle(HealthDurum.HATA, "bellek", str(e))
            return {"hata": str(e)}

    def modul_kontrolu(self):
        sonuc = {"moduller": {}, "basarili": 0, "basarisiz": 0}
        for mod_adi in self.KRITIK_MODULLER:
            try:
                importlib.import_module(mod_adi)
                sonuc["moduller"][mod_adi] = "ok"
                sonuc["basarili"] += 1
            except ImportError:
                sonuc["moduller"][mod_adi] = "yuklenemedi"
                sonuc["basarisiz"] += 1
                self._sorun_ekle(
                    HealthDurum.UYARI, "modul", "{} yuklenemedi".format(mod_adi)
                )
            except Exception as e:
                sonuc["moduller"][mod_adi] = "hata: {}".format(type(e).__name__)
                sonuc["basarisiz"] += 1
                self._sorun_ekle(
                    HealthDurum.UYARI, "modul", "{} hata: {}".format(mod_adi, e)
                )
        self.rapor["kontroller"]["moduller"] = sonuc
        return sonuc

    def api_baglantisi(self):
        try:
            import urllib.request
            import urllib.error
        except ImportError:
            return {"not": "urllib mevcut degil"}
        sonuc = {}
        for isim, url in self.API_SAGLIK_URLS.items():
            try:
                req = urllib.request.Request(url, method="GET")
                with urllib.request.urlopen(req, timeout=3) as resp:
                    sonuc[isim] = {"durum": "erisilebilir", "kod": resp.status}
            except urllib.error.URLError:
                sonuc[isim] = {"durum": "erisilemez"}
                self._sorun_ekle(
                    HealthDurum.UYARI, "api", "{} erisilemez ({})".format(isim, url)
                )
            except Exception as e:
                sonuc[isim] = {"durum": "hata", "mesaj": str(e)}
                self._sorun_ekle(HealthDurum.UYARI, "api", "{}: {}".format(isim, e))
        self.rapor["kontroller"]["api"] = sonuc
        return sonuc

    def dosya_sistemi_kontrol(self):
        kontrol = {
            "base_dir": self.base_dir,
            "reymen_pkg": self.base_dir / "reymen",
            "sistem_dir": self.base_dir / "reymen" / "sistem",
            "guvenlik_dir": self.base_dir / "reymen" / "guvenlik",
            "hafiza_dir": self.base_dir / "reymen" / "hafiza",
        }
        sonuc = {}
        for isim, yol in kontrol.items():
            mevcut = yol.exists()
            sonuc[isim] = "var" if mevcut else "yok"
            if not mevcut:
                seviye = HealthDurum.KRITIK if isim == "base_dir" else HealthDurum.UYARI
                self._sorun_ekle(
                    seviye, "dosya_sistemi", "{} bulunamadi: {}".format(isim, yol)
                )
        self.rapor["kontroller"]["dosya_sistemi"] = sonuc
        return sonuc

    def audit_tamamla(
        self,
        bulan_profil=None,
        konu=None,
        dosya_yolu="",
        onem_derecesi="orta",
        aciklama="",
    ):
        """
        Katman 1 — Denetim sonucunu bulgu panosuna OTOMATİK kaydeder.

        Her tam_kontrol() çalıştığında bu fonksiyon çağrılır:
          1. HealthChecker bulgularını (self.sorunlar) board'a yazar
          2. Eğer hiç sorun yoksa "Temiz rapor" kaydı düşer
          3. Bağımsız çağrı: audit_tamamla(bulan_profil="reymen", konu="...", ...)

        Parametreler:
            bulan_profil: "reymen"/"kiral38"/"pasa_38"/"default"
            konu: Bulgu başlığı
            dosya_yolu: İlgili dosya (opsiyonel)
            onem_derecesi: "kritik"/"orta"/"dusuk"
            aciklama: Açıklama metni
        Returns:
            {"basarili": bool, "id": int|None, "hata": str|None}
        """
        import datetime, sqlite3, logging

        logger = logging.getLogger(__name__)

        # Board yolunu bul
        board_path = self.base_dir / "shared_state" / "findings_board.db"

        # DB yoksa oluştur
        board_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(board_path))
        cur = conn.cursor()
        cur.execute("""
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
            )
        """)

        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        profil = bulan_profil or "reymen"

        # Eğer spesifik konu verilmemişse, self.sorunlar'ı board'a yaz
        if konu is None:
            yazilan = 0
            for sorun in self.sorunlar:
                try:
                    baslik = "[{}] {}".format(sorun["alan"], sorun["mesaj"][:80])
                    cur.execute(
                        """
                        INSERT OR IGNORE INTO findings
                        (bulan_profil, tarih, konu, dosya_yolu, onem_derecesi, durum, aciklama)
                        VALUES (?, ?, ?, ?, ?, 'yeni', ?)
                    """,
                        (
                            profil,
                            now,
                            baslik,
                            dosya_yolu,
                            sorun["seviye"],
                            sorun["mesaj"],
                        ),
                    )
                    if cur.rowcount > 0:
                        yazilan += 1
                except Exception as e:
                    logger.warning("[audit_tamamla] Kayit hatasi: %s", e)

            if yazilan == 0 and not self.sorunlar:
                # Hiç sorun yok — "temiz" kaydı
                cur.execute(
                    """
                    INSERT OR IGNORE INTO findings
                    (bulan_profil, tarih, konu, dosya_yolu, onem_derecesi, durum, aciklama)
                    VALUES (?, ?, ?, ?, 'dusuk', 'yeni', ?)
                """,
                    (
                        profil,
                        now,
                        "Saglik kontrolu: Temiz rapor",
                        dosya_yolu,
                        "{} kontrollerin hicbirinde sorun bulunamadi.".format(now),
                    ),
                )
                yazilan = 1 if cur.rowcount > 0 else 0

            conn.commit()
            son_id = cur.lastrowid
            conn.close()
            logger.info(
                "[audit_tamamla] %d bulgu board'a yazildi (tam_kontrol sonrasi)",
                yazilan,
            )
            return {"basarili": True, "id": son_id, "yazilan": yazilan, "hata": None}

        # Spesifik kayıt
        try:
            cur.execute(
                """
                INSERT OR IGNORE INTO findings
                (bulan_profil, tarih, konu, dosya_yolu, onem_derecesi, durum, aciklama)
                VALUES (?, ?, ?, ?, ?, 'yeni', ?)
            """,
                (profil, now, konu, dosya_yolu, onem_derecesi, aciklama),
            )
            conn.commit()
            son_id = cur.lastrowid
            yazildi = cur.rowcount > 0
            conn.close()

            if yazildi:
                logger.info("[audit_tamamla] Kaydedildi: #%d — %s", son_id, konu[:60])
            else:
                logger.info("[audit_tamamla] Atlandi (benzersiz): %s", konu[:60])

            return {
                "basarili": True,
                "id": son_id,
                "yazilan": 1 if yazildi else 0,
                "yeni_mi": yazildi,
                "hata": None,
            }

        except Exception as e:
            conn.close()
            logger.error("[audit_tamamla] Hata: %s", e)
            return {"basarili": False, "id": None, "yazilan": 0, "hata": str(e)}

    def check_findings_board_health(self):
        """
        Katman 2 — Bulgu Panosu (findings_board.db) Sağlık Kontrolü.

        1. Son 7 günde en az 1 audit/tarama çalıştı mı? (log'lardan kontrol)
        2. Audit çalıştıysa, aynı dönemde board'a yeni bulgu eklendi mi?
        3. Audit var ama board güncel değilse → Telegram uyarısı
        4. 3 profilin SOUL.md'sinde findings_board kuralı hala var mı? (haftalık)
        """
        import datetime, json, re

        sonuc = {
            "son_7_gun_audit": False,
            "son_7_gun_board_guncellemesi": False,
            "uyari_mesaji": None,
            "soul_durumu": {},
        }

        now = datetime.datetime.now()
        yedi_gun_once = now - datetime.timedelta(days=7)
        yedi_gun_once_ts = yedi_gun_once.timestamp()

        # 1) Log'lardan son 7 günde audit/tarama ara
        log_dir = self.base_dir / "logs"
        audit_bulundu = False
        if log_dir.exists():
            for log_file in log_dir.glob("*.log"):
                if log_file.stat().st_mtime < yedi_gun_once_ts:
                    continue
                try:
                    with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
                        icerik = f.read()
                    if re.search(
                        r"saglik_kontrolu|health_check|scan|tarama|audit|tam_kontrol",
                        icerik,
                        re.IGNORECASE,
                    ):
                        audit_bulundu = True
                        break
                except Exception:
                    pass
        # Her ihtimale karşı .ReYMeN/logs/ dizinini de kontrol et
        reymen_log = self.base_dir / ".ReYMeN" / "logs"
        if not audit_bulundu and reymen_log.exists():
            for log_file in reymen_log.glob("*.log"):
                if log_file.stat().st_mtime < yedi_gun_once_ts:
                    continue
                try:
                    with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
                        icerik = f.read()
                    if re.search(
                        r"saglik_kontrolu|health_check|scan|tarama|audit|tam_kontrol",
                        icerik,
                        re.IGNORECASE,
                    ):
                        audit_bulundu = True
                        break
                except Exception:
                    pass

        sonuc["son_7_gun_audit"] = audit_bulundu

        # 2) Board'da son 7 günde yeni bulgu var mı?
        board_guncellendi = False
        board_path = self.base_dir / "shared_state" / "findings_board.db"
        if board_path.exists():
            try:
                import sqlite3

                board_conn = sqlite3.connect(str(board_path))
                board_cur = board_conn.cursor()
                board_cur.execute(
                    "SELECT COUNT(*) FROM findings WHERE tarih >= ?",
                    (yedi_gun_once.strftime("%Y-%m-%d"),),
                )
                yeni_bulgu = board_cur.fetchone()[0]
                board_conn.close()
                board_guncellendi = yeni_bulgu > 0
            except Exception as e:
                sonuc["board_hatasi"] = str(e)

        sonuc["son_7_gun_board_guncellemesi"] = board_guncellendi

        # 3) Audit var ama board güncel değilse uyarı
        if audit_bulundu and not board_guncellendi:
            uyari = (
                "Denetim yapildi ama bulgu panosuna yazilmadi, "
                "kural bozulmus olabilir!"
            )
            sonuc["uyari_mesaji"] = uyari
            self._sorun_ekle(HealthDurum.UYARI, "findings_board", uyari)

        # 4) 3 profilin SOUL.md'sinde kural hala var mı?
        hermes_profiles = Path.home() / "AppData" / "Local" / "hermes" / "profiles"
        for profil_adi in ["default", "reymen", "kiral38"]:
            soul_path = hermes_profiles / profil_adi / "SOUL.md"
            kural_var = False
            if soul_path.exists():
                try:
                    with open(soul_path, "r", encoding="utf-8", errors="ignore") as f:
                        icerik = f.read()
                    kural_var = (
                        "findings" in icerik.lower() or "board" in icerik.lower()
                    )
                except Exception:
                    pass
            sonuc["soul_durumu"][profil_adi] = kural_var
            if not kural_var:
                self._sorun_ekle(
                    HealthDurum.UYARI,
                    "soul_md",
                    "{} SOUL.md'de findings_board kurali eksik!".format(profil_adi),
                )

        self.rapor["kontroller"]["findings_board"] = sonuc
        return sonuc

    def tam_kontrol(self):
        self.disk_kontrol()
        self.bellek_kontrol()
        self.modul_kontrolu()
        self.api_baglantisi()
        self.dosya_sistemi_kontrol()
        self.check_findings_board_health()
        self.audit_tamamla()
        self.rapor["sorunlar"] = self.sorunlar
        self.rapor["toplam_sorun"] = len(self.sorunlar)
        self.rapor["sorun_ozeti"] = {
            "kritik": len(
                [s for s in self.sorunlar if s["seviye"] == HealthDurum.KRITIK]
            ),
            "uyari": len(
                [s for s in self.sorunlar if s["seviye"] == HealthDurum.UYARI]
            ),
            "hata": len([s for s in self.sorunlar if s["seviye"] == HealthDurum.HATA]),
        }
        return self.rapor


def saglik_kontrolu():
    hc = HealthChecker()
    return hc.tam_kontrol()


def hizli_kontrol():
    rapor = saglik_kontrolu()
    durum = rapor["durum"]
    sorun = rapor["toplam_sorun"]
    ozet = rapor.get("sorun_ozeti", {})
    return "[{}] {} sorun (kritik:{} uyari:{} hata:{}) - {}".format(
        durum.upper(),
        sorun,
        ozet.get("kritik", 0),
        ozet.get("uyari", 0),
        ozet.get("hata", 0),
        rapor["zaman"],
    )


if __name__ == "__main__":
    rapor = saglik_kontrolu()
    print()
    print("=" * 50)
    print("ReYMeN Saglik Raporu - " + rapor["zaman"])
    print("=" * 50)
    print("Durum: " + rapor["durum"].upper())
    print("Toplam sorun: {}".format(rapor["toplam_sorun"]))
    ozet = rapor.get("sorun_ozeti", {})
    print("  Kritik: {}".format(ozet.get("kritik", 0)))
    print("  Uyari:  {}".format(ozet.get("uyari", 0)))
    print("  Hata:   {}".format(ozet.get("hata", 0)))
    print()
    for alan, veri in rapor["kontroller"].items():
        print("  [{}]".format(alan))
        if isinstance(veri, dict):
            for k, v in veri.items():
                if isinstance(v, dict):
                    print("    {}: {}".format(k, v.get("durum", v)))
                else:
                    print("    {}: {}".format(k, v))
    print()
    for sorun in rapor["sorunlar"]:
        simge_map = {"kritik": "!", "uyari": "~", "hata": "X"}
        simge = simge_map.get(sorun["seviye"], "?")
        print("  [{}] [{}] {}".format(simge, sorun["alan"], sorun["mesaj"]))
    if not rapor["sorunlar"]:
        print("  OK Sorun yok - tum sistemler normal.")
    print("=" * 50)
