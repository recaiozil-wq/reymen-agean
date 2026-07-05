# -*- coding: utf-8 -*-
"""
api_server.py â€” OpenAI-uyumlu REST API sunucusu.

ReYMeN altyapÃ½sÃ½nÃ½ (Beyin) FastAPI üzerinden OpenAI uyumlu bir API
olarak sunar. Streaming (SSE) ve non-streaming chat completions,
model listeleme ve saÃ°lÃ½k kontrolü endpoint'leri içerir.

KullanÃ½m:
    python -m reymen.api_server --port 8000
    python -m reymen.api_server --port 8000 --host 0.0.0.0 --no-auth

BaÃ°Ã½mlÃ½lÃ½klar:
    fastapi>=0.110.0
    uvicorn[standard]>=0.29.0
    pyyaml>=6.0
    python-dotenv>=1.0.0
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import time
import uuid
from pathlib import Path
from typing import Any, AsyncGenerator, Optional

logger = logging.getLogger("reymen.api_server")

# â”€â”€ Proje kökü (config.yaml ve .env'nin bulunduÃ°u yer) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
_PROJE_KOKU = Path(__file__).resolve().parent.parent
_CONFIG_YOLU = _PROJE_KOKU / "config.yaml"
_ENV_YOLU = _PROJE_KOKU / ".env"


# â”€â”€ FastAPI ve Starlette içe aktar â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import StreamingResponse
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_500_INTERNAL_SERVER_ERROR

# â”€â”€ Pydantic Ã¾emalarÃ½ â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
from pydantic import BaseModel, Field


class ChatCompletionRequest(BaseModel):
    """OpenAI /v1/chat/completions istek Ã¾emasÃ½."""

    model: Optional[str] = None
    messages: list[dict] = Field(..., description="KonuÃ¾ma mesajlarÃ½")
    stream: bool = False
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    top_p: Optional[float] = None
    frequency_penalty: Optional[float] = None
    presence_penalty: Optional[float] = None
    stop: Optional[list[str] | str] = None
    user: Optional[str] = None


class ChatCompletionMessage(BaseModel):
    """OpenAI yanÃ½t mesajÃ½."""

    role: str = "assistant"
    content: str = ""


class ChatCompletionChoice(BaseModel):
    """OpenAI yanÃ½t seçeneÃ°i."""

    index: int = 0
    message: ChatCompletionMessage
    finish_reason: str = "stop"


class ChatCompletionUsage(BaseModel):
    """OpenAI kullanÃ½m istatistiÃ°i."""

    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


class ChatCompletionResponse(BaseModel):
    """OpenAI /v1/chat/completions yanÃ½t Ã¾emasÃ½."""

    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: list[ChatCompletionChoice]
    usage: ChatCompletionUsage = ChatCompletionUsage()


class ModelPermission(BaseModel):
    """Model izin Ã¾emasÃ½ (OpenAI uyumluluÃ°u için)."""

    id: str = ""
    object: str = "model_permission"
    created: int = 0
    allow_create_engine: bool = False
    allow_sampling: bool = True
    allow_logprobs: bool = False
    allow_search_indices: bool = False
    allow_view: bool = True
    allow_fine_tuning: bool = False
    organization: str = "*"
    group: Optional[str] = None
    is_blocking: bool = False


class ModelObject(BaseModel):
    """OpenAI model nesnesi."""

    id: str
    object: str = "model"
    created: int = 0
    owned_by: str = "reymen"
    permission: list[ModelPermission] = []


class ModelList(BaseModel):
    """GET /v1/models yanÃ½tÃ½."""

    object: str = "list"
    data: list[ModelObject]


# â”€â”€ VarsayÃ½lan modeller (Beyin'den çek) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
try:
    from reymen.cereyan.beyin import _VARSAYILAN_MODELLER as _BEYIN_VARSAYILAN_MODELLER
except ImportError:
    _BEYIN_VARSAYILAN_MODELLER = {}


# â”€â”€ Config yükleyici â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def _config_yukle() -> dict[str, Any]:
    """config.yaml'i okuyup Beyin için uygun formata çevirir.

    config.yaml'deki ``fallback_providers`` listesini
    ``providers`` sözlüÃ°üne dönüÃ¾türür.
    """
    try:
        import yaml as _yaml
    except ImportError:
        raise ImportError("pyyaml kurulu deÃ°il. 'pip install pyyaml' ile kur.")

    if not _CONFIG_YOLU.exists():
        logger.warning(
            "config.yaml bulunamadÃ½: %s â€” varsayÃ½lan config kullanÃ½lÃ½yor.", _CONFIG_YOLU
        )
        return {
            "default_provider": "deepseek",
            "default_model": "deepseek-v4-flash",
            "providers": {},
        }

    with open(_CONFIG_YOLU, "r", encoding="utf-8") as f:
        raw: dict = _yaml.safe_load(f) or {}

    # Ana config'den provider/default model
    provider = raw.get("model", {}).get("provider") or raw.get("provider", "deepseek")
    model = raw.get("model", {}).get("default") or raw.get("general", {}).get(
        "default_model", "deepseek-v4-flash"
    )

    # fallback_providers â†’ providers dict
    providers: dict[str, dict[str, str]] = {}
    for fb in raw.get("fallback_providers", []):
        pname = fb.get("provider", "")
        if pname:
            providers[pname] = {
                "base_url": fb.get("base_url", ""),
                "api_key": "",  # runtime'da env'den okunur
            }

    # providers varsa üstüne yaz
    providers.update(raw.get("providers", {}))

    return {
        "default_provider": provider,
        "default_model": model,
        "providers": providers,
        "fallback_model": raw.get("fallback_model"),
        "general": raw.get("general", {}),
    }


# â”€â”€ .env yükleyici â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def _env_yukle() -> None:
    """.env dosyasÃ½nÃ½ ortam deÃ°iÃ¾kenlerine yükle."""
    try:
        from dotenv import load_dotenv

        load_dotenv(_ENV_YOLU, override=True)
        logger.info(".env yüklendi: %s", _ENV_YOLU)
    except ImportError:
        logger.debug("python-dotenv yok, .env yüklenmedi.")
    except Exception as e:
        logger.warning(".env yüklenirken hata: %s", e)


# â”€â”€ API anahtarÃ½ doÃ°rulayÃ½cÃ½ â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def _api_key_kontrol(request: Request) -> str | None:
    """Ãstekten API anahtarÃ½nÃ½ çÃ½kar; doÃ°rulama kapalÃ½ysa None döndür.

    SÃ½rasÃ½yla: Authorization header â†’ X-API-Key header â†’ query param.
    """
    auth = request.headers.get("Authorization", "")
    if auth.lower().startswith("bearer "):
        return auth[7:].strip()
    x_key = request.headers.get("X-API-Key", "")
    if x_key:
        return x_key.strip()
    query_key = request.query_params.get("api_key", "")
    if query_key:
        return query_key.strip()
    return None


# â”€â”€ API Sunucusu SÃ½nÃ½fÃ½ â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
class APIServer:
    """OpenAI-uyumlu REST API sunucusu.

    ReYMeN'in :class:`reymen.cereyan.beyin.Beyin` altyapÃ½sÃ½nÃ½
    FastAPI üzerinden OpenAI uyumlu bir arayüzle dÃ½Ã¾arÃ½ya açar.

    Ã–zellikler:
        * GET /v1/models â€” modelleri listele
        * POST /v1/chat/completions â€” chat tamamlama (streaming + non-streaming)
        * GET /health â€” saÃ°lÃ½k kontrolü
        * CORS desteÃ°i
        * ÃsteÃ°e baÃ°lÃ½ API anahtarÃ½ korumasÃ½ (Authorization: Bearer)
        * SSE streaming (Server-Sent Events)

    KullanÃ½m:
        >>> server = APIServer(port=8000, host="127.0.0.1")
        >>> server.run()
    """

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 8000,
        api_key_required: bool = True,
        log_level: str = "INFO",
    ) -> None:
        """API sunucusunu baÃ¾lat.

        Args:
            host: Dinlenecek aÃ° arayüzü.
            port: Dinlenecek port.
            api_key_required: True ise .env'deki API_KEY ile koru.
            log_level: Log seviyesi (DEBUG, INFO, WARNING, ERROR).
        """
        self.host = host
        self.port = port
        self.api_key_required = api_key_required
        # .env'yi önceden yükle ki API_KEY okunabilsin
        _env_yukle()
        self._api_key = os.environ.get("API_KEY", "")

        # Loglama
        logging.basicConfig(
            level=getattr(logging, log_level.upper(), logging.INFO),
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        # Config yükle
        self._beyin_config = _config_yukle()

        # Beyin örneÃ°i (lazy)
        self._beyin: Any = None

        # FastAPI uygulamasÃ½
        self.app = FastAPI(
            title="ReYMeN API",
            description="ReYMeN AI AsistanÃ½ â€” OpenAI-uyumlu REST API",
            version="0.1.0",
            docs_url="/docs",
            redoc_url="/redoc",
        )

        self._kayit_et()

    def _beyin_al(self) -> Any:
        """Beyin örneÃ°ini lazy-load ile al.

        Thread-safe deÃ°ildir; tek thread'li uvicorn için yeterlidir.
        """
        if self._beyin is None:
            try:
                from reymen.cereyan.beyin import Beyin

                self._beyin = Beyin(config=self._beyin_config)
                logger.info(
                    "Beyin baÃ¾latÃ½ldÃ½: provider=%s model=%s",
                    self._beyin.provider,
                    self._beyin.model,
                )
            except Exception as e:
                logger.error("Beyin baÃ¾latÃ½lamadÃ½: %s", e)
                raise RuntimeError(f"Beyin baÃ¾latÃ½lamadÃ½: {e}") from e
        return self._beyin

    def _dogrula(self, request: Request) -> None:
        """API anahtarÃ½ doÃ°rulamasÃ½ yap (isteÃ°e baÃ°lÃ½).

        Raises:
            HTTPException: Anahtar geçersiz veya eksikse 401.
        """
        if not self.api_key_required or not self._api_key:
            return

        gelen = _api_key_kontrol(request)
        if not gelen:
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail="API anahtarÃ½ gerekli. Authorization: Bearer *** kullanÃ½n.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if gelen != self._api_key:
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail="API anahtarÃ½ geçersiz.",
                headers={"WWW-Authenticate": "Bearer"},
            )

    def _kayit_et(self) -> None:
        """Tüm endpoint'leri FastAPI uygulamasÃ½na kaydet."""

        # â”€â”€ SaÃ°lÃ½k kontrolü â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        @self.app.get("/health")
        async def health(request: Request) -> dict:
            """SaÃ°lÃ½k kontrolü endpoint'i.

            Beyin örneÃ°inin canlÃ½ olup olmadÃ½Ã°Ã½nÃ½ kontrol eder.

            Returns:
                {"status": "ok", "provider": ..., "model": ...}
            """
            try:
                beyin = self._beyin_al()
                return {
                    "status": "ok",
                    "provider": beyin.provider,
                    "model": beyin.model,
                    "timestamp": int(time.time()),
                }
            except Exception as e:
                raise HTTPException(
                    status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"SaÃ°lÃ½k kontrolü baÃ¾arÃ½sÃ½z: {e}",
                )

        # â”€â”€ Modelleri listele â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        @self.app.get("/v1/models")
        async def list_models(request: Request) -> ModelList:
            """KullanÃ½labilir modelleri listele.

            Config'deki tüm saÃ°layÃ½cÃ½/modelleri OpenAI formatÃ½nda döndürür.
            """
            self._dogrula(request)
            modeller: list[ModelObject] = []
            suan = int(time.time())

            cfg = self._beyin_config
            birincil_provider = cfg.get("default_provider", "deepseek")
            birincil_model = cfg.get("default_model", "deepseek-v4-flash")

            # Birincil model
            modeller.append(
                ModelObject(
                    id=f"{birincil_provider}/{birincil_model}",
                    created=suan,
                    owned_by=birincil_provider,
                )
            )

            # Fallback provider'lardaki modeller
            for pname in cfg.get("providers", {}):
                # VarsayÃ½lan model
                pmid = _BEYIN_VARSAYILAN_MODELLER.get(pname, f"{pname}/default")
                mid = f"{pname}/{pmid}"
                if mid not in {m.id for m in modeller}:
                    modeller.append(
                        ModelObject(
                            id=mid,
                            created=suan,
                            owned_by=pname,
                        )
                    )

            return ModelList(data=modeller)

        # â”€â”€ Chat Completions â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        @self.app.post("/v1/chat/completions")
        async def chat_completions(
            request: Request,
            body: ChatCompletionRequest,
        ) -> Any:
            """OpenAI-uyumlu chat completions endpoint'i.

            Streaming (SSE) ve non-streaming modlarÃ½ destekler.

            Args:
                body: OpenAI uyumlu istek gövdesi.

            Returns:
                StreamingResponse (SSE) veya ChatCompletionResponse (JSON).
            """
            self._dogrula(request)
            beyin = self._beyin_al()

            # Model/provider seçimi
            model_adi = body.model or beyin.model
            provider_adi: str | None = None

            # "provider/model" formatÃ½nÃ½ çöz
            if "/" in model_adi:
                parts = model_adi.split("/", 1)
                provider_adi = parts[0]
                model_adi = parts[1]
                logger.debug(
                    "Ã‡özümlenen: provider=%s model=%s", provider_adi, model_adi
                )

            # MesajlarÃ½ ayÃ½r: sistem prompt'u ayrÃ½
            sistem_prompt = ""
            mesajlar: list[dict] = []
            for msg in body.messages:
                if msg.get("role") == "system":
                    sistem_prompt = msg.get("content", "")
                else:
                    mesajlar.append(
                        {
                            "role": msg.get("role", "user"),
                            "content": msg.get("content", ""),
                        }
                    )

            # OpenAI-uyumlu yanÃ½t ID'si
            yanit_id = f"chatcmpl-{uuid.uuid4().hex[:12]}"
            suan = int(time.time())

            # â”€â”€ Streaming mod â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
            if body.stream:

                async def _stream_generator() -> AsyncGenerator[str, None]:
                    """SSE akÃ½Ã¾Ã½ üretir."""
                    try:
                        # Ãlk chunk: rol
                        ilk_chunk = {
                            "id": yanit_id,
                            "object": "chat.completion.chunk",
                            "created": suan,
                            "model": model_adi,
                            "choices": [
                                {
                                    "index": 0,
                                    "delta": {"role": "assistant", "content": ""},
                                    "finish_reason": None,
                                }
                            ],
                        }
                        yield f"data: {json.dumps(ilk_chunk, ensure_ascii=False)}\n\n"

                        # Token akÃ½Ã¾Ã½
                        for token in beyin.dusun_stream(
                            sistem_prompt=sistem_prompt,
                            mesajlar=mesajlar,
                            model=model_adi if not provider_adi else None,
                        ):
                            chunk = {
                                "id": yanit_id,
                                "object": "chat.completion.chunk",
                                "created": suan,
                                "model": model_adi,
                                "choices": [
                                    {
                                        "index": 0,
                                        "delta": {"content": token},
                                        "finish_reason": None,
                                    }
                                ],
                            }
                            yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"

                        # BitiÃ¾ chunk'Ã½
                        son_chunk = {
                            "id": yanit_id,
                            "object": "chat.completion.chunk",
                            "created": suan,
                            "model": model_adi,
                            "choices": [
                                {
                                    "index": 0,
                                    "delta": {},
                                    "finish_reason": "stop",
                                }
                            ],
                        }
                        yield f"data: {json.dumps(son_chunk, ensure_ascii=False)}\n\n"
                        yield "data: [DONE]\n\n"

                    except Exception as e:
                        logger.error("Streaming hatasÃ½: %s", e)
                        hata_chunk = {
                            "id": yanit_id,
                            "object": "chat.completion.chunk",
                            "created": suan,
                            "model": model_adi,
                            "choices": [
                                {
                                    "index": 0,
                                    "delta": {},
                                    "finish_reason": "error",
                                }
                            ],
                        }
                        yield f"data: {json.dumps(hata_chunk, ensure_ascii=False)}\n\n"
                        yield "data: [DONE]\n\n"

                return StreamingResponse(
                    _stream_generator(),
                    media_type="text/event-stream",
                    headers={
                        "Cache-Control": "no-cache",
                        "Connection": "keep-alive",
                        "X-Accel-Buffering": "no",
                    },
                )

            # â”€â”€ Non-streaming mod â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
            try:
                yanit_metni = beyin.dusun(
                    sistem_prompt=sistem_prompt,
                    mesajlar=mesajlar,
                    model=model_adi if not provider_adi else None,
                    provider=provider_adi,
                )

                # Token sayÃ½sÃ½ tahmini
                prompt_token = len(sistem_prompt.split()) + sum(
                    len(m.get("content", "").split()) for m in mesajlar
                )
                completion_token = len(yanit_metni.split())

                return ChatCompletionResponse(
                    id=yanit_id,
                    created=suan,
                    model=model_adi,
                    choices=[
                        ChatCompletionChoice(
                            index=0,
                            message=ChatCompletionMessage(
                                role="assistant",
                                content=yanit_metni,
                            ),
                            finish_reason="stop",
                        )
                    ],
                    usage=ChatCompletionUsage(
                        prompt_tokens=prompt_token,
                        completion_tokens=completion_token,
                        total_tokens=prompt_token + completion_token,
                    ),
                )

            except Exception as e:
                logger.error("Chat completions hatasÃ½: %s", e)
                raise HTTPException(
                    status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"YanÃ½t üretilemedi: {e}",
                )

    # â”€â”€ CORS middleware â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    def _cors_ekle(self) -> None:
        """Tüm origin'lere izin veren CORS middleware'i ekle."""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    def run(self) -> None:
        """Sunucuyu baÃ¾lat (blocking call)."""
        import uvicorn

        self._cors_ekle()

        logger.info(
            "ReYMeN API sunucusu baÃ¾latÃ½lÃ½yor â†’ http://%s:%s",
            self.host,
            self.port,
        )
        logger.info(
            "Beyin: provider=%s model=%s",
            self._beyin_config.get("default_provider", "?"),
            self._beyin_config.get("default_model", "?"),
        )
        if self.api_key_required and self._api_key:
            logger.info("API anahtarÃ½ korumasÃ½: AÃ‡IK")
        else:
            logger.info("API anahtarÃ½ korumasÃ½: KAPALI")

        uvicorn.run(
            self.app,
            host=self.host,
            port=self.port,
            log_level="info",
        )


