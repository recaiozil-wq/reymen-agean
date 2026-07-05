# -*- coding: utf-8 -*-
"""codex_responses_adapter.py â€” OpenAI Codex / Responses API Adaptörü.

OpenAI'nin yeni `/v1/responses` endpoint'ini kullanÄ±r (GPT-4o dahil).
Klasik `/v1/chat/completions`'tan farkÄ±: durum bilgisi saklama, web arama,
kod yorumlama gibi built-in araçlarÄ± destekler.
ENV: OPENAI_API_KEY
"""

import json
import os
import urllib.request
from typing import Optional

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
OPENAI_BASE = "https://api.openai.com/v1"
VARSAYILAN_MODEL = os.environ.get("CODEX_MODEL", "gpt-4o")


def _openai_istek(yol: str, veri: dict) -> dict:
    if not OPENAI_API_KEY:
        return {"error": "OPENAI_API_KEY ayarlanmamÄ±ÅŸ."}
    try:
        req = urllib.request.Request(
            f"{OPENAI_BASE}{yol}",
            data=json.dumps(veri).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json",
            },
        )
        with urllib.request.urlopen(req, timeout=90) as r:
            return json.loads(r.read().decode("utf-8"))
    except Exception as e:
        return {"error": str(e)}


def _responses_istek(veri: dict) -> dict:
    """/v1/responses endpoint'i â€” yeni Responses API."""
    return _openai_istek("/responses", veri)


class CodexResponsesAdapter:
    """OpenAI Responses API adaptörü (built-in araçlar destekli)."""

    def __init__(
        self,
        model: str = VARSAYILAN_MODEL,
        api_key: str = OPENAI_API_KEY,
    ):
        self.model = model
        self.api_key = api_key

    def _baslik(self) -> dict:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def tamamla(
        self,
        mesajlar: list[dict],
        araclar: Optional[list[dict]] = None,
        onceki_yanit_id: str = "",
        max_output_tokens: int = 4096,
        sicaklik: float = 0.7,
    ) -> dict:
        """Responses API çaÄŸrÄ±sÄ±.

        Args:
            mesajlar:         KonuÅŸma geçmiÅŸi
            araclar:          Built-in araçlar (web_search_preview, code_interpreter, vb.)
            onceki_yanit_id:  Durum bilgisi devamÄ± için önceki yanÄ±t ID
            max_output_tokens: Maks çÄ±ktÄ± token
            sicaklik:         YaratÄ±cÄ±lÄ±k (0-2)

        Returns:
            API yanÄ±tÄ± dict
        """
        govde: dict = {
            "model": self.model,
            "input": mesajlar,
            "max_output_tokens": max_output_tokens,
            "temperature": sicaklik,
        }
        if araclar:
            govde["tools"] = araclar
        if onceki_yanit_id:
            govde["previous_response_id"] = onceki_yanit_id

        try:
            req = urllib.request.Request(
                f"{OPENAI_BASE}/responses",
                data=json.dumps(govde).encode("utf-8"),
                headers=self._baslik(),
            )
            with urllib.request.urlopen(req, timeout=90) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:
            return {"error": str(e)}

    def uret(
        self,
        sistem: str,
        mesajlar: list[dict],
        web_arama: bool = False,
        kod_yorumlayici: bool = False,
        **kwargs,
    ) -> str:
        """Responses API'den yanÄ±t al.

        Args:
            sistem:           Sistem promptu
            mesajlar:         KonuÅŸma geçmiÅŸi
            web_arama:        Web arama aracÄ± etkin mi
            kod_yorumlayici:  Kod yorumlayÄ±cÄ± aracÄ± etkin mi

        Returns:
            YanÄ±t metni
        """
        giris = (
            [{"role": "system", "content": sistem}] + mesajlar if sistem else mesajlar
        )

        araclar = []
        if web_arama:
            araclar.append({"type": "web_search_preview"})
        if kod_yorumlayici:
            araclar.append({"type": "code_interpreter"})

        yanit = self.tamamla(giris, araclar=araclar or None, **kwargs)

        if "error" in yanit:
            return f"[Codex Responses]: {yanit['error']}"

        # Responses API çÄ±ktÄ± formatÄ±
        cikti = yanit.get("output", [])
        if isinstance(cikti, list):
            metin_parcalari = []
            for ogre in cikti:
                if ogre.get("type") == "message":
                    for icerik in ogre.get("content", []):
                        if icerik.get("type") == "output_text":
                            metin_parcalari.append(icerik.get("text", ""))
            if metin_parcalari:
                return "\n".join(metin_parcalari).strip()

        # Fallback: chat completions format
        secimler = yanit.get("choices", [])
        if secimler:
            return secimler[0].get("message", {}).get("content", "")

        return f"[Codex Responses]: {yanit}"

    def kod_calistir(self, kod: str, dil: str = "python") -> str:
        """Kod yorumlayÄ±cÄ± ile kod çalÄ±ÅŸtÄ±r.

        Args:
            kod:  Ã‡alÄ±ÅŸtÄ±rÄ±lacak kod
            dil:  Programlama dili (python varsayÄ±lan)

        Returns:
            Ã‡Ä±ktÄ± veya hata
        """
        return self.uret(
            sistem="Sen bir kod çalÄ±ÅŸtÄ±rma asistanÄ±sÄ±n.",
            mesajlar=[
                {
                    "role": "user",
                    "content": f"Bu {dil} kodunu çalÄ±ÅŸtÄ±r:\n```{dil}\n{kod}\n```",
                }
            ],
            kod_yorumlayici=True,
        )

    def web_ara(self, sorgu: str) -> str:
        """Web arama built-in aracÄ± ile arama yap."""
        return self.uret(
            sistem="Sen web araÅŸtÄ±rmasÄ± yapan bir asistandÄ±n.",
            mesajlar=[{"role": "user", "content": sorgu}],
            web_arama=True,
        )

    def yapilandirildi_mi(self) -> bool:
        return bool(self.api_key)

    def saglik_kontrol(self) -> dict:
        if not self.api_key:
            return {"ok": False, "sebep": "API anahtarÄ± yok"}
        yanit = self.tamamla([{"role": "user", "content": "test"}], max_output_tokens=5)
        if "error" in yanit:
            return {"ok": False, "sebep": yanit["error"]}
        return {"ok": True, "model": self.model}


# Chat completions fallback (eski endpoint uyumluluÄŸu)
class OpenAIChatAdapter:
    """Klasik /v1/chat/completions endpoint'i."""

    def __init__(self, model: str = VARSAYILAN_MODEL):
        self.model = model

    def uret(self, sistem: str, mesajlar: list[dict], max_tokens: int = 4096) -> str:
        msgs = (
            [{"role": "system", "content": sistem}] + mesajlar if sistem else mesajlar
        )
        yanit = _openai_istek(
            "/chat/completions",
            {
                "model": self.model,
                "messages": msgs,
                "max_tokens": max_tokens,
            },
        )
        if "error" in yanit:
            return f"[OpenAI]: {yanit['error']}"
        secimler = yanit.get("choices", [])
        return secimler[0]["message"]["content"] if secimler else "[OpenAI]: BoÅŸ yanÄ±t"


if __name__ == "__main__":
    adapter = CodexResponsesAdapter()
    print(f"Model: {adapter.model}")
    print(f"YapÄ±landÄ±rÄ±ldÄ±: {adapter.yapilandirildi_mi()}")
    if adapter.yapilandirildi_mi():
        print(adapter.saglik_kontrol())
