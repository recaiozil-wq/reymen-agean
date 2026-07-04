"""
ReYMeN Gateway — Feishu/Lark platform adapter.

Feishu Open API (https://open.feishu.cn) üzerinden mesaj gonderme.

Kullanilan Feishu Open API endpoint'leri:
  - Token: POST /open-apis/auth/v3/tenant_access_token/internal
  - Mesaj: POST /open-apis/im/v1/messages

Yapilandirma (ortam degiskenleri):
  - FEISHU_APP_ID      — Feishu uygulama App ID (zorunlu)
  - FEISHU_APP_SECRET  — Feishu uygulama App Secret (zorunlu)
"""

import asyncio
import json
import logging
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable, Awaitable

from pathlib import Path as _Path
sys.path.insert(0, str(_Path(__file__).resolve().parents[2]))

from src.gateways.config import Platform, PlatformConfig
from src.gateways.platforms.base import (
    BasePlatformAdapter,
    MessageEvent,
    MessageType,
    ProcessingOutcome,
    SendResult,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Bagimlilik kontrolu
# ---------------------------------------------------------------------------

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False
    httpx = None  # type: ignore[assignment]


def check_feishu_requirements() -> bool:
    """Check if httpx is available, attempt lazy install if not."""
    global HTTPX_AVAILABLE, httpx
    if HTTPX_AVAILABLE:
        return True
    try:
        from reymen.cron.hermes_stubs import ensure as _lazy_ensure
        _lazy_ensure("platform.feishu", prompt=False)
    except Exception:
        return False
    try:
        import httpx as _httpx
        httpx = _httpx
        HTTPX_AVAILABLE = True
        return True
    except ImportError:
        return False


def _env(key: str, default: str = "") -> str:
    return os.environ.get(key, default).strip()


def _env_required(key: str) -> str:
    value = _env(key)
    if not value:
        raise EnvironmentError(f"[Feishu] Eksik yapilandirma: {key}")
    return value


# ---------------------------------------------------------------------------
# Feishu Open API sabitleri
# ---------------------------------------------------------------------------

FEISHU_BASE_URL = "https://open.feishu.cn"
FEISHU_TOKEN_URL = f"{FEISHU_BASE_URL}/open-apis/auth/v3/tenant_access_token/internal"
FEISHU_SEND_URL = f"{FEISHU_BASE_URL}/open-apis/im/v1/messages"


# ---------------------------------------------------------------------------
# Feishu Adapter
# ---------------------------------------------------------------------------


class FeishuAdapter(BasePlatformAdapter):
    """
    Feishu (Lark) platform adapter.

    Feishu Open API kullanarak tenant_access_token alir ve
    open_id bazli mesaj gonderimi yapar.
    """

    MAX_MESSAGE_LENGTH = 30000  # Feishu mesaj limiti (karakter)
    supports_code_blocks = False
    typed_command_prefix = "/"

    def __init__(self, config: PlatformConfig):
        super().__init__(config, Platform.FEISHU)
        self._app_id: str = _env("FEISHU_APP_ID", config.extra.get("app_id", ""))
        self._app_secret: str = _env("FEISHU_APP_SECRET", config.extra.get("app_secret", ""))

        self._client: Optional[httpx.AsyncClient] = None
        self._tenant_access_token: Optional[str] = None
        self._token_expires_at: float = 0.0  # Unix timestamp (saniye)

    # ── HTTP Istemci Yonetimi ─────────────────────────────────────────

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create the HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=30.0)
        return self._client

    # ── Token Yonetimi ────────────────────────────────────────────────

    async def _ensure_token(self) -> str:
        """Gecerli bir tenant_access_token dondur, gerekiyorsa yenile.

        Returns:
            Gecerli tenant_access_token string'i.

        Raises:
            RuntimeError: Token alinamazsa.
        """
        # Token hala gecerliyse (5 dk buffer birak)
        if self._tenant_access_token and time.time() < self._token_expires_at - 300:
            return self._tenant_access_token

        await self._refresh_tenant_access_token()
        assert self._tenant_access_token is not None
        return self._tenant_access_token

    async def _refresh_tenant_access_token(self) -> str:
        """Feishu tenant_access_token al (internal app).

        POST https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal

        Request body:
            {
                "app_id": "...",
                "app_secret": "..."
            }

        Response:
            {
                "code": 0,
                "msg": "ok",
                "tenant_access_token": "...",
                "expire": 7200
            }

        Returns:
            Tenant access token string.

        Raises:
            RuntimeError: App ID veya App Secret eksikse ya da API hatasi olursa.
        """
        if not self._app_id or not self._app_secret:
            raise RuntimeError("[Feishu] FEISHU_APP_ID / FEISHU_APP_SECRET eksik.")

        client = await self._get_client()
        payload = {
            "app_id": self._app_id,
            "app_secret": self._app_secret,
        }

        logger.info("[Feishu] Tenant access token aliniyor...")
        resp = await client.post(FEISHU_TOKEN_URL, json=payload)
        resp.raise_for_status()
        data = resp.json()

        code = data.get("code", -1)
        if code != 0:
            msg = data.get("msg", "Bilinmeyen hata")
            raise RuntimeError(f"[Feishu] Token hatasi (code={code}): {msg}")

        self._tenant_access_token = data["tenant_access_token"]
        expire_seconds = data.get("expire", 7200)
        self._token_expires_at = time.time() + expire_seconds

        logger.info(
            "[Feishu] Tenant access token alindi (%d sn gecerli).",
            expire_seconds,
        )
        return self._tenant_access_token

    # ── Baglanti Yonetimi ────────────────────────────────────────────

    async def connect(self) -> bool:
        """
        Feishu baglantisini dogrula.

        FEISHU_APP_ID ve FEISHU_APP_SECRET ile tenant_access_token almayi dener.
        """
        if not check_feishu_requirements():
            logger.error("[Feishu] httpx kurulu degil.")
            return False

        if not self._app_id:
            logger.error("[Feishu] FEISHU_APP_ID eksik.")
            return False

        if not self._app_secret:
            logger.error("[Feishu] FEISHU_APP_SECRET eksik.")
            return False

        try:
            await self._refresh_tenant_access_token()
        except Exception as e:
            logger.error("[Feishu] Baglanti basarisiz: %s", e)
            return False

        logger.info(
            "[Feishu] Hazir (App ID: %s, Token: %s)",
            self._app_id[:8] + "..." if len(self._app_id) > 8 else self._app_id,
            "var" if self._tenant_access_token else "yok",
        )
        self._mark_connected()
        return True

    async def disconnect(self) -> None:
        """Feishu HTTP baglantisini kapat."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None
            self._tenant_access_token = None
            self._token_expires_at = 0.0
            logger.info("[Feishu] Baglanti kapatildi.")

    # ── Mesaj Gonderme ───────────────────────────────────────────────

    async def send(
        self,
        chat_id: str,
        content: str,
        reply_to: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> SendResult:
        """
        Feishu kullanicisina mesaj gonder (open_id ile).

        POST https://open.feishu.cn/open-apis/im/v1/messages

        Args:
            chat_id: Alicinin open_id'si (kullanici veya grup).
            content: Mesaj icerigi (duz metin veya JSON formatinda).
            reply_to: Opsiyonel, yanitlanan mesajin ID'si.
            metadata: ``msg_type`` (``"text"`` (varsayilan) / ``"post"`` / ``"interactive"``)
                      ve ``receive_id_type`` (``"open_id"`` (varsayilan) / ``"chat_id"``)
                      gibi ek opsiyonlar.

        Returns:
            SendResult.
        """
        if not HTTPX_AVAILABLE:
            return SendResult(success=False, error="httpx kurulu degil")

        if not content:
            return SendResult(success=False, error="Mesaj icerigi bos")

        if not self._tenant_access_token:
            return SendResult(
                success=False,
                error="tenant_access_token alinamamis, once connect() cagrilmali",
                retryable=True,
            )

        try:
            token = await self._ensure_token()
            client = await self._get_client()

            # Mesaj tipi: varsayilan "text"
            msg_type = (metadata or {}).get("msg_type", "text")
            receive_id_type = (metadata or {}).get("receive_id_type", "open_id")

            # Icerik: msg_type="text" icin JSON formatinda {"text":"..."}
            if msg_type == "text":
                content_json = json.dumps({"text": content}, ensure_ascii=False)
            else:
                # post, interactive gibi diger formatlar
                content_json = content

            payload: Dict[str, Any] = {
                "receive_id": chat_id,
                "msg_type": msg_type,
                "content": content_json,
            }

            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json; charset=utf-8",
            }

            params: Dict[str, str] = {
                "receive_id_type": receive_id_type,
            }

            # Yanit (thread) destegi
            if reply_to:
                payload["reply_in_thread"] = True
                # Feishu icin UUID formatinda message_id

            resp = await client.post(
                FEISHU_SEND_URL,
                params=params,
                json=payload,
                headers=headers,
                timeout=30.0,
            )
            resp.raise_for_status()
            data = resp.json()

            code = data.get("code", -1)
            if code != 0:
                msg = data.get("msg", "Bilinmeyen hata")
                logger.error(
                    "[Feishu] API hatasi (code=%d): %s",
                    code,
                    msg,
                )
                # Token suresi dolmus olabilir, yenilemeyi dene
                retryable = code in (99991663, 99991664, 99991668)  # token-related hatalar
                if retryable:
                    self._tenant_access_token = None
                return SendResult(
                    success=False,
                    error=f"Feishu API hatasi (code={code}): {msg}",
                    retryable=retryable,
                )

            # Basarili gonderim
            message_id = (
                data.get("data", {}).get("message_id", "")
                or data.get("data", {}).get("msg_id", "")
                or ""
            )
            return SendResult(
                success=True,
                message_id=str(message_id) if message_id else None,
                raw_response=data,
            )

        except httpx.HTTPStatusError as e:
            error_body = ""
            try:
                error_body = str(e.response.text)
            except Exception:
                pass
            status = e.response.status_code if e.response else 0
            error_msg = f"HTTP {status}: {error_body or str(e)}"
            logger.error("[Feishu] Gonderim HTTP hatasi: %s", error_msg)
            return SendResult(
                success=False,
                error=error_msg,
                retryable=status in (429, 500, 502, 503, 504),
            )

        except httpx.RequestError as e:
            logger.error("[Feishu] Gonderim baglanti hatasi: %s", e)
            return SendResult(success=False, error=str(e), retryable=True)

        except Exception as e:
            logger.error("[Feishu] Beklenmeyen gonderim hatasi: %s", e)
            return SendResult(success=False, error=str(e))

    async def send_typing(
        self, chat_id: str, metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Feishu yaziyor gostergesi (no-op).

        Feishu Open API su an icin typing indicator desteklemez.
        """
        pass

    async def edit_message(
        self,
        chat_id: str,
        message_id: str,
        content: str,
        *,
        finalize: bool = False,
    ) -> SendResult:
        """
        Feishu mesaj duzenleme (desteklenmiyor).

        Feishu Open API'nin mesaj duzenleme endpoint'i
        su an icin bu adapterde implemente edilmemistir.
        """
        return SendResult(success=False, error="Feishu mesaj duzenleme desteklemez")

    async def delete_message(
        self,
        chat_id: str,
        message_id: str,
    ) -> bool:
        """
        Feishu mesaj silme (desteklenmiyor).

        Feishu Open API mesaj silme endpoint'i opsiyoneldir;
        su an icin bu adapterde implemente edilmemistir.
        """
        return False

    # ── Chat Bilgisi ──────────────────────────────────────────────────

    async def get_chat_info(self, chat_id: str) -> Dict[str, Any]:
        """
        Feishu kullanici/grup bilgisi al.

        Args:
            chat_id: open_id veya chat_id.

        Returns:
            Dict ile:
            - name: Kullanici/grup adi
            - type: "dm" | "group" (su an icin varsayilan doner)
        """
        # Feishu Open API'den chat bilgisi almak icin
        # GET /open-apis/im/v1/chats/:chat_id endpoint'i kullanilabilir.
        # Su an icin basit bir varsayilan donuyor.
        logger.warning(
            "[Feishu] get_chat_info su an icin sinirli bilgi donuyor (chat_id=%s)",
            chat_id,
        )
        return {
            "name": chat_id,
            "type": "dm",  # open_id ise dm, chat_id ise grup olabilir
        }
