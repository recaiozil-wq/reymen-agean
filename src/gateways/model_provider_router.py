# -*- coding: utf-8 -*-
"""
model_provider_router.py â€” Modelâ†’Provider yÃ¶nlendirici

Model adÄ±ndan provider'a, failover zincirinden saÄŸlÄ±k kontrolÃ¼ne
kadar tÃ¼m model routing mantÄ±ÄŸÄ±nÄ± barÄ±ndÄ±rÄ±r.

Ã–zellikler:
  - Modelâ†’Provider statik haritasÄ± (config.yaml + built-in fallback)
  - Failover zinciri: bir provider hata verince sÄ±radakine atla
  - Model bazlÄ± provider doÄŸrulama
  - Thread-safe singleton
"""

from __future__ import annotations

import logging
import threading
import yaml
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from gateways.provider_router import (
    SaglayiciYonlendirici,
    SaglayiciDurum,
    yonlendirici_al,
)

logger = logging.getLogger(__name__)


# â”€â”€ VarsayÄ±lan Modelâ†’Provider HaritasÄ± â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# config.yaml'da model_providers: yoksa kullanÄ±lÄ±r
VARSAYILAN_MODEL_PROVIDER_MAP: dict[str, str] = {
    # DeepSeek
    "deepseek-v4-flash": "deepseek",
    "deepseek-v3": "deepseek",
    "deepseek-chat": "deepseek",
    "deepseek-reasoner": "deepseek",
    "deepseek-r1": "deepseek",
    # OpenAI
    "gpt-4o": "openai",
    "gpt-4o-mini": "openai",
    "gpt-4-turbo": "openai",
    "gpt-3.5-turbo": "openai",
    "o1": "openai",
    "o3-mini": "openai",
    # Anthropic
    "claude-sonnet-4": "anthropic",
    "claude-sonnet-4-20250514": "anthropic",
    "claude-3-5-sonnet": "anthropic",
    "claude-3-opus": "anthropic",
    "claude-3-haiku": "anthropic",
    # OpenRouter
    "openrouter/auto": "openrouter",
    "openrouter/deepseek": "openrouter",
    "openrouter/llama": "openrouter",
    "openrouter/mistral": "openrouter",
    # Groq
    "groq/llama3": "groq",
    "groq/mixtral": "groq",
    "groq/deepseek": "groq",
    "groq/gemma": "groq",
    # Azure OpenAI
    "azure/gpt-4o": "azure",
    "azure/gpt-4": "azure",
    # Gemini
    "gemini-pro": "gemini",
    "gemini-1.5-pro": "gemini",
    "gemini-1.5-flash": "gemini",
    # LM Studio (yerel)
    "lm-studio/default": "lmstudio",
    "local-model": "lmstudio",
    # Amazon Bedrock
    "bedrock/claude": "bedrock",
    "bedrock/llama": "bedrock",
}

# Providerâ†’failover sÄ±rasÄ± (varsayÄ±lan)
VARSAYILAN_FAILOVER_ZINCIRI: list[list[str]] = [
    # Birinci tercih: local provider
    ["lmstudio"],
    # Ä°kinci tercih: ana API provider'larÄ±
    ["deepseek", "openrouter"],
    # ÃœÃ§Ã¼ncÃ¼ tercih: alternatif API'ler
    ["openai", "anthropic"],
    # Son Ã§are
    ["groq", "gemini"],
]

# Provider tipi â†’ API uyumluluÄŸu
PROVIDER_API_TIPI: dict[str, str] = {
    "openrouter": "openai",
    "openai": "openai",
    "deepseek": "openai",
    "groq": "openai",
    "azure": "openai",
    "gemini": "openai",
    "anthropic": "anthropic",
    "bedrock": "bedrock",
    "lmstudio": "openai",
}

# Provider â†’ varsayÄ±lan model
PROVIDER_VARSAYILAN_MODEL: dict[str, str] = {
    "deepseek": "deepseek-v4-flash",
    "openai": "gpt-4o",
    "anthropic": "claude-sonnet-4-20250514",
    "openrouter": "openrouter/auto",
    "groq": "groq/llama3",
    "azure": "azure/gpt-4o",
    "gemini": "gemini-1.5-pro",
    "bedrock": "bedrock/claude",
    "lmstudio": "lm-studio/default",
}


