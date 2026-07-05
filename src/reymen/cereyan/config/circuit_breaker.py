# -*- coding: utf-8 -*-
"""Circuit breaker ve retry sabitleri.

ReYMeN Agent pattern'i:
- max_deneme=3, 3 başarısızsa → dur + bildir
- Kalıcı: kullanıcı müdahalesi gerekene kadar kapalı kalır
"""
from __future__ import annotations

import os

# Circuit breaker (ReYMeN Agent pattern'i)
CIRCUIT_BREAKER_MAX_HATA: int = int(os.environ.get("CB_MAX_HATA", "3"))
CIRCUIT_BREAKER_SURESI: int = int(os.environ.get("CB_SURESI", "0"))  # 0 = otomatik açılmaz
CIRCUIT_BREAKER_KALICI: bool = True  # True = kullanıcı müdahalesi gerekene kadar kalıcı

# Mekanik retry: max 3 deneme, sonra circuit breaker
MAX_RETRY: int = int(os.environ.get("MAX_RETRY", "3"))

# Exponential backoff için max retry denemesi
MAX_API_RETRY: int = 3

# Aynı eylem 3x = takılma
TAKILMA_ESI: int = 3

# Art arda tool hatası limiti — aşılınca model toolsuz cevap vermeye zorlanır
ARTI_ARDA_TOOL_HATA_LIMIT: int = 3

# Toplam tool çağrısı limiti (Hermes max_tool_calls=25)
MAX_TOOL_CALLS: int = int(os.environ.get("MAX_TOOL_CALLS", "25"))

# Context budget: toplam mesaj karakter sayısı limiti
CONTEXT_BUDGET_CHARS: int = int(os.environ.get("CONTEXT_BUDGET_CHARS", "300000"))

# Streaming sabitleri
STREAMING_AKTIF: bool = os.environ.get("STREAMING_AKTIF", "true").lower() in ("true", "1")

# Context sikistirma esigi (%50)
CONTEXT_SIKISTIRMA_ESIGI: float = float(os.environ.get("CONTEXT_ESIK", "0.50"))
