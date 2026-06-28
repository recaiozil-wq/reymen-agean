# -*- coding: utf-8 -*-
"""
providers/base.py — ProviderProfile taban sinifi.
Her LLM saglayicisi bu profili kullanarak kaydedilir.
"""
import os
from dataclasses import dataclass, field


# Sentinel: temperature'i iletme (None yerine)
OMIT_TEMPERATURE = "OMIT_TEMPERATURE"


@dataclass
class ProviderProfile:
    """Bir LLM saglayicisinin tanimi."""
    name: str
    base_url: str
    env_vars: tuple = ()
    aliases: tuple = ()
    api_key_header: str = "Authorization"
    api_key_prefix: str = "Bearer"
    default_model: str = ""
    openai_compat: bool = True
    notes: str = ""
    # Model provider plugin ek alanlari (ReYMeN uyumlulugu)
    api_mode: str = ""
    auth_type: str = ""
    display_name: str = ""
    default_aux_model: str = ""
    models_url: str = ""
    signup_url: str = ""
    description: str = ""
    fallback_models: tuple = ()
    provider_type: str = ""
    default_max_tokens: int = 0
    default_headers: dict = field(default_factory=dict)
    supports_health_check: bool = False
    fixed_temperature: float = 0.0

    def api_key_from_env(self) -> str:
        """Ortam degiskenlerinden API anahtarini bul.

        env_vars sirasiyla denenir; maskelenmis (***...) veya bos
        degerler atlanir.
        """
        for var in self.env_vars:
            val = os.environ.get(var, "").strip()
            if val and not val.startswith("***"):
                return val
        return ""

    def headers(self, api_key: str = "") -> dict:
        """HTTP baslik sozlugu olustur.

        api_key verilmezse ortam degiskenlerinden okunur. Anahtar
        yoksa veya "not-needed" ise (yerel sunucular icin), Authorization
        basligi eklenmez.
        """
        key = (api_key or self.api_key_from_env()).strip()
        if not key or key.lower() == "not-needed":
            return {"Content-Type": "application/json"}
        return {
            self.api_key_header: f"{self.api_key_prefix} {key}".strip(),
            "Content-Type": "application/json",
        }

    def chat_url(self) -> str:
        """Tamamlanma (chat completions) endpoint URL'sini olustur.

        base_url icinde zaten '/v1' gibi bir yol varsa tekrar eklenmez.
        """
        url = self.base_url.rstrip("/")
        suffix = "/v1/chat/completions" if self.openai_compat else "/chat/completions"
        if url.endswith(suffix):
            return url
        if self.openai_compat and url.endswith("/v1"):
            return f"{url}/chat/completions"
        return f"{url}{suffix}"

    def mevcut_mu(self) -> bool:
        """API anahtari var mi (yerel providerlar icin True).

        env_vars tanimli degilse (ornegin Ollama gibi yerel sunucular)
        anahtar gerekmedigi kabul edilir ve True dondurulur.
        """
        if not self.env_vars:
            return True
        return bool(self.api_key_from_env())
