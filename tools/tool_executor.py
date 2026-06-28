# -*- coding: utf-8 -*-
"""tools/tool_executor.py — Tool calistirma motoru.

Tum tool cagrilerini merkezi yonetir: retry, timeout ve sonuc dogrulama.
"""

import importlib
import json
import time
import threading
from typing import Any

# ANSI renk kodlari
_Y = "\033[92m"   # yesil
_S = "\033[93m"   # sari
_K = "\033[91m"   # kirmizi
_M = "\033[94m"   # mavi
_R = "\033[0m"    # sifirla

MAX_RETRY = 3
DEFAULT_TIMEOUT_S = 30


def _fmt(msg: str, renk: str) -> str:
    return f"{renk}{msg}{_R}"


def _dogrula_sonuc(sonuc: Any) -> tuple:
    """Sonucun gecerli olup olmadigini kontrol et.

    Args:
        sonuc: Tool'dan donen ham deger.

    Returns:
        (gecerli: bool, aciklama: str)
    """
    if sonuc is None:
        return False, "Sonuc None"
    if isinstance(sonuc, str) and sonuc.lstrip().startswith("[Hata]"):
        return False, f"Tool hata string'i: {sonuc[:120]}"
    if isinstance(sonuc, dict) and sonuc.get("durum") == "hata":
        return False, f"Tool hata dict'i: {sonuc.get('mesaj', '')}"
    return True, "Gecerli"


def execute_tool(name: str, args: dict, timeout_s: int = DEFAULT_TIMEOUT_S) -> dict:
    """Bir tool'u retry ve timeout korumasi altinda calistir.

    Onceki denemeler basarisiz olursa exponential backoff (1s, 2s, 4s) uygular.
    Timeout asiminda thread birakılır; Windows'ta thread iptal edilemez,
    bu nedenle daemon=True ile isaretlenir.

    Args:
        name: tools/ icerisindeki modul adi (ornegin 'shell', 'file_ops').
        args: Tool'a gecilecek anahtar-deger parametreler.
        timeout_s: Her deneme icin zaman asimi saniyesi.

    Returns:
        dict: {
            'ok': bool,
            'result': Any,        # basaridaysa ham cikti
            'error': str | None,  # hata varsa aciklama
            'attempts': int       # kac deneme yapildi
        }
    """
    kayit = {"ok": False, "result": None, "error": None, "attempts": 0}

    for deneme in range(1, MAX_RETRY + 1):
        kayit["attempts"] = deneme

        try:
            mod = importlib.import_module(f"tools.{name}")
        except ModuleNotFoundError:
            kayit["error"] = _fmt(f"[EXECUTOR] Modul bulunamadi: tools.{name}", _K)
            break

        run_fn = getattr(mod, "run", None)
        if run_fn is None:
            kayit["error"] = _fmt(f"[EXECUTOR] '{name}' modulunde run() yok", _K)
            break

        result_kutu: list = [None]
        exc_kutu: list = [None]

        def _calistir():
            try:
                result_kutu[0] = run_fn(**args)
            except Exception as exc:
                exc_kutu[0] = exc

        t = threading.Thread(target=_calistir, daemon=True)
        t.start()
        t.join(timeout=timeout_s)

        if t.is_alive():
            msg = _fmt(f"[EXECUTOR] '{name}' {timeout_s}s icinde tamamlanamadi (deneme {deneme})", _S)
            print(msg)
            kayit["error"] = msg
            if deneme < MAX_RETRY:
                time.sleep(2 ** (deneme - 1))
            continue

        if exc_kutu[0] is not None:
            msg = _fmt(f"[EXECUTOR] '{name}' exception: {exc_kutu[0]} (deneme {deneme})", _K)
            print(msg)
            kayit["error"] = msg
            if deneme < MAX_RETRY:
                time.sleep(2 ** (deneme - 1))
            continue

        gecerli, aciklama = _dogrula_sonuc(result_kutu[0])
        if gecerli:
            kayit["ok"] = True
            kayit["result"] = result_kutu[0]
            kayit["error"] = None
            print(_fmt(f"[EXECUTOR] {_Y}OK{_R} — '{name}' {deneme}. denemede basarili", _Y))
            return kayit

        msg = _fmt(f"[EXECUTOR] Sonuc gecersiz ({aciklama}), deneme {deneme}", _S)
        print(msg)
        kayit["error"] = msg
        if deneme < MAX_RETRY:
            time.sleep(2 ** (deneme - 1))

    print(_fmt(f"[EXECUTOR] BASARISIZ — '{name}' {kayit['attempts']} denemeden sonra", _K))
    return kayit


def run(islem: str = "execute", name: str = "", args=None, timeout_s: int = DEFAULT_TIMEOUT_S) -> str:
    """Tool executor harici arayuzu (tool_registry uyumu icin).

    Args:
        islem: Su an yalnizca 'execute' destekleniyor.
        name: Calistirilacak tool modul adi.
        args: Dict veya JSON string olarak parametreler.
        timeout_s: Zaman asimi saniyesi.

    Returns:
        str: JSON formatinda sonuc.
    """
    args = args or {}
    if isinstance(args, str):
        try:
            args = json.loads(args)
        except json.JSONDecodeError:
            args = {}

    try:
        if islem == "execute":
            sonuc = execute_tool(name, args, int(timeout_s))
            return json.dumps(sonuc, ensure_ascii=False, default=str)
        return json.dumps({"durum": "hata", "mesaj": f"bilinmeyen islem: {islem}"}, ensure_ascii=False)
    except Exception as exc:
        return json.dumps({"durum": "hata", "mesaj": str(exc)}, ensure_ascii=False)


if __name__ == "__main__":
    print(run("execute", "shell", {"komut": "echo merhaba executor"}))
