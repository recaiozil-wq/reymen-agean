# -*- coding: utf-8 -*-
"""gateway/authz_mixin.py — Gateway Yetkilendirme Mixin.

Tüm platformlar için ortak token doğrulama, yetki kontrolü, API anahtarı yönetimi.
"""

import hashlib
import hmac
import json
import os
import time
from typing import Any, Callable, Optional
import logging
logger = logging.getLogger(__name__)


class AuthzMixin:
    """Yetkilendirme mixin — platformlara ortak auth kabiliyeti kazandırır."""

    def __init__(self):
        self._api_anahtarlari: dict[str, dict] = {}
        self._token_ornekleri: dict[str, str] = {}
        self._roller: dict[str, list[str]] = {}
        self._kullanici_yetkileri: dict[str, list[str]] = {}

    # ── API Anahtarı Yönetimi ──────────────────────────────────────────

    def api_anahtari_ekle(self, anahtar: str, etiket: str = "", roller: Optional[list[str]] = None):
        """API anahtarı ekle.

        Args:
            anahtar: API anahtarı
            etiket: Tanımlayıcı etiket
            roller: İzin verilen roller
        """
        self._api_anahtarlari[anahtar] = {
            "etiket": etiket,
            "roller": roller or ["kullanici"],
            "olusturma": time.time(),
            "son_kullanim": 0,
        }

    def api_anahtari_dogrula(self, anahtar: str) -> bool:
        """API anahtarının geçerliliğini kontrol et."""
        if anahtar in self._api_anahtarlari:
            self._api_anahtarlari[anahtar]["son_kullanim"] = time.time()
            return True
        return False

    def api_anahtari_sil(self, anahtar: str) -> bool:
        """API anahtarı sil."""
        try:
            return bool(self._api_anahtarlari.pop(anahtar, None))
        except Exception:
            return False

    def api_anahtari_listele(self) -> list[dict]:
        """Tüm API anahtarlarını döndür (anahtar değeri hariç)."""
        return [
            {"etiket": v["etiket"], "roller": v["roller"],
             "olusturma": v["olusturma"], "son_kullanim": v["son_kullanim"]}
            for v in self._api_anahtarlari.values()
        ]

    # ── Token Doğrulama ────────────────────────────────────────────────

    def token_olustur(self, kullanici_id: str, gizli: str) -> str:
        """HMAC tabanlı token oluştur."""
        zaman = str(int(time.time()))
        mesaj = f"{kullanici_id}:{zaman}"
        imza = hmac.new(gizli.encode(), mesaj.encode(), hashlib.sha256).hexdigest()
        token = f"{kullanici_id}.{zaman}.{imza[:16]}"
        self._token_ornekleri[token[:20]] = kullanici_id
        return token

    def token_dogrula(self, token: str, gizli: str, max_yas: int = 86400) -> Optional[str]:
        """Token doğrula, başarılıysa kullanıcı ID'sini döndür."""
        try:
            parcalar = token.split(".")
            if len(parcalar) != 3:
                return None
            kullanici_id, zaman, _ = parcalar
            zaman_int = int(zaman)
            if time.time() - zaman_int > max_yas:
                return None
            beklenen = hmac.new(
                gizli.encode(), f"{kullanici_id}:{zaman}".encode(), hashlib.sha256
            ).hexdigest()[:16]
            if not hmac.compare_digest(parcalar[2], beklenen):
                return None
            return kullanici_id
        except Exception:
            return None

    # ── Yetki Kontrolü ─────────────────────────────────────────────────

    def yetki_tanimla(self, kullanici_id: str, roller: list[str]):
        """Kullanıcıya roller ata."""
        self._kullanici_yetkileri[kullanici_id] = roller

    def yetki_kontrol(self, kullanici_id: str, gerekli_rol: str) -> bool:
        """Kullanıcının belirli bir role sahip olup olmadığını kontrol et."""
        try:
            roller = self._kullanici_yetkileri.get(kullanici_id, [])
            return gerekli_rol in roller
        except Exception:
            return False

    def yetkili_mi(self, kullanici_id: str, izin: str) -> bool:
        """Kullanıcının belirli bir izne sahip olup olmadığını kontrol et (alias)."""
        return self.yetki_kontrol(kullanici_id, izin)

    # ── Ortak Gateway Metodları ────────────────────────────────────────

    def ping(self) -> dict:
        """Sağlık kontrolü."""
        return {
            "modul": "authz_mixin",
            "durum": "hazir",
            "api_anahtar_sayisi": len(self._api_anahtarlari),
            "kullanici_sayisi": len(self._kullanici_yetkileri),
        }

    def send_message(self, mesaj: str, hedef: str, **kwargs) -> str:
        """Yetkilendirme mesajı gönder (soyut)."""
        return f"[Authz]: {hedef} -> {mesaj[:50]}... (yetki kanalı)"

    # ── Dosyadan/Sınıf Dışı Kullanım ──────────────────────────────────

    def json_aktar(self) -> dict:
        """Durumu JSON'a aktar."""
        return {
            "anahtarlar": {k: {"etiket": v["etiket"], "roller": v["roller"]}
                          for k, v in self._api_anahtarlari.items()},
            "kullanicilar": dict(self._kullanici_yetkileri),
        }

    def json_yukle(self, veri: dict):
        """JSON'dan durum yükle."""
        try:
            for anahtar, bilgi in veri.get("anahtarlar", {}).items():
                self.api_anahtari_ekle(anahtar, bilgi.get("etiket", ""), bilgi.get("roller"))
            self._kullanici_yetkileri.update(veri.get("kullanicilar", {}))
        except Exception as e:
            raise ValueError(f"Authz JSON yükleme hatası: {e}")


