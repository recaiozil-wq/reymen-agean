# -*- coding: utf-8 -*-
"""tools/python_exec.py — Python Kodu Calistirma Araci.

PYTHON_CALISTIR icin sandbox'ta Python kodu calistirir.
"""

try:
    from izole_laboratuvar import izole_python_calistir as _sandbox
except ImportError:
    _sandbox = None


def run(kod: str, timeout: int = 30) -> str:
    """Python kodunu calistir.

    Args:
        kod: Calistirilacak Python kodu
        timeout: Zaman asimi

    Returns:
        Cikti metni
    """
    if not kod:
        return "[Python]: Kod gerekli."
    if _sandbox:
        return _sandbox(kod)
    import subprocess, sys, tempfile, os
    try:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(kod)
            f.flush()
            r = subprocess.run([sys.executable, f.name], capture_output=True, text=True, timeout=timeout)
            os.unlink(f.name)
            return (r.stdout or "") + ("\n" + r.stderr if r.stderr else "")
    except subprocess.TimeoutExpired:
        return "[Python]: Zaman asimi."
    except Exception as e:
        return f"[Python]: Hata: {e}"


def ping() -> bool:
    return True


if __name__ == "__main__":
    print(run("print('merhaba')"))
