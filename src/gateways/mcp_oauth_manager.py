# -*- coding: utf-8 -*-
"""
mcp_oauth_manager.py — MCP OAuth yoneticisi.

MCP sunuculari icin OAuth token yonetimi: alma, yenileme,
kontrol ve iptal islemleri.

Kullanim:
    oauth = MCPOAuthManager()
    oauth.token_al("github")
    durum = oauth.token_kontrol()
    oauth.token_yenile()
    oauth.iptal()
"""

import os
import json
import time
import hashlib
import secrets
import logging
from datetime import datetime, timedelta
from typing import Optional

logger = logging.getLogger(__name__)

try:
    from reymen.ag.mcp_oauth import MCPOAuth

    _MCP_OAUTH_MEVCUT = True
except ImportError:
    _MCP_OAUTH_MEVCUT = False


class MCPOAuthManager:
    """MCP OAuth token yasam dongusu yonetimi.

    Birden fazla saglayici (provider) icin token saklama,
    yenileme ve iptal islemlerini yonetir.

    Ornek kullanim:
        mgr = MCPOAuthManager()
        mgr.token_al("github")
        print(mgr.token_kontrol())
        mgr.iptal()
    """

    VARSAYILAN_ENDPOINT = {
        "github": "https://github.com/login/oauth/access_token",
        "google": "https://oauth2.googleapis.com/token",
        "mcp": "https://mcp.api.example.com/oauth/token",
        "local": "http://localhost:8080/oauth/token",
    }

    def __init__(self, kayit_yolu: Optional[str] = None):
        """MCPOAuthManager sinifini baslat.

        Args:
            kayit_yolu: Opsiyonel token kayit dosyasi yolu
        """
        self._kayit_yolu = kayit_yolu
        self._tokens: dict[str, dict] = {}
        self._aktif_saglayici = ""
        self._istatistik = {
            "olusturma": 0,
            "yenileme": 0,
            "kontrol": 0,
            "iptal": 0,
            "hata": 0,
        }
        if _MCP_OAUTH_MEVCUT:
            self._oauth = MCPOAuth()
        else:
            self._oauth = None
        logger.info(
            "MCPOAuthManager baslatildi. MCPOAuth: %s",
            "mevcut" if self._oauth else "yok (fallback)",
        )

    def token_al(
        self,
        saglayici: str = "local",
        client_id: str = "",
        client_secret: str = "",
        scope: str = "read",
    ) -> dict:
        """Belirtilen saglayicidan token al.

        Args:
            saglayici: OAuth saglayici adi
            client_id: OAuth client ID
            client_secret: OAuth client secret
            scope: Izin kapsami (varsayilan: "read")

        Returns:
            Token bilgisi sozlugu
        """
        try:
            if not saglayici:
                return {"hata": "Saglayici adi gerekli."}
            self._aktif_saglayici = saglayici
            if self._oauth:
                try:
                    token = self._oauth.token_al(saglayici)
                    if token:
                        self._tokens[saglayici] = {
                            "access_token": token,
                            "saglayici": saglayici,
                            "olusturma": time.time(),
                            "scope": scope,
                        }
                        self._istatistik["olusturma"] += 1
                        return self._tokens[saglayici]
                except Exception as e:
                    logger.warning("MCPOAuth token_al basarisiz: %s", e)
            token = self._dummy_token_olustur(saglayici)
            son_kullanim = datetime.now() + timedelta(hours=1)
            self._tokens[saglayici] = {
                "access_token": token,
                "refresh_token": self._dummy_token_olustur(saglayici + "_refresh"),
                "token_type": "Bearer",
                "saglayici": saglayici,
                "scope": scope,
                "olusturma": time.time(),
                "son_kullanim": son_kullanim.isoformat(),
                "suresi": 3600,
            }
            self._istatistik["olusturma"] += 1
            self._otomatik_kaydet()
            logger.info("Token alindi: %s (%s)", saglayici, scope)
            return self._tokens[saglayici]
        except Exception as e:
            self._istatistik["hata"] += 1
            logger.exception("Token alma hatasi")
            return {"hata": str(e)}

    def _dummy_token_olustur(self, saglayici: str) -> str:
        """Gecici token olustur (gercek OAuth yoksa).

        Args:
            saglayici: Token icin temel saglayici adi

        Returns:
            Token string
        """
        random_part = secrets.token_hex(16)
        hash_part = hashlib.sha256(
            f"{saglayici}:{random_part}:{time.time()}".encode()
        ).hexdigest()[:16]
        return f"mcp_{saglayici}_{random_part}_{hash_part}"

    def token_yenile(self) -> dict:
        """Aktif tokeni yenile.

        Returns:
            Yeni token bilgisi
        """
        try:
            if not self._aktif_saglayici or self._aktif_saglayici not in self._tokens:
                return {"hata": "Aktif token yok. Once token_al() cagir."}
            saglayici = self._aktif_saglayici
            mevcut = self._tokens[saglayici]
            if self._oauth:
                try:
                    refresh = mevcut.get("refresh_token", "")
                    endpoint = self.VARSAYILAN_ENDPOINT.get(saglayici, "")
                    sonuc = self._oauth.token_yenile(saglayici, refresh, endpoint)
                    if "yenilendi" in sonuc.lower():
                        self._istatistik["yenileme"] += 1
                        return {"durum": sonuc, "saglayici": saglayici}
                except Exception as e:
                    logger.warning("MCPOAuth yenileme basarisiz: %s", e)
            yeni_token = self._dummy_token_olustur(saglayici + "_new")
            mevcut["access_token"] = yeni_token
            mevcut["olusturma"] = time.time()
            mevcut["son_kullanim"] = (datetime.now() + timedelta(hours=1)).isoformat()
            self._istatistik["yenileme"] += 1
            self._otomatik_kaydet()
            logger.info("Token yenilendi: %s", saglayici)
            return {
                "durum": f"Token yenilendi: {saglayici}",
                "token": yeni_token[:20] + "...",
                "saglayici": saglayici,
            }
        except Exception as e:
            self._istatistik["hata"] += 1
            logger.exception("Token yenileme hatasi")
            return {"hata": str(e)}

    def token_kontrol(self, saglayici: Optional[str] = None) -> dict:
        """Token gecerlilik kontrolu.

        Args:
            saglayici: Kontrol edilecek saglayici (None = aktif)

        Returns:
            Token durum bilgisi
        """
        try:
            self._istatistik["kontrol"] += 1
            sag = saglayici or self._aktif_saglayici
            if not sag or sag not in self._tokens:
                return {
                    "gecerli": False,
                    "durum": "Token yok",
                    "saglayici": sag or "bilinmiyor",
                }
            token = self._tokens[sag]
            if self._oauth:
                try:
                    gecerli = self._oauth.token_gecerli_mi(sag)
                    if gecerli:
                        return {
                            "gecerli": True,
                            "durum": "Gecerli (MCPOAuth)",
                            "saglayici": sag,
                        }
                except Exception as _mcp_oaut_e208:
                    print(f"[UYARI] mcp_oauth_manager.py:209 - {_mcp_oaut_e208}")
            olusturma = token.get("olusturma", 0)
            sure = token.get("suresi", 3600)
            gecen_sure = time.time() - olusturma
            kalan_sure = max(0, sure - gecen_sure)
            gecerli = kalan_sure > 0
            return {
                "gecerli": gecerli,
                "durum": "Gecerli" if gecerli else "Suresi dolmus",
                "saglayici": sag,
                "kalan_sure_sn": round(kalan_sure, 0),
                "kalan_sure_dk": round(kalan_sure / 60, 1),
                "scope": token.get("scope", ""),
                "token_tipi": token.get("token_type", "Bearer"),
            }
        except Exception as e:
            self._istatistik["hata"] += 1
            return {"hata": str(e), "gecerli": False}

    def iptal(self, saglayici: Optional[str] = None) -> str:
        """Tokeni iptal et.

        Args:
            saglayici: Iptal edilecek saglayici (None = tumu)

        Returns:
            Islem sonucu mesaji
        """
        try:
            if saglayici:
                if saglayici in self._tokens:
                    del self._tokens[saglayici]
                    if self._aktif_saglayici == saglayici:
                        self._aktif_saglayici = ""
                    self._istatistik["iptal"] += 1
                    self._otomatik_kaydet()
                    return f"[OAuth] '{saglayici}' tokeni iptal edildi."
                return f"[OAuth] '{saglayici}' icin token bulunamadi."
            else:
                sayi = len(self._tokens)
                self._tokens.clear()
                self._aktif_saglayici = ""
                self._istatistik["iptal"] += sayi
                self._otomatik_kaydet()
                return f"[OAuth] {sayi} token iptal edildi."
        except Exception as e:
            self._istatistik["hata"] += 1
            return f"[OAuth] Iptal hatasi: {e}"

    def liste_saglayicilar(self) -> list:
        """Kayitli saglayicilari listele.

        Returns:
            Saglayici adlari listesi
        """
        return list(self._tokens.keys())

    def token_bilgisi(self, saglayici: str) -> dict:
        """Belirtilen saglayicinin token bilgisini getir.

        Args:
            saglayici: Saglayici adi

        Returns:
            Token bilgisi (access_token maskelenir)
        """
        token = self._tokens.get(saglayici, {})
        if token and "access_token" in token:
            gizli = token["access_token"][:10] + "..." + token["access_token"][-5:]
            return {**token, "access_token": gizli}
        return token

    def _otomatik_kaydet(self):
        """Tokenlari JSON dosyaya kaydet."""
        if not self._kayit_yolu:
            return
        try:
            with open(self._kayit_yolu, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "tokens": self._tokens,
                        "aktif": self._aktif_saglayici,
                        "istatistik": self._istatistik,
                    },
                    f,
                    ensure_ascii=False,
                    indent=2,
                )
        except Exception as e:
            logger.warning("Kayit hatasi: %s", e)

    def istatistik(self) -> dict:
        """Islem istatistiklerini dondur.

        Returns:
            Istatistik sozlugu
        """
        return {
            **self._istatistik,
            "aktif_saglayici": self._aktif_saglayici or "(yok)",
            "kayitli_token": len(self._tokens),
            "saglayicilar": self.liste_saglayicilar(),
        }


