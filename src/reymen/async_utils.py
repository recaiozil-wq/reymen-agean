# -*- coding: utf-8 -*-
"""Async yardimci fonksiyonlar.

Hermes agent/async_utils.py'den adapte edilmistir.
"""
from __future__ import annotations
import asyncio
from typing import Any, Coroutine

def run_async(coro: Coroutine) -> Any:
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            return asyncio.run_coroutine_threadsafe(coro, loop).result()
        return loop.run_until_complete(coro)
    except RuntimeError:
        return asyncio.run(coro)

async def run_sync(fn, *args, **kwargs):
    return fn(*args, **kwargs)