# â”€â”€ Veri YapÄ±larÄ± â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


@dataclass
class ModelYonlendirmeKarari:
    """Model yÃ¶nlendirme kararÄ± â€” hangi provider'a, hangi model adÄ±yla gidilecek."""

    model: str  # LLM'e gÃ¶nderilecek model adÄ±
    provider: str  # Provider adÄ± (deepseek, openai vb.)
    api_tipi: str  # API uyumluluk tipi (openai/anthropic/bedrock)
    base_url: str  # Provider base URL
    api_key: str  # API anahtarÄ±
    failover_zinciri: list[str] = field(default_factory=list)  # Yedek provider listesi
    orijinal_model: str = ""  # Ä°stenen orijinal model adÄ±

    def __post_init__(self):
        if not self.orijinal_model:
            self.orijinal_model = self.model


# â”€â”€ Ana SÄ±nÄ±f â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


class ModelProviderRouter:
    """Modelâ†’Provider yÃ¶nlendirme + failover zinciri yÃ¶netimi.

    config.yaml'daki model_providers: bÃ¶lÃ¼mÃ¼nÃ¼ okur, varsayÄ±lan harita
    ile birleÅŸtirir. Bir model hangi provider'da Ã§alÄ±ÅŸÄ±r, hata alÄ±nÄ±rsa
    hangi sÄ±rayla diÄŸer provider'lara geÃ§ilir â€” tÃ¼m bu mantÄ±k buradadÄ±r.
    """

    def __init__(
        self,
        config_yolu: Optional[str] = None,
        model_provider_map: Optional[dict[str, str]] = None,
        failover_zinciri: Optional[list[list[str]]] = None,
    ):
        self._lock = threading.Lock()
        self._yonlendirici: SaglayiciYonlendirici = yonlendirici_al()

        # Haritalar
        self._model_provider_map: dict[str, str] = {}
        self._failover_zinciri: list[list[str]] = []
        self._provider_yapisi: dict[str, dict] = {}  # providers: config.yaml'daki yapÄ±

        # Config'den yÃ¼kle
        self._config_yolu = config_yolu
        self._config_yukle(config_yolu)

        # Parametre override'larÄ±
        if model_provider_map:
            self._model_provider_map.update(model_provider_map)
        if failover_zinciri:
            self._failover_zinciri = failover_zinciri

        # Provider'larÄ± yÃ¶nlendiriciye kaydet
        for ad in list(self._model_provider_map.values()) + [
            p for zincir in self._failover_zinciri for p in zincir
        ]:
            self._yonlendirici.kaydet(ad)

        logger.info(
            "[ModelRouter] %d modelâ†’provider eÅŸlemesi, %d failover adÄ±mÄ± yÃ¼klendi",
            len(self._model_provider_map),
            len(self._failover_zinciri),
        )

    # â”€â”€ Config YÃ¼kleme â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def _config_yukle(self, config_yolu: Optional[str] = None) -> None:
        """config.yaml'dan model_providers: ve providers: bÃ¶lÃ¼mlerini oku."""
        yollar = []
        if config_yolu:
            yollar.append(Path(config_yolu))
        yollar.extend(
            [
                Path.cwd() / "config.yaml",
                Path(__file__).resolve().parent.parent.parent / "config.yaml",
            ]
        )

        for y in yollar:
            if y.exists():
                try:
                    with open(y, "r", encoding="utf-8") as f:
                        cfg = yaml.safe_load(f) or {}

                    # model_providers: bÃ¶lÃ¼mÃ¼
                    mp = cfg.get("model_providers", {})
                    if isinstance(mp, dict):
                        self._model_provider_map.update(mp)

                    # providers: bÃ¶lÃ¼mÃ¼ (base_url, api_key bilgisi)
                    prov = cfg.get("providers", {})
                    if isinstance(prov, dict):
                        self._provider_yapisi = prov
                        # Her provider'Ä± yÃ¶nlendiriciye kaydet
                        for ad in prov:
                            self._yonlendirici.kaydet(ad)

                    # failover_zinciri: bÃ¶lÃ¼mÃ¼ (opsiyonel)
                    fz = cfg.get("failover_zinciri")
                    if isinstance(fz, list):
                        self._failover_zinciri = fz

                    logger.info("[ModelRouter] Config yÃ¼klendi: %s", y)
                    return
                except Exception as e:
                    logger.warning("[ModelRouter] Config okuma hatasÄ± (%s): %s", y, e)

        # Config bulunamadÄ± â€” varsayÄ±lan haritayÄ± kullan
        self._model_provider_map = dict(VARSAYILAN_MODEL_PROVIDER_MAP)
        self._failover_zinciri = list(VARSAYILAN_FAILOVER_ZINCIRI)
        logger.info("[ModelRouter] Config bulunamadÄ±, varsayÄ±lan harita kullanÄ±lÄ±yor")

    # â”€â”€ Model YÃ¶nlendirme â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def model_route(
        self, model: str, provider_override: Optional[str] = None
    ) -> ModelYonlendirmeKarari:
        """Bir model adÄ±nÄ± Ã§Ã¶zÃ¼mle: hangi provider, hangi API tipi, hangi URL.

        Args:
            model: Ä°stenen model adÄ± (Ã¶rn: "deepseek-v4-flash")
            provider_override: Provider'Ä± zorla (Ã¶rn: "openrouter")

        Returns:
            ModelYonlendirmeKarari â€” yÃ¶nlendirme kararÄ±
        """
        model_adi = model.strip()

        with self._lock:
            # Provider override varsa onu kullan
            if provider_override:
                provider = provider_override
            else:
                # Modelâ†’Provider haritasÄ±nda ara
                provider = self._model_provider_map.get(model_adi)

            if not provider:
                # Hello? fallback: model adÄ±nÄ±n ilk kÄ±smÄ±nÄ± provider olarak dene
                # Ã–rn: "deepseek-v4-flash" â†’ "deepseek"
                prefix = model_adi.split("-")[0].split("/")[0].split(".")[0]
                if prefix in self._model_provider_map.values():
                    provider = prefix
                elif prefix in PROVIDER_API_TIPI:
                    provider = prefix
                else:
                    # HiÃ§bir ÅŸey bulunamadÄ± â€” varsayÄ±lan provider'a yÃ¶nlendir
                    provider = "deepseek"
                    logger.warning(
                        "[ModelRouter] '%s' modeli iÃ§in provider bulunamadÄ±, "
                        "varsayÄ±lan: %s",
                        model_adi,
                        provider,
                    )

            # Provider yapÄ±landÄ±rmasÄ±nÄ± al
            prov_yapi = self._provider_yapisi.get(provider, {})
            base_url = prov_yapi.get("base_url", "")
            api_key = prov_yapi.get("api_key", "")
            api_key_env = prov_yapi.get("api_key_env", "")
            if not api_key and api_key_env:
                import os

                api_key = os.environ.get(api_key_env, "")

            # API tipini belirle
            api_tipi = PROVIDER_API_TIPI.get(provider, "openai")

            # Failover zinciri oluÅŸtur
            failover_zinciri = self._failover_zincir_olustur(provider)

            return ModelYonlendirmeKarari(
                model=model_adi,
                provider=provider,
                api_tipi=api_tipi,
                base_url=base_url,
                api_key=api_key,
                failover_zinciri=failover_zinciri,
                orijinal_model=model_adi,
            )

    def _failover_zincir_olustur(self, baslangic_provider: str) -> list[str]:
        """Bir provider'dan baÅŸlayarak failover zinciri oluÅŸtur.

        VarsayÄ±lan failover zincirindeki gruplarÄ± tara, baÅŸlangÄ±Ã§
        provider'Ä±nÄ± bul, ondan sonraki tÃ¼m provider'larÄ± zincire ekle.

        Ã–rn: baslangic="anthropic" â†’ ["anthropic", "groq", "gemini"]
        """
        bulundu = False
        zincir = []
        for grup in self._failover_zinciri:
            for p in grup:
                if bulundu:
                    zincir.append(p)
                elif p == baslangic_provider:
                    zincir.append(p)
                    bulundu = True
                    # AynÄ± gruptaki diÄŸer provider'larÄ± da ekle
                    for diger in grup:
                        if diger != p:
                            zincir.append(diger)

        if not bulundu:
            # Provider failover zincirinde bulunamadÄ± â€” sadece kendisi
            zincir = [baslangic_provider]

        return zincir

    # â”€â”€ Provider SaÄŸlÄ±k KontrolÃ¼ â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def tum_provider_saglik(self) -> dict[str, bool]:
        """TÃ¼m provider'larÄ±n saÄŸlÄ±k kontrolÃ¼nÃ¼ yap.

        Returns:
            {provider_adi: canli_mi} sÃ¶zlÃ¼ÄŸÃ¼
        """
        provider_list = []
        for ad, yapi in self._provider_yapisi.items():
            base_url = yapi.get("base_url", "")
            api_key = yapi.get("api_key", "")
            api_key_env = yapi.get("api_key_env", "")
            if not api_key and api_key_env:
                import os

                api_key = os.environ.get(api_key_env, "")
            if base_url:
                provider_list.append((ad, base_url, api_key))

        return self._yonlendirici.saglik_kontrolu(provider_list)

    def provider_durum(self, provider: Optional[str] = None) -> dict:
        """Provider durum raporu.

        Args:
            provider: Provider adÄ± (None = tÃ¼mÃ¼)

        Returns:
            Durum bilgisi dict
        """
        if provider:
            aktif = self._yonlendirici.aktif_mi(provider)
            return {
                "provider": provider,
                "aktif": aktif,
                "durum_ozeti": self._yonlendirici.durum_ozeti(),
            }

        return {
            "provider_sayisi": len(self._provider_yapisi),
            "model_sayisi": len(self._model_provider_map),
            "failover_adim_sayisi": len(self._failover_zinciri),
            "provider_durumlari": self._yonlendirici.durum_ozeti(),
        }

    # â”€â”€ Provider Hata/BaÅŸarÄ± Bildirimi â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def hata_bildir(self, provider: str):
        """Provider hata bildirimi â€” circuit breaker tetiklenebilir."""
        self._yonlendirici.hata_bildir(provider)

    def basari_bildir(self, provider: str):
        """Provider baÅŸarÄ± bildirimi â€” hata sayacÄ± sÄ±fÄ±rlanÄ±r."""
        self._yonlendirici.basari_bildir(provider)

    def aktif_mi(self, provider: str) -> bool:
        """Provider kullanÄ±labilir durumda mÄ±?"""
        return self._yonlendirici.aktif_mi(provider)

    # â”€â”€ Model Listesi â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def modelleri_listele(self, provider_filtre: Optional[str] = None) -> list[dict]:
        """TÃ¼m bilinen modelleri listele.

        Args:
            provider_filtre: Sadece belirli bir provider'daki modeller

        Returns:
            [{"model": ..., "provider": ..., "api_tipi": ...}, ...]
        """
        sonuc = []
        for model_adi, provider_adi in self._model_provider_map.items():
            if provider_filtre and provider_adi != provider_filtre:
                continue
            api_tipi = PROVIDER_API_TIPI.get(provider_adi, "openai")
            sonuc.append(
                {
                    "model": model_adi,
                    "provider": provider_adi,
                    "api_tipi": api_tipi,
                }
            )
        return sonuc

    def provider_modelleri(self, provider: str) -> list[str]:
        """Bir provider'daki tÃ¼m modelleri listele."""
        return [m for m, p in self._model_provider_map.items() if p == provider]


# â”€â”€ Singleton â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

_router: Optional[ModelProviderRouter] = None
_router_lock = threading.Lock()


def router_al(
    config_yolu: Optional[str] = None,
    model_provider_map: Optional[dict[str, str]] = None,
    failover_zinciri: Optional[list[list[str]]] = None,
) -> ModelProviderRouter:
    """Thread-safe singleton eriÅŸimi."""
    global _router
    if _router is None:
        with _router_lock:
            if _router is None:
                _router = ModelProviderRouter(
                    config_yolu=config_yolu,
                    model_provider_map=model_provider_map,
                    failover_zinciri=failover_zinciri,
                )
    elif config_yolu or model_provider_map or failover_zinciri:
        # Ä°lk kurulumdan sonra parametre deÄŸiÅŸikliÄŸi â€” log uyar
        logger.warning(
            "[ModelRouter] router_al() parametreleri singleton sonrasÄ± yok sayÄ±ldÄ±"
        )
    return _router