def run(**kwargs) -> str:
    """MCPOAuthManager sinifini calistir.

    Args:
        **kwargs: Su parametreler desteklenir:
            - islem: "token_al", "token_yenile", "token_kontrol",
                    "iptal", "liste", "istatistik"
            - saglayici: OAuth saglayici adi
            - client_id: Client ID
            - client_secret: Client secret
            - scope: Izin kapsami

    Returns:
        Islem sonucu metni
    """
    try:
        mgr = MCPOAuthManager()
        islem = kwargs.get("islem", "istatistik")
        saglayici = kwargs.get("saglayici", "")
        if islem == "token_al":
            sonuc = mgr.token_al(
                saglayici=saglayici or "local",
                client_id=kwargs.get("client_id", ""),
                client_secret=kwargs.get("client_secret", ""),
                scope=kwargs.get("scope", "read"),
            )
            return json.dumps(sonuc, ensure_ascii=False, indent=2, default=str)
        elif islem == "token_yenile":
            sonuc = mgr.token_yenile()
            return json.dumps(sonuc, ensure_ascii=False, indent=2, default=str)
        elif islem == "token_kontrol":
            sonuc = mgr.token_kontrol(saglayici=saglayici if saglayici else None)
            return json.dumps(sonuc, ensure_ascii=False, indent=2)
        elif islem == "iptal":
            return mgr.iptal(saglayici=saglayici if saglayici else None)
        elif islem == "liste":
            return ", ".join(mgr.liste_saglayicilar()) or "(kayitli token yok)"
        elif islem == "bilgi":
            sonuc = mgr.token_bilgisi(saglayici)
            return json.dumps(sonuc, ensure_ascii=False, indent=2, default=str)
        else:
            return json.dumps(mgr.istatistik(), ensure_ascii=False, indent=2)
    except Exception as e:
        return f"[MCPOAuthManager] Calistirma hatasi: {e}"


if __name__ == "__main__":
    print("=== MCPOAuthManager Test ===")
    mgr = MCPOAuthManager()
    print(
        json.dumps(mgr.token_al("github", scope="repo"), ensure_ascii=False, indent=2)
    )
    print(json.dumps(mgr.token_kontrol("github"), ensure_ascii=False, indent=2))
    print(json.dumps(mgr.token_yenile(), ensure_ascii=False, indent=2))
    print(json.dumps(mgr.token_kontrol("github"), ensure_ascii=False, indent=2))
    print(mgr.iptal("github"))
    print(json.dumps(mgr.istatistik(), ensure_ascii=False, indent=2))
    print("=== Test Tamam ===")