# â”€â”€ CLI entry point â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def main() -> None:
    """Komut satÃ½rÃ½ giriÃ¾ noktasÃ½.

    KullanÃ½m::

        python -m reymen.api_server --port 8000
        python -m reymen.api_server --port 8000 --host 0.0.0.0 --no-auth
        python -m reymen.api_server --port 8000 --log DEBUG
    """
    parser = argparse.ArgumentParser(
        prog="python -m reymen.api_server",
        description="ReYMeN API Sunucusu â€” OpenAI-uyumlu REST API",
    )
    parser.add_argument(
        "--port",
        "-p",
        type=int,
        default=int(os.environ.get("API_PORT", "8000")),
        help="Dinlenecek port (ortam: API_PORT, varsayÃ½lan: 8000)",
    )
    parser.add_argument(
        "--host",
        type=str,
        default=os.environ.get("API_HOST", "127.0.0.1"),
        help="Dinlenecek host (ortam: API_HOST, varsayÃ½lan: 127.0.0.1)",
    )
    parser.add_argument(
        "--no-auth",
        action="store_true",
        help="API anahtarÃ½ korumasÃ½nÃ½ kapat (.env'deki API_KEY gerekmez)",
    )
    parser.add_argument(
        "--log",
        type=str,
        default=os.environ.get("API_LOG_LEVEL", "INFO"),
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Log seviyesi (varsayÃ½lan: INFO)",
    )

    args = parser.parse_args()

    server = APIServer(
        host=args.host,
        port=args.port,
        api_key_required=not args.no_auth,
        log_level=args.log,
    )
    server.run()


if __name__ == "__main__":
    main()
