"""
ReYMeN Gateway — WeCom (WeChat Work) platform adapter.

WeCom Robot Webhook + REST API uzerinden mesaj gonderir.

Kullanilan ozellikler:
  - Robot Webhook: Grup ici custom robot mesaji gonderimi (text/markdown)
  - REST API: Uygulama bazli mesaj gonderme (CorpID/AgentID/CorpSecret ile token alimi)

Yapilandirma (ortam degiskenleri):
  - WECOM_WEBHOOK_URL  — Robot webhook URL (ornek: https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxx)
  - WECOM_CORP_ID      — WeCom sirket ID (CorpID, opsiyonel, REST API icin)
  - WECOM_AGENT_ID     — WeCom uygulama AgentID (opsiyonel, REST API icin)
  - WECOM_CORP_SECRET  — WeCom uygulama CorpSecret (opsiyonel, REST API icin)
"""

import asyncio
import hashlib
import logging
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urlencode, urlparse, urlunparse

from pathlib import Path as _Path

sys.path.insert(0, str(_Path(__file__).resolve().parents[2]))

from gateways.config import Platform, PlatformConfig
from gateways.platforms.base import (
    BasePlatformAdapter,
    MessageEvent,
    MessageType,
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


def check_wecom_requirements() -> bool:
    """Check if httpx is available, attempt lazy install if not."""
    global HTTPX_AVAILABLE, httpx
    if HTTPX_AVAILABLE:
        return True
    try:
        from reymen.sistem.reymen_stubs import ensure as _lazy_ensure

        _lazy_ensure("platform.wecom", prompt=False)
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
        raise EnvironmentError(f"[WeCom] Eksik yapilandirma: {key}")
    return value


# ---------------------------------------------------------------------------
# WeCom API sabitleri
# ---------------------------------------------------------------------------

WECOM_API_BASE = "https://qyapi.weixin.qq.com"
WECOM_TOKEN_ENDPOINT = f"{WECOM_API_BASE}/cgi-bin/gettoken"
WECOM_WEBHOOK_SEND_ENDPOINT = f"{WECOM_API_BASE}/cgi-bin/webhook/send"
WECOM_APP_SEND_ENDPOINT = f"{WECOM_API_BASE}/cgi-bin/message/send"


# ---------------------------------------------------------------------------
# WeCom (WeChat Work) Adapter
# ---------------------------------------------------------------------------


class WeComAdapter(BasePlatformAdapter):
    """
    WeCom (WeChat Work) platform adapter.

    WeCom Robot Webhook ile grup mesaji gonderir.
    Opsiyonel olarak REST API (CorpID/AgentID/CorpSecret) ile uygulama bazli
    mesaj gonderme destegi saglar.
    """

    MAX_MESSAGE_LENGTH = 2048  # WeCom webhook mesaj limiti (karakter)
    supports_code_blocks = True

    def __init__(self, config: PlatformConfig):
        super().__init__(config, Platform.WECOM)
        self._webhook_url: str = _env(
            "WECOM_WEBHOOK_URL", config.extra.get("webhook_url", "")
        )
        self._corp_id: str = _env("WECOM_CORP_ID", config.extra.get("corp_id", ""))
        self._agent_id: str = _env("WECOM_AGENT_ID", config.extra.get("agent_id", ""))
        self._corp_secret: str = _env(
            "WECOM_CORP_SECRET", config.extra.get("corp_secret", "")
        )

        self._client: Optional[httpx.AsyncClient] = None
        self._access_token: Optional[str] = None
        self._token_expires_at: float = 0.0

    # ── HTTP Istemci Yonetimi ─────────────────────────────────────────

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create the HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=30.0)
        return self._client

    # ── Baglanti Yonetimi ────────────────────────────────────────────

    async def connect(self) -> bool:
        """
        WeCom baglantisini dogrula.

        Webhook URL'si varsa baglanti basarili sayilir.
        CorpID/AgentID/CorpSecret varsa REST API token almayi dener (opsiyonel).
        """
        if not check_wecom_requirements():
            logger.error("[WeCom] httpx kurulu degil.")
            return False

        # En az bir gonderim yontemi olmali
        has_webhook = bool(self._webhook_url)
        has_api_creds = bool(self._corp_id and self._agent_id and self._corp_secret)

        if not has_webhook and not has_api_creds:
            logger.error(
                "[WeCom] Hicbir gonderim yontemi yapilandirilmamis. "
                "WECOM_WEBHOOK_URL veya (WECOM_CORP_ID + WECOM_AGENT_ID + WECOM_CORP_SECRET) gereklidir."
            )
            return False

        # Webhook URL formatini dogrula
        if (
            has_webhook
            and "key=" not in self._webhook_url
            and "/webhook/send" not in self._webhook_url
        ):
            logger.warning(
                "[WeCom] Webhook URL formatinda 'key' parametresi bulunamadi. "
                "URL ornegi: https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxx"
            )

        # Opsiyonel: REST API token al
        if has_api_creds:
            try:
                await self._refresh_access_token()
            except Exception as e:
                logger.warning(
                    "[WeCom] REST API token alinamadi (devam ediliyor): %s", e
                )

        logger.info(
            "[WeCom] Hazir (Webhook: %s, REST API: %s)",
            "var" if has_webhook else "yok",
            "var" if self._access_token else "yok",
        )
        self._mark_connected()
        return True

    async def disconnect(self) -> None:
        """WeCom HTTP baglantisini kapat."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None
            logger.info("[WeCom] Baglanti kapatildi.")

    async def _refresh_access_token(self) -> str:
        """
        WeCom REST API access token al (CorpID/CorpSecret ile).

        GET https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid=xxx&corpsecret=yyy

        Returns:
            Access token string.

        Raises:
            RuntimeError: CorpID veya CorpSecret eksikse ya da API hatasi olursa.
        """
        if not self._corp_id or not self._corp_secret:
            raise RuntimeError("[WeCom] CorpID/CorpSecret eksik.")

        # Token hala gecerliyse yeniden alma
        if self._access_token and time.time() < self._token_expires_at - 60:
            return self._access_token

        client = await self._get_client()
        resp = await client.get(
            WECOM_TOKEN_ENDPOINT,
            params={
                "corpid": self._corp_id,
                "corpsecret": self._corp_secret,
            },
        )
        resp.raise_for_status()
        data = resp.json()

        if data.get("errcode") != 0:
            raise RuntimeError(
                f"[WeCom] Token hatasi: {data.get('errcode')} - {data.get('errmsg', '')}"
            )

        self._access_token = data.get("access_token", "")
        expires_in = data.get("expires_in", 7200)
        self._token_expires_at = time.time() + expires_in
        logger.info("[WeCom] REST API token alindi (gecerlilik: %ds).", expires_in)
        return self._access_token

    # ── Mesaj Gonderme ───────────────────────────────────────────────

    async def send_message(
        self,
        chat_id: str,
        text: str,
        *,
        reply_to: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> SendResult:
        """
        WeCom Robot webhook'una mesaj gonder.

        Oncelik sirasi:
          1. Webhook URL (WECOM_WEBHOOK_URL) varsa robot webhook uzerinden gonderilir
          2. Yoksa ve REST API yapilandirilmissa uygulama mesaji olarak gonderilir

        Args:
            chat_id: Webhook modunda kullanilmaz (webhook URL'si zaten hedef grubu
                     belirler). REST API modunda hedef kullanici/grup ID'si olarak
                     kullanilir.
            text: Mesaj icerigi (Markdown formatinda destegi).
            reply_to: Kullanilmaz (WeCom Robot Webhook thread yaniti desteklemez).
                      Uyumluluk amaciyla bulunur.
            metadata: Ek opsiyonlar.
                      - msg_type: "text" | "markdown" (varsayilan: markdown)
                      - chat_type: "user" | "group" (REST API icin, varsayilan: "group")
                      - safe: int (0/1, REST API icin)

        Returns:
            SendResult
        """
        if not HTTPX_AVAILABLE:
            return SendResult(False, error="httpx kurulu degil")

        if not text:
            return SendResult(False, error="Mesaj icerigi bos")

        msg_type = (metadata or {}).get("msg_type", "markdown")

        # Webhook yontemi ile gonder (oncecelikli)
        if self._webhook_url:
            return await self._send_via_webhook(text, msg_type, metadata)

        # REST API yontemi ile gonder
        if self._corp_id and self._agent_id and self._corp_secret:
            return await self._send_via_api(chat_id, text, msg_type, metadata)

        return SendResult(
            False,
            error="Hicbir gonderim yontemi yapilandirilmamis "
            "(WECOM_WEBHOOK_URL veya WECOM_CORP_ID+WECOM_AGENT_ID+WECOM_CORP_SECRET)",
        )

    async def _send_via_webhook(
        self,
        text: str,
        msg_type: str,
        metadata: Optional[dict] = None,
    ) -> SendResult:
        """
        WeCom Robot Webhook uzerinden mesaj gonder.

        POST https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxx
        """
        try:
            client = await self._get_client()

            # Mesaj payload'ini olustur
            payload: Dict[str, Any]

            if msg_type == "markdown":
                payload = {
                    "msgtype": "markdown",
                    "markdown": {
                        "content": text,
                    },
                }
            else:
                payload = {
                    "msgtype": "text",
                    "text": {
                        "content": text,
                    },
                }

                # @ mention destegi (sadece text mesajinda)
                mentioned_list = (metadata or {}).get("mentioned_list", [])
                if mentioned_list:
                    payload["text"]["mentioned_list"] = mentioned_list

                at_all = (metadata or {}).get("at_all", False)
                if at_all:
                    payload["text"]["mentioned_list"] = ["@all"]

            resp = await client.post(
                self._webhook_url,
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()

            # WeCom API hata kodlarini kontrol et
            errcode = data.get("errcode", -1)
            if errcode != 0:
                errmsg = data.get("errmsg", "Bilinmeyen hata")
                logger.error(
                    "[WeCom] Robot webhook API hatasi (%d): %s", errcode, errmsg
                )
                return SendResult(
                    False,
                    error=f"WeCom webhook API hatasi: {errmsg}",
                    retryable=errcode in (90002, 90006, 90010, 301002, 301003),
                )

            return SendResult(
                success=True,
                message_id=str(data.get("msgid", "")),
                raw_response=data,
            )

        except httpx.HTTPStatusError as e:
            error_msg = str(e)
            status = e.response.status_code if e.response else 0
            logger.error("[WeCom] Webhook HTTP hatasi (%d): %s", status, error_msg)
            return SendResult(
                False,
                error=error_msg,
                retryable=status in (429, 500, 502, 503, 504),
            )

        except httpx.RequestError as e:
            logger.error("[WeCom] Webhook istemci hatasi: %s", e)
            return SendResult(False, error=str(e), retryable=True)

        except Exception as e:
            logger.error("[WeCom] Webhook beklenmeyen gonderim hatasi: %s", e)
            return SendResult(False, error=str(e))

    async def _send_via_api(
        self,
        chat_id: str,
        text: str,
        msg_type: str,
        metadata: Optional[dict] = None,
    ) -> SendResult:
        """
        WeCom REST API uzerinden uygulama mesaji gonder.

        POST https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=xxx
        """
        try:
            token = await self._refresh_access_token()
            client = await self._get_client()

            # Hedef belirleme
            chat_type = (metadata or {}).get("chat_type", "group")
            to_param: Dict[str, Any]

            if chat_type == "user":
                to_param = {"touser": chat_id}
            else:
                to_param = {"touser": "@all"} if not chat_id else {"touser": chat_id}

            safe = (metadata or {}).get("safe", 0)

            # Mesaj payload'ini olustur
            payload: Dict[str, Any] = {
                **to_param,
                "msgtype": msg_type,
                "agentid": int(self._agent_id)
                if self._agent_id.isdigit()
                else self._agent_id,
                "safe": safe,
            }

            if msg_type == "markdown":
                payload["markdown"] = {
                    "content": text,
                }
            else:
                payload["text"] = {
                    "content": text,
                }

            resp = await client.post(
                WECOM_APP_SEND_ENDPOINT,
                params={"access_token": token},
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()

            errcode = data.get("errcode", -1)
            if errcode != 0:
                errmsg = data.get("errmsg", "Bilinmeyen hata")
                logger.error("[WeCom] REST API hatasi (%d): %s", errcode, errmsg)
                return SendResult(
                    False,
                    error=f"WeCom API hatasi: {errmsg}",
                    retryable=errcode in (90002, 90006, 90010, 40014, 41001, 42001),
                )

            return SendResult(
                success=True,
                message_id=str(data.get("msgid", "")),
                raw_response=data,
            )

        except httpx.HTTPStatusError as e:
            error_msg = str(e)
            status = e.response.status_code if e.response else 0
            logger.error("[WeCom] REST API HTTP hatasi (%d): %s", status, error_msg)
            return SendResult(
                False,
                error=error_msg,
                retryable=status in (429, 500, 502, 503, 504),
            )

        except httpx.RequestError as e:
            logger.error("[WeCom] REST API istemci hatasi: %s", e)
            return SendResult(False, error=str(e), retryable=True)

        except Exception as e:
            logger.error("[WeCom] REST API beklenmeyen gonderim hatasi: %s", e)
            return SendResult(False, error=str(e))

    async def send_typing(
        self, chat_id: str, metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        WeCom yaziyor gostergesi (no-op).

        WeCom Robot Webhook ve REST API, typing indicator desteklemez.
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
        WeCom mesaj duzenleme (desteklenmiyor).

        WeCom Robot Webhook ve REST API uzerinden gonderilen mesajlar
        duzenlenemez.
        """
        return SendResult(False, error="WeCom mesaj duzenleme desteklemez")

    async def delete_message(
        self,
        chat_id: str,
        message_id: str,
    ) -> bool:
        """
        WeCom mesaj silme (desteklenmiyor).

        WeCom Robot Webhook uzerinden gonderilen mesajlar silinemez.
        """
        return False

    # ── BasePlatformAdapter soyut metotlari ──────────────────────────

    async def send(
        self,
        chat_id: str,
        content: str,
        reply_to: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> SendResult:
        """
        Send metodu — send_message'e yonlendirir.

        BasePlatformAdapter.soyut metot zorunlulugunu karsilar.
        """
        return await self.send_message(
            chat_id=chat_id,
            text=content,
            reply_to=reply_to,
            metadata=metadata,
        )

    async def get_chat_info(self, chat_id: str) -> Dict[str, Any]:
        """
        Sohbet bilgisi dondurur.

        WeCom Robot Webhook sohbet bilgisi sorgulama desteklemez;
        REST API ile sorgulama da bu adapterin kapsami disindadir.
        Temel bilgilerle dummy bir yanit doner.
        """
        return {
            "name": chat_id or "WeCom Chat",
            "type": "group",
            "platform": "wecom",
        }
