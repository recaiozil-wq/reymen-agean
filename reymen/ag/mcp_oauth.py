# -*- coding: utf-8 -*-
"""mcp_oauth.py — MCP OAuth Yonetimi.

MCP sunucularina OAuth 2.0 ile guvenli baglanti.
"""

import os
import json
import requests
from pathlib import Path
import logging
logger = logging.getLogger(__name__)

OAUTH_DB = Path(__file__).parent / ".ReYMeN" / "mcp_oauth.json"


class MCPOAuth:
    def __init__(self):
        self._tokens = self._yukle()

    def _yukle(self) -> dict:
        if OAUTH_DB.exists():
            try:
                return json.loads(OAUTH_DB.read_text(encoding="utf-8"))
            except Exception as _mcp_oaut_e22:
                print(f"[UYARI] mcp_oauth.py:23 - {_mcp_oaut_e22}")
        return {}

    def _kaydet(self):
        OAUTH_DB.parent.mkdir(parents=True, exist_ok=True)
        OAUTH_DB.write_text(json.dumps(self._tokens, ensure_ascii=False, indent=2), encoding="utf-8")

    def token_al(self, sunucu: str) -> str:
        return self._tokens.get(sunucu, {}).get("access_token", "")

    def token_kaydet(self, sunucu: str, token: str):
        self._tokens[sunucu] = {"access_token": token}
        self._kaydet()

    def yetkilendir(self, auth_url: str, client_id: str, scope: str = "") -> str:
        """OAuth yetkilendirme URL'si olustur."""
        import uuid
        state = uuid.uuid4().hex[:16]
        params = f"response_type=token&client_id={client_id}&state={state}"
        if scope:
            params += f"&scope={scope}"
        return f"{auth_url}?{params}"

    def token_gecerli_mi(self, sunucu: str) -> bool:
        token = self.token_al(sunucu)
        if not token:
            return False
        try:
            import jwt
            decoded = jwt.decode(token, options={"verify_signature": False})
            import time
            return decoded.get("exp", 0) > time.time()
        except Exception:
            return bool(token)


_oauth = MCPOAuth()


def oauth_token_al(sunucu: str) -> str:
    return _oauth.token_al(sunucu)


def motor_kaydet(motor):
    """MCP OAuth araçlarını motora kaydet."""
    if not hasattr(motor, "_plugin_arac_kaydet"):
        return
    motor._plugin_arac_kaydet(
        "MCP_OAUTH_TOKEN",
        lambda sunucu="": oauth_token_al(str(sunucu)) or f"[OAuth]: {sunucu} için token yok",
        "MCP sunucu OAuth token'ını al (sunucu: sunucu adı)",
    )


if __name__ == "__main__":
    o = MCPOAuth()
    print(f"Mevcut token: {list(o._tokens.keys())}")
