# -*- coding: utf-8 -*-
"""
telegram_bot/memory_agent.py — MemoryAgent

Konusma hafizasini yoneten, context penceresini yoneten ve LLM cagrisi yapan
modul. OpenAI-uyumlu API (DeepSeek) kullanir.
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from threading import Lock

logger = logging.getLogger("memory_agent")


class MemoryAgent:
    """Konusma hafizasi ve LLM entegrasyonu.

    Ozellikler:
    - Sliding window context (en son N mesaj)
    - Eski mesajlari otomatik ozetle (summarize_after)
    - JSON dosyasina kaydet/ger Yukle
    - Opsiyonel vektor hafiza (chromadb)
    """

    def __init__(
        self,
        context_length: int = 50,
        summarize_after: int = 30,
        use_vector_memory: bool = False,
        api_key: str = "",
        api_base: str = "https://api.deepseek.com/v1",
        model: str = "deepseek-chat",
        system_prompt: str = "",
        memory_dir: str = "",
    ):
        self.context_length = context_length
        self.summarize_after = summarize_after
        self.use_vector_memory = use_vector_memory
        self.model = model
        self.system_prompt = system_prompt

        # LLM client
        self._api_key = api_key
        self._api_base = api_base.rstrip("/")
        self._client = None

        # Hafiza
        self.messages: list[dict] = []
        self.summary: str = ""
        self._lock = Lock()

        # Dosya yolu
        if memory_dir:
            self._memory_dir = Path(memory_dir)
        else:
            self._memory_dir = (
                Path(os.environ.get("LOCALAPPDATA", "")) / "ReYMeN" / "memory"
            )
        self._memory_dir.mkdir(parents=True, exist_ok=True)
        self._memory_file = self._memory_dir / "chat_memory.json"

        # Vektor hafiza (istege bagli)
        self._vector_store = None
        if use_vector_memory:
            self._init_vector_store()

    # ── LLM Client ───────────────────────────

    def _get_client(self):
        """OpenAI-uyumlu client nesnesini olustur (lazy)."""
        if self._client is not None:
            return self._client
        try:
            from openai import OpenAI

            self._client = OpenAI(
                api_key=self._api_key,
                base_url=self._api_base,
            )
        except ImportError:
            logger.error("openai paketi kurulu degil, fallback kullaniliyor.")
            self._client = None
        except Exception as e:
            logger.error(f"LLM client baslatilamadi: {e}")
            self._client = None
        return self._client

    def complete(self, prompt: str) -> str:
        """LLM'den cevap al (senkron, blocking).

        system_prompt varsa system rolüyle API'ye eklenir.
        """
        client = self._get_client()
        if client is None:
            return self._fallback_complete(prompt)

        try:
            messages = []
            if self.system_prompt:
                messages.append({"role": "system", "content": self.system_prompt})
            messages.append({"role": "user", "content": prompt})

            resp = client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=2000,
                temperature=0.7,
                timeout=30,
            )
            return resp.choices[0].message.content.strip()[:4000]
        except Exception as e:
            logger.error(f"LLM cagrisi basarisiz: {e}")
            return self._fallback_complete(prompt)

    def _fallback_complete(self, prompt: str) -> str:
        """OpenAI paketi yoksa HTTP ile DeepSeek API'ye git."""
        import requests as req

        key = self._api_key or os.environ.get("DEEPSEEK_API_KEY", "")
        if not key:
            return "Uzgunum, su anda cevap veremiyorum (API anahtari eksik)."

        try:
            messages = []
            if self.system_prompt:
                messages.append({"role": "system", "content": self.system_prompt})
            messages.append({"role": "user", "content": prompt})

            r = req.post(
                f"{self._api_base}/chat/completions",
                headers={
                    "Authorization": f"Bearer {key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": messages,
                    "max_tokens": 2000,
                    "temperature": 0.7,
                },
                timeout=30,
            )
            r.raise_for_status()
            return r.json()["choices"][0]["message"]["content"].strip()[:4000]
        except Exception as e:
            logger.error(f"Fallback LLM hatasi: {e}")
            return f"Uzgunum, bir hata olustu: {str(e)[:200]}"

    # ── Context Yonetimi ─────────────────────

    def add_message(self, role: str, content: str):
        """Bir mesaji hafizaya ekle.

        Args:
            role: 'user' veya 'assistant'
            content: Mesaj metni
        """
        with self._lock:
            self.messages.append({
                "role": role,
                "content": content,
                "timestamp": datetime.now().isoformat(),
            })
            self._maybe_summarize()
            self._trim_context()

    def get_context(self, query: str = "") -> str:
        """Mevcut hafizadan context metni olustur.

        Args:
            query: Vektor aramada kullanilacak sorgu (opsiyonel)

        Returns:
            Context metni
        """
        with self._lock:
            parts = []

            # Ozet varsa ekle
            if self.summary:
                parts.append(f"[OZET: {self.summary}]")

            # Vektor hafizadan ilgili bilgiler
            if self.use_vector_memory and query and self._vector_store:
                try:
                    relevant = self._vector_store.similarity_search(query, k=3)
                    if relevant:
                        contexts = "\n".join(
                            f"- {doc.page_content[:200]}"
                            for doc in relevant
                        )
                        parts.append(f"[ILGILI HAFIZA:\n{contexts}\n]")
                except Exception as e:
                    logger.debug(f"Vektor arama hatasi: {e}")

            # Son mesajlar
            if self.messages:
                history = self.messages[-(self.context_length):]
                history_text = "\n".join(
                    f"{m['role']}: {m['content']}"
                    for m in history
                )
                parts.append(f"[KONUSMA GECMISI:\n{history_text}\n]")

            return "\n\n".join(parts)

    def _maybe_summarize(self):
        """Mesaj sayisi summarize_after'i gecerse eski mesajlari ozetle."""
        if len(self.messages) < self.summarize_after:
            return
        if self.summary:
            return  # Zaten ozetlenmis

        # Ilk N/2 mesaji ozetle
        to_summarize = self.messages[: len(self.messages) // 2]
        if not to_summarize:
            return

        text = "\n".join(
            f"{m['role']}: {m['content'][:500]}"
            for m in to_summarize
        )

        try:
            summary_prompt = (
                f"Asagidaki konusmayi 2-3 cumlede ozetle (Turkce):\n\n{text}"
            )
            summary = self.complete(summary_prompt)
            self.summary = summary[:500]
            # Ozetlenen mesajlari temizle
            self.messages = self.messages[len(to_summarize):]
            logger.info(f"Hafiza ozetlendi: {len(to_summarize)} mesaj -> 1 ozet")
        except Exception as e:
            logger.warning(f"Ozetleme basarisiz: {e}")

    def _trim_context(self):
        """Context penceresini context_length ile sinirla."""
        if len(self.messages) > self.context_length * 2:
            self.messages = self.messages[-(self.context_length):]

    # ── Kaydet/Yukle ─────────────────────────

    def save_memory(self):
        """Hafizayi JSON dosyasina kaydet."""
        with self._lock:
            try:
                data = {
                    "messages": self.messages,
                    "summary": self.summary,
                    "saved_at": datetime.now().isoformat(),
                }
                self._memory_file.write_text(
                    json.dumps(data, indent=2, ensure_ascii=False, default=str),
                    encoding="utf-8",
                )
            except Exception as e:
                logger.error(f"Hafiza kaydedilemedi: {e}")

    def load_memory(self):
        """JSON dosyasindan hafizayi yukle."""
        with self._lock:
            try:
                if self._memory_file.exists():
                    data = json.loads(
                        self._memory_file.read_text(encoding="utf-8")
                    )
                    self.messages = data.get("messages", [])
                    self.summary = data.get("summary", "")
                    logger.info(
                        f"Hafiza yuklendi: {len(self.messages)} mesaj, "
                        f"ozet={bool(self.summary)}"
                    )
            except Exception as e:
                logger.warning(f"Hafiza yuklenemedi: {e}")

    def clear_memory(self):
        """Hafizayi temizle."""
        with self._lock:
            self.messages = []
            self.summary = ""
            if self._memory_file.exists():
                self._memory_file.unlink()
            logger.info("Hafiza temizlendi.")

    # ── Vektor Hafiza ────────────────────────

    def _init_vector_store(self):
        """ChromaDB vektor deposunu baslat (opsiyonel)."""
        try:
            from chromadb import PersistentClient

            vector_dir = self._memory_dir / "vectors"
            vector_dir.mkdir(parents=True, exist_ok=True)
            self._vector_client = PersistentClient(str(vector_dir))
            self._vector_store = None  # gerektiginde collection olusturulur
            logger.info("Vektor hafiza hazir.")
        except ImportError:
            logger.warning("chromadb paketi yok, vektor hafiza devre disi.")
            self.use_vector_memory = False
        except Exception as e:
            logger.warning(f"Vektor hafiza baslatilamadi: {e}")
            self.use_vector_memory = False
