# -*- coding: utf-8 -*-
"""Google OAuth 2.0 — Google API'lerine erisim icin kimlik dogrulama.

Hermes agent/google_oauth.py'den adapte edilmistir.
"""
from __future__ import annotations
import logging
import os
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class GoogleOAuth:
    """Google OAuth 2.0 yonetimi."""

    def __init__(self, client_id: str = "", client_secret: str = ""):
        self.client_id = client_id or os.environ.get("GOOGLE_CLIENT_ID", "")
        self.client_secret = client_secret or os.environ.get("GOOGLE_CLIENT_SECRET", "")
        self._token: Optional[Dict] = None

    def is_configured(self) -> bool:
        return bool(self.client_id and self.client_secret)

    def get_access_token(self) -> Optional[str]:
        try:
            from google.oauth2.credentials import Credentials
            from google.auth.transport.requests import Request

            if self._token:
                creds = Credentials.from_authorized_user_info(self._token)
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                    self._token = {"token": creds.token, "refresh_token": creds.refresh_token}
                return creds.token if creds else None
            return None
        except Exception as e:
            logger.debug("Google OAuth hatasi: %s", e)
            return None

    def has_token(self) -> bool:
        return self._token is not None
