# -*- coding: utf-8 -*-
"""
âš™ï¸ OAuth Servis â€” OAuth sistemi yÃ¶neticisi.

Provider'lar iÃ§in login/callback/refresh/logout/durum iÅŸlemlerini
tek bir API'de birleÅŸtirir.

KullanÄ±m:
    servis = OAuthServis()
    url = servis.login("google")
    token = servis.callback("google", "auth_code_here")
    durum = servis.durum("google")
    yeni_token = servis.refresh("google")
    servis.logout("google")
"""

from __future__ import annotations

import logging
from typing import Any, Optional

from reymen.guvenlik.oauth_sistemi import (
    OAuthSistemi,
    OAuthToken,
    OAuthError,
    oauth_sistemi as _varsayilan_sistem,
)

logger = logging.getLogger(__name__)

# FastAPI mevcutsa callback route'larÄ± iÃ§in yardÄ±mcÄ±
try:
    from fastapi import APIRouter, Query, HTTPException  # type: ignore[import-untyped]
    from fastapi.responses import RedirectResponse  # type: ignore[import-untyped]

    _FASTAPI_MEVCUT = True
except ImportError:
    _FASTAPI_MEVCUT = False
    APIRouter = None  # type: ignore[assignment]
    Query = None  # type: ignore[assignment]
    HTTPException = None  # type: ignore[assignment]
    RedirectResponse = None  # type: ignore[assignment]


class OAuthServis:
    """OAuth sistemi yÃ¶neticisi â€” login/callback/refresh/logout/durum.

    TÃ¼m iÅŸlemler alttaki OAuthSistemi Ã¼zerinden yÃ¼rÃ¼tÃ¼lÃ¼r.
    """

    def __init__(self, sistem: Optional[OAuthSistemi] = None):
        self._sistem = sistem or _varsayilan_sistem

    @property
    def sistem(self) -> OAuthSistemi:
        """Alttaki OAuth sistemi."""
        return self._sistem

    # â”€â”€ Ana API â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def login(self, provider: str) -> str:
        """Provider'a giriÅŸ yapmak iÃ§in auth URL'si dÃ¶ndÃ¼r.

        Args:
            provider: "google", "github", "discord"

        Returns:
            Auth URL (kullanÄ±cÄ±nÄ±n tarayÄ±cÄ±da aÃ§masÄ± gereken URL)

        Raises:
            OAuthError: Provider bulunamazsa veya hazÄ±r deÄŸilse
        """
        url = self._sistem.giris_yap(provider)
        if url is None:
            p = self._sistem.provider(provider)
            if not p.hazir:
                raise OAuthError(
                    f"[{provider.upper()}] OAuth yapÄ±landÄ±rmasÄ± eksik. "
                    f"LÃ¼tfen .env dosyasÄ±na {provider.upper()}_CLIENT_ID ve "
                    f"{provider.upper()}_CLIENT_SECRET ekleyin.",
                    provider=provider,
                    code="oauth_config_eksik",
                )
            raise OAuthError(
                f"[{provider.upper()}] Auth URL oluÅŸturulamadÄ±.",
                provider=provider,
                code="oauth_url_hatasi",
            )
        return url

    def callback(self, provider: str, code: str) -> dict[str, Any]:
        """Authorization code ile token al.

        Args:
            provider: "google", "github", "discord"
            code: Authorization code (callback URL'den gelen 'code' parametresi)

        Returns:
            Token bilgisi (dict)

        Raises:
            OAuthError: Token alÄ±namazsa
        """
        token = self._sistem.callback_islem(provider, code)
        if token is None:
            raise OAuthError(
                f"[{provider.upper()}] Authorization code ile token alÄ±namadÄ±. "
                f"Code geÃ§ersiz olabilir veya sÃ¼resi dolmuÅŸ olabilir.",
                provider=provider,
                code="oauth_token_alma_hatasi",
            )
        return {
            "basarili": True,
            "provider": provider,
            "access_token": token.access_token[:20] + "..."
            if len(token.access_token) > 20
            else token.access_token,
            "refresh_token_var": bool(token.refresh_token),
            "email": token.email,
            "display_name": token.display_name,
            "user_id": token.user_id,
            "expires_at": token.expires_at_local,
            "scope": token.scope,
        }

    def refresh(self, provider: str) -> dict[str, Any]:
        """Refresh token ile yeni access token al.

        Args:
            provider: "google", "github", "discord"

        Returns:
            Yeni token bilgisi (dict)

        Raises:
            OAuthError: Token yenilenemezse
        """
        # GitHub'da refresh_token yok â€” Ã¶zel mesaj
        if provider.lower() == "github":
            mevcut = self._sistem.token_yukle("github")
            if mevcut and not mevcut.is_expired:
                return {
                    "basarili": True,
                    "mesaj": "GitHub token'Ä± kalÄ±cÄ±dÄ±r, yenileme gerekmez.",
                    "provider": "github",
                    "durum": "geÃ§erli",
                }
            raise OAuthError(
                "[GITHUB] GitHub token'larÄ± sÃ¼resizdir, refresh_token desteÄŸi yoktur. "
                "Token silinip yeniden giriÅŸ yapÄ±labilir.",
                provider="github",
                code="github_no_refresh",
            )

        yeni_token = self._sistem.token_yenile(provider)
        if yeni_token is None:
            raise OAuthError(
                f"[{provider.upper()}] Token yenilenemedi. "
                f"Refresh token geÃ§ersiz veya sÃ¼resi dolmuÅŸ olabilir. "
                f"Tekrar giriÅŸ yapmayÄ± deneyin.",
                provider=provider,
                code="oauth_refresh_hatasi",
            )
        return {
            "basarili": True,
            "provider": provider,
            "access_token": yeni_token.access_token[:20] + "..."
            if len(yeni_token.access_token) > 20
            else yeni_token.access_token,
            "refresh_token_var": bool(yeni_token.refresh_token),
            "email": yeni_token.email,
            "display_name": yeni_token.display_name,
            "expires_at": yeni_token.expires_at_local,
        }

    def logout(self, provider: str) -> dict[str, Any]:
        """Provider'dan Ã§Ä±kÄ±ÅŸ yap (token'Ä± sil).

        Args:
            provider: "google", "github", "discord"

        Returns:
            Ä°ÅŸlem sonucu (dict)
        """
        basarili = self._sistem.cikis_yap(provider)
        return {
            "basarili": basarili,
            "provider": provider,
            "mesaj": "Ã‡Ä±kÄ±ÅŸ yapÄ±ldÄ±, token silindi."
            if basarili
            else f"[{provider.upper()}] Zaten giriÅŸ yapÄ±lmamÄ±ÅŸ.",
        }

    def durum(self, provider: str) -> dict[str, Any]:
        """Provider iÃ§in token durumunu dÃ¶ndÃ¼r.

        Args:
            provider: "google", "github", "discord"

        Returns:
            {
                "provider": "...",
                "var_mi": True/False,
                "gecerli_mi": True/False,
                "email": "...",
                "display_name": "...",
                "expires_at": "...",
            }
        """
        return self._sistem.token_durum(provider)

    def listele(self) -> list[dict[str, Any]]:
        """TÃ¼m kayÄ±tlÄ± token'larÄ± listele."""
        return self._sistem.token_listele()

    def gecerli_token_al(self, provider: str) -> Optional[OAuthToken]:
        """GeÃ§erli (sÃ¼resi dolmamÄ±ÅŸ) OAuthToken nesnesini dÃ¶ndÃ¼r.

        SÃ¼resi dolmuÅŸsa ve refresh_token varsa otomatik yeniler.
        API Ã§aÄŸrÄ±larÄ±nda access_token'Ä± kullanmak iÃ§in idealdir.

        Args:
            provider: "google", "github", "discord"

        Returns:
            OAuthToken veya None (token yoksa veya yenilenemezse)
        """
        return self._sistem.gecerli_token(provider)

    # â”€â”€ KolaylÄ±k metodlarÄ± â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def google_auth_url(self) -> str:
        """Google giriÅŸ URL'si."""
        return self.login("google")

    def github_auth_url(self) -> str:
        """GitHub giriÅŸ URL'si."""
        return self.login("github")

    def discord_auth_url(self) -> str:
        """Discord giriÅŸ URL'si."""
        return self.login("discord")

    def google_durum(self) -> dict[str, Any]:
        """Google token durumu."""
        return self.durum("google")

    def github_durum(self) -> dict[str, Any]:
        """GitHub token durumu."""
        return self.durum("github")

    def discord_durum(self) -> dict[str, Any]:
        """Discord token durumu."""
        return self.durum("discord")


