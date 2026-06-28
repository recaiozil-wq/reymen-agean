# -*- coding: utf-8 -*-
"""tools/code_execution_tool.py — Kod Çalıştırma Sandbox Aracı.

ReYMeN: Güvenli Python kodu çalıştırma ortamı.
Tehlikeli fonksiyonları engeller, timeout ile sınırlandırır.
"""

import sys
import json
import signal
import traceback
from io import StringIO
from contextlib import redirect_stdout, redirect_stderr

# Güvenli modda engellenecek tehlikeli isimler
_TEHLIKELI_ISIMLER = {
    "__import__", "eval", "exec", "open", "compile",
    "globals", "locals", "vars", "dir",
}

# Engellenecek modüller
_TEHLIKELI_MODULLER = {
    "subprocess", "os", "sys", "shutil", "socket",
    "ctypes", "signal", "multiprocessing", "threading",
    "importlib", "pickle", "shelve", "marshal",
    "webbrowser", "tkinter", "code", "codeop",
    "pty", "tty", "fcntl", "termios",
}


class _GuvenliNamespace(dict):
    """Tehlikeli erişimleri engelleyen özel namespace."""

    def __getitem__(self, key):
        if key in _TEHLIKELI_ISIMLER:
            raise NameError(f"Güvenlik: '{key}' kullanımı engellendi.")
        return super().__getitem__(key)

    def __setitem__(self, key, value):
        if key in _TEHLIKELI_ISIMLER:
            raise NameError(f"Güvenlik: '{key}' ataması engellendi.")
        # Modül atamalarını da engelle
        if hasattr(value, "__name__") and value.__name__ in _TEHLIKELI_MODULLER:
            raise NameError(f"Güvenlik: '{value.__name__}' modülü engellendi.")
        super().__setitem__(key, value)


def _guvenli_calistir(kod: str, timeout: int) -> str:
    """Kodu güvenli sandbox'ta çalıştır."""
    import builtins

    # Güvenli builtins oluştur
    guvenli_builtins = {}
    for name in dir(builtins):
        if name not in _TEHLIKELI_ISIMLER and not name.startswith("_"):
            guvenli_builtins[name] = getattr(builtins, name)

    # İzin verilen builtin'ler
    guvenli_builtins["print"] = print
    guvenli_builtins["len"] = len
    guvenli_builtins["range"] = range
    guvenli_builtins["int"] = int
    guvenli_builtins["float"] = float
    guvenli_builtins["str"] = str
    guvenli_builtins["bool"] = bool
    guvenli_builtins["list"] = list
    guvenli_builtins["dict"] = dict
    guvenli_builtins["tuple"] = tuple
    guvenli_builtins["set"] = set
    guvenli_builtins["max"] = max
    guvenli_builtins["min"] = min
    guvenli_builtins["sum"] = sum
    guvenli_builtins["abs"] = abs
    guvenli_builtins["any"] = any
    guvenli_builtins["all"] = all
    guvenli_builtins["enumerate"] = enumerate
    guvenli_builtins["zip"] = zip
    guvenli_builtins["sorted"] = sorted
    guvenli_builtins["reversed"] = reversed
    guvenli_builtins["isinstance"] = isinstance
    guvenli_builtins["type"] = type
    guvenli_builtins["hasattr"] = hasattr
    guvenli_builtins["getattr"] = getattr
    guvenli_builtins["setattr"] = setattr
    guvenli_builtins["ValueError"] = ValueError
    guvenli_builtins["TypeError"] = TypeError
    guvenli_builtins["KeyError"] = KeyError
    guvenli_builtins["IndexError"] = IndexError
    guvenli_builtins["Exception"] = Exception
    guvenli_builtins["True"] = True
    guvenli_builtins["False"] = False
    guvenli_builtins["None"] = None
    guvenli_builtins["__name__"] = "__main__"

    # Namespace oluştur
    ns = _GuvenliNamespace({"__builtins__": guvenli_builtins})

    # Çıktı yakalama
    cikti_buff = StringIO()
    hata_buff = StringIO()

    try:
        # Kodu derle (compile güvenli builtins'te yok)
        try:
            derlenmis = builtins.compile(kod, "<sandbox>", "exec")
        except Exception as e:
            return json.dumps({
                "durum": "hata",
                "hata": f"Derleme hatası: {e}",
                "cikti": "",
                "hata_metni": str(e)
            }, ensure_ascii=False)

        # Zaman aşımı için sinyal
        if hasattr(signal, "SIGALRM"):
            signal.signal(signal.SIGALRM, lambda s, f: (_ for _ in ()).throw(TimeoutError("Zaman aşımı")))
            signal.alarm(timeout)

        # Kodu çalıştır
        with redirect_stdout(cikti_buff), redirect_stderr(hata_buff):
            try:
                builtins.exec(derlenmis, ns)
            except TimeoutError as e:
                return json.dumps({
                    "durum": "zaman_asimi",
                    "hata": f"Kod {timeout} saniyede tamamlanamadı.",
                    "cikti": cikti_buff.getvalue(),
                    "hata_metni": str(e)
                }, ensure_ascii=False)
            except Exception as e:
                hata_detay = traceback.format_exc()
                return json.dumps({
                    "durum": "hata",
                    "hata": str(e),
                    "cikti": cikti_buff.getvalue(),
                    "hata_metni": hata_detay
                }, ensure_ascii=False)
            finally:
                if hasattr(signal, "SIGALRM"):
                    signal.alarm(0)

        return json.dumps({
            "durum": "basarili",
            "cikti": cikti_buff.getvalue(),
            "hata_metni": ""
        }, ensure_ascii=False)

    except Exception as e:
        return json.dumps({
            "durum": "hata",
            "hata": str(e),
            "cikti": cikti_buff.getvalue(),
            "hata_metni": traceback.format_exc()
        }, ensure_ascii=False)