# ── Testler için Rol Enum ─────────────────────────────────────────────
from enum import Enum
import functools


class Rol(str, Enum):
    """Kullanıcı rolleri."""
    ZIYARETCI = "ziyaretci"
    KULLANICI = "kullanici"
    YONETICI = "yonetici"
    YASAKLI = "yasakli"


class Yetki(str, Enum):
    """Sistem yetkileri."""
    MESAJ_GONDER = "mesaj_gonder"
    SISTEM_YONET = "sistem_yonet"


class YetkilendirmeMixin:
    """Yetkilendirme mixin — testlerde kullanılan tam Türkçe arayüz."""

    ROL_MAP = {
        "ziyaretci": Rol.ZIYARETCI,
        "kullanici": Rol.KULLANICI,
        "admin": Rol.YONETICI,
        "yonetici": Rol.YONETICI,
        "yasakli": Rol.YASAKLI,
    }

    def __init__(self):
        self._roller: dict[str, str] = {}
        self._varsayilan_rol: str = "ziyaretci"
        self._kara_liste: set[str] = set()
        self._beyaz_liste: set[str] = set()
        self._platform_izinleri: dict[str, set[str]] = {}
        self._yetki_esikleri: dict[str, str] = {
            Yetki.MESAJ_GONDER.value: "kullanici",
            Yetki.SISTEM_YONET.value: "yonetici",
        }
        self._mesaj_kuyrugu: list[dict] = []

    # ── Rol Yönetimi ──────────────────────────────────────────────────

    def rol_ata(self, kullanici_id: str, rol: str) -> bool:
        normalized = rol.lower()
        if normalized not in self.ROL_MAP:
            return False
        self._roller[kullanici_id] = normalized
        return True

    def rol_al(self, kullanici_id: str) -> Rol:
        if kullanici_id in self._kara_liste:
            return Rol.YASAKLI
        if kullanici_id in self._beyaz_liste:
            return Rol.YONETICI
        rol_str = self._roller.get(kullanici_id, self._varsayilan_rol)
        return self.ROL_MAP.get(rol_str, Rol.ZIYARETCI)

    def rol_sil(self, kullanici_id: str):
        self._roller.pop(kullanici_id, None)

    def rol_listele(self) -> dict[str, str]:
        return {uid: self.ROL_MAP.get(r, Rol.ZIYARETCI).value
                for uid, r in self._roller.items()}

    def varsayilan_rol_ayarla(self, rol: str) -> bool:
        normalized = rol.lower()
        if normalized not in self.ROL_MAP:
            return False
        self._varsayilan_rol = normalized
        return True

    def varsayilan_rol_al(self) -> Rol:
        return self.ROL_MAP.get(self._varsayilan_rol, Rol.ZIYARETCI)

    # ── Kara Liste / Beyaz Liste ─────────────────────────────────────

    def kara_listeye_ekle(self, kullanici_id: str):
        self._kara_liste.add(kullanici_id)

    def kara_liste_kaldir(self, kullanici_id: str):
        self._kara_liste.discard(kullanici_id)
        return None  # discard returns None

    def kara_liste_mi(self, kullanici_id: str) -> bool:
        return kullanici_id in self._kara_liste

    def beyaz_listeye_ekle(self, kullanici_id: str):
        self._beyaz_liste.add(kullanici_id)

    # ── Platform İzinleri ────────────────────────────────────────────

    def platform_izin_ekle(self, platform: str, kullanici_id: str):
        self._platform_izinleri.setdefault(platform, set()).add(kullanici_id)

    def platform_izin_kaldir(self, platform: str, kullanici_id: str):
        self._platform_izinleri.get(platform, set()).discard(kullanici_id)

    def platform_izinli_mi(self, platform: str, kullanici_id: str) -> bool:
        izinliler = self._platform_izinleri.get(platform)
        if izinliler is None:
            return True  # platformda kisitlama yoksa herkese acik
        return kullanici_id in izinliler

    # ── Yetki Kontrolü ───────────────────────────────────────────────

    def yetki_kontrol(self, kullanici_id: str, gerekli_yetki: Yetki,
                      platform: str = "") -> tuple[bool, str]:
        # Kara liste kontrolu
        if self.kara_liste_mi(kullanici_id):
            return False, "kullanici engellenmis"

        # Platform kisitlamasi
        if platform and not self.platform_izinli_mi(platform, kullanici_id):
            return False, f"platform izni yok: {platform}"

        rol = self.rol_al(kullanici_id)
        esik = self._yetki_esikleri.get(gerekli_yetki, "ziyaretci")
        esik_rol = self.ROL_MAP.get(esik, Rol.ZIYARETCI)
        # Rol hiyerarsisi: YONETICI > KULLANICI > ZIYARETCI > YASAKLI
        hiyerarsi = [Rol.YASAKLI, Rol.ZIYARETCI, Rol.KULLANICI, Rol.YONETICI]
        if hiyerarsi.index(rol) >= hiyerarsi.index(esik_rol):
            return True, ""
        return False, "yetersiz yetki"

    def yetki_esigi_ayarla(self, yetki: Yetki, rol: str) -> bool:
        normalized = rol.lower()
        if normalized not in self.ROL_MAP:
            return False
        self._yetki_esikleri[yetki] = normalized
        return True

    def yetki_esigi_al(self, yetki: Yetki) -> Rol:
        esik = self._yetki_esikleri.get(yetki, "ziyaretci")
        return self.ROL_MAP.get(esik, Rol.ZIYARETCI)

    def yetkilendirme_ozeti(self) -> dict:
        return {
            "toplam_kullanici": len(self._roller),
            "varsayilan_rol": self._varsayilan_rol,
            "kara_liste": len(self._kara_liste),
            "beyaz_liste": len(self._beyaz_liste),
        }

    # ── Sağlık / Mesaj ───────────────────────────────────────────────

    def ping(self) -> dict:
        return {"modul": "authz_mixin", "durum": "hazir"}

    def send_message(self, mesaj: str, hedef: str) -> str:
        rol = self.rol_al(hedef)
        if rol in (Rol.YONETICI, Rol.KULLANICI):
            self._mesaj_kuyrugu.append({"hedef": hedef, "mesaj": mesaj})
            return f"mesaj kaydedildi: {hedef} -> {mesaj[:30]}"
        return f"yetkisi yok: {hedef}"

    # ── Decorator ────────────────────────────────────────────────────

    def yetkilendirilmis(self, gerekli_yetki: Yetki):
        """Decorator: belirli bir yetki gerektiren fonksiyonlar icin."""
        def decorator(fn):
            @functools.wraps(fn)
            def wrapper(*args, **kwargs):
                # args[1] -> ctx (dict with 'kullanici_id')
                ctx = args[1] if len(args) > 1 else {}
                kullanici_id = ctx.get("kullanici_id", "") if isinstance(ctx, dict) else ""
                gecerli, hata = self.yetki_kontrol(kullanici_id, gerekli_yetki)
                if gecerli:
                    return fn(*args, **kwargs)
                return {"error": hata}
            return wrapper
        return decorator


def kullanici_yetkilendir(fn):
    """Decorator: kullanici_id='0' olan istekleri engeller."""
    @functools.wraps(fn)
    def wrapper(kullanici_id, *args, **kwargs):
        if kullanici_id == "0":
            return {"error": "yetkisiz kullanici"}
        return fn(kullanici_id, *args, **kwargs)
    return wrapper


# Global instance
yetkilendirme = AuthzMixin()
kuresel_yetki = YetkilendirmeMixin()