# ---------------------------------------------------------------------------
# FastAPI Callback Route'larÄ± (isteÄŸe baÄŸlÄ±)
# ---------------------------------------------------------------------------


def fastapi_callback_router(servis: Optional[OAuthServis] = None) -> Any:
    """FastAPI router oluÅŸtur â€” OAuth callback'leri iÃ§in.

    KullanÄ±m (FastAPI uygulamasÄ±nda):
        from reymen.guvenlik.oauth_servis import fastapi_callback_router
        app.include_router(fastapi_callback_router())

    Route'lar:
        GET /auth/login/{provider}  -> Redirect to provider auth
        GET /auth/callback/{provider}?code=... -> Handle callback
        GET /auth/durum/{provider}  -> Token durumu
    """
    if not _FASTAPI_MEVCUT:
        raise ImportError("FastAPI kurulu deÄŸil. 'pip install fastapi' ile kurun.")

    # FastAPI varlÄ±ÄŸÄ± yukarÄ±da kontrol edildi
    from fastapi import APIRouter, Query, HTTPException
    from fastapi.responses import RedirectResponse

    servis = servis or OAuthServis()
    router = APIRouter(prefix="/auth", tags=["OAuth"])

    @router.get("/login/{provider}")
    async def login(provider: str):
        """Provider'a yÃ¶nlendir."""
        try:
            url = servis.login(provider)
            return RedirectResponse(url=url)
        except OAuthError as e:
            raise HTTPException(status_code=400, detail=str(e))

    @router.get("/callback/{provider}")
    async def callback(provider: str, code: str = Query(...), state: str = Query("")):
        """OAuth callback â€” authorization code ile token al."""
        try:
            sonuc = servis.callback(provider, code)
            return {
                "mesaj": f"{provider.upper()} giriÅŸ baÅŸarÄ±lÄ±!",
                "token": sonuc,
            }
        except OAuthError as e:
            raise HTTPException(status_code=400, detail=str(e))

    @router.get("/durum/{provider}")
    async def token_durum(provider: str):
        """Token durumunu gÃ¶ster."""
        return servis.durum(provider)

    @router.post("/refresh/{provider}")
    async def token_refresh(provider: str):
        """Token yenile."""
        try:
            return servis.refresh(provider)
        except OAuthError as e:
            raise HTTPException(status_code=400, detail=str(e))

    @router.post("/logout/{provider}")
    async def logout(provider: str):
        """Ã‡Ä±kÄ±ÅŸ yap."""
        return servis.logout(provider)

    return router


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------

oauth_servis = OAuthServis()