def _guvensiz_calistir(kod: str, timeout: int) -> str:
    """Kodu güvenlik olmadan çalıştır (guvenli=False)."""
    import subprocess, tempfile, os
    try:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(kod)
            f.flush()
            r = subprocess.run(
                [sys.executable, f.name],
                capture_output=True, text=True, timeout=timeout
            )
            os.unlink(f.name)
            return json.dumps({
                "durum": "basarili",
                "cikti": r.stdout or "",
                "hata_metni": r.stderr or ""
            }, ensure_ascii=False)
    except subprocess.TimeoutExpired:
        os.unlink(f.name)
        return json.dumps({
            "durum": "zaman_asimi",
            "hata": f"Kod {timeout} saniyede tamamlanamadı."
        }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({
            "durum": "hata",
            "hata": str(e)
        }, ensure_ascii=False)


def run(**kwargs) -> str:
    """Python kodunu güvenli sandbox'ta çalıştır.

    Args:
        kod (str): Zorunlu. Çalıştırılacak Python kodu.
        timeout (int, optional): Zaman aşımı saniyesi. Varsayılan: 30.
        guvenli (bool, optional): Güvenli mod. Varsayılan: True.

    Returns:
        str: JSON formatında çalıştırma sonucu.
    """
    try:
        kod = kwargs.get("kod")
        if not kod:
            return json.dumps({
                "durum": "hata",
                "hata": "'kod' parametresi zorunludur."
            }, ensure_ascii=False)

        timeout = int(kwargs.get("timeout", 30))
        if timeout < 1:
            timeout = 30
        if timeout > 120:
            timeout = 120

        guvenli = kwargs.get("guvenli", True)
        if isinstance(guvenli, str):
            guvenli = guvenli.lower() in ("true", "1", "yes", "evet")

        if guvenli:
            return _guvenli_calistir(kod, timeout)
        else:
            return _guvensiz_calistir(kod, timeout)

    except Exception as e:
        return json.dumps({
            "durum": "hata",
            "hata": f"Beklenmeyen hata: {e}"
        }, ensure_ascii=False)


def ping() -> bool:
    return True


if __name__ == "__main__":
    print(run(kod="print('Merhaba ReYMeN!'); 2 + 2"))
