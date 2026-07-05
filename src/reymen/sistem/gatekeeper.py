# -*- coding: utf-8 -*-
"""
Agent Gatekeeper â€” ReYMeN / DeepSeek-V4-Flash icin
zorunlu arac-calistirma dogrulama motoru.

AmaÃ§: Modelin "TOOL CALL yaptim" ya da "test ettim" demesine
GUVENMEMEK. Bunun yerine:
  1. Modelin urettigi kodu gercekten calistir.
  2. Calistirma logunu SQLite'a yaz.
  3. Final cevap uretilmeden once, o oturumda gercek bir
     execution kaydi var mi diye kontrol et (gatekeeper).
  4. Kayit yoksa cevabi REDDET, modele "once calistir" diye geri gonder.

Bu enforcement modelin PROMPT'una degil, bu KODA dayanir.
"""

import json
import subprocess
import sqlite3
import re
import time
import os
from pathlib import Path

# ---------------------------------------------------------------------
# ReYMeN proje kokunu bul
# ---------------------------------------------------------------------
_PROJE_KOK = Path(__file__).resolve().parent.parent.parent
_LOG_DB = _PROJE_KOK / "execution_log.sqlite"

# ---------------------------------------------------------------------
# 1) Calistirma logu â€” gercek kanit burada tutulur
# ---------------------------------------------------------------------
def init_log():
    conn = sqlite3.connect(str(_LOG_DB))
    conn.execute("""
        CREATE TABLE IF NOT EXISTS executions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            code TEXT,
            stdout TEXT,
            stderr TEXT,
            returncode INTEGER,
            ts REAL
        )
    """)
    conn.commit()
    conn.close()


def run_and_log(session_id: str, code: str, timeout: int = 15) -> dict:
    """Kodu gercekten calistirir, ham ciktiyi yakar ve DB'ye yazar."""
    import sys as _sys
    python_bin = _sys.executable if hasattr(_sys, 'executable') and _sys.executable else "python3"
    try:
        result = subprocess.run(
            [python_bin, "-c", code],
            capture_output=True, text=True, timeout=timeout
        )
        stdout, stderr, rc = result.stdout, result.stderr, result.returncode
    except subprocess.TimeoutExpired:
        stdout, stderr, rc = "", "TIMEOUT", -1
    except Exception as e:
        stdout, stderr, rc = "", f"CALISTIRMA HATASI: {e}", -1

    conn = sqlite3.connect(str(_LOG_DB))
    conn.execute(
        "INSERT INTO executions (session_id, code, stdout, stderr, returncode, ts) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (session_id, code, stdout, stderr, rc, time.time())
    )
    conn.commit()
    conn.close()

    return {"stdout": stdout, "stderr": stderr, "returncode": rc}


def has_real_execution(session_id: str, since_ts: float = 0) -> bool:
    """Gatekeeper: bu oturumda, since_ts'ten sonra gercek bir calistirma var mi?"""
    conn = sqlite3.connect(str(_LOG_DB))
    row = conn.execute(
        "SELECT COUNT(*) FROM executions WHERE session_id=? AND ts>?",
        (session_id, since_ts)
    ).fetchone()
    conn.close()
    return row[0] > 0


# ---------------------------------------------------------------------
# 2) Sayisal / DB iddiasi tespiti
# ---------------------------------------------------------------------
NUMERIC_CLAIM_PATTERN = re.compile(
    r"(\bSELECT\b|\bsonuÃ§\b.*\d|\btoplam\b.*\d|=\s*\d+\.?\d*|%\d+)", re.IGNORECASE
)

def response_makes_numeric_claim(text: str) -> bool:
    return bool(NUMERIC_CLAIM_PATTERN.search(text))


# ---------------------------------------------------------------------
# 3) Model cagrisi â€” ReYMeN'in mevcut Beyin.uret()'ine bagli
# ---------------------------------------------------------------------
def call_model(messages: list, session_id: str = "default") -> str:
    """
    ReYMeN'in kendi Beyin motoru uzerinden DeepSeek-V4-Flash'i cagirir.
    """
    import sys
    sys.path.insert(0, str(_PROJE_KOK))
    sys.path.insert(0, str(_PROJE_KOK / "src"))

    try:
        from reymen.cereyan.beyin import Beyin

        # ReYMeN config'ini .env'den al
        config = {
            "provider": os.environ.get("REYMEN_PROVIDER", "deepseek"),
            "model": os.environ.get("REYMEN_MODEL", "deepseek-chat"),
            "temperature": 0.7,
            "max_tokens": 4096,
        }

        beyin = Beyin(config=config)
        # System prompt'u messages'in ilk mesaji olarak kabul et
        system_prompt = ""
        user_messages = messages
        if messages and messages[0].get("role") == "system":
            system_prompt = messages[0]["content"]
            user_messages = messages[1:]

        yanit = beyin.uret(system_prompt, user_messages)
        return yanit or ""

    except ImportError as e:
        # Fallback: direkt OpenAI-uyumlu API cagrisi
        return _call_model_direct_api(messages)
    except Exception as e:
        return f"[MODEL HATASI] {e}"


def _call_model_direct_api(messages: list) -> str:
    """
    Fallback: OpenAI-uyumlu REST API uzerinden DeepSeek.
    """
    import urllib.request
    import urllib.error

    api_key = os.environ.get("DEEPSEEK_API_KEY", "")
    if not api_key:
        # ReYMeN profil .env'sinden dene
        try:
            from dotenv import load_dotenv
            profil_env = Path(os.environ.get("REYMEN_PROFILE_DIR", "")) / ".env"
            if profil_env.exists():
                load_dotenv(profil_env, override=True)
                api_key = os.environ.get("DEEPSEEK_API_KEY", "")
        except Exception:
            pass
        if not api_key:
            # Son cares: proje .env
            dotenv_path = _PROJE_KOK / ".env"
            if dotenv_path.exists():
                with open(str(dotenv_path)) as f:
                    for line in f:
                        if line.startswith("DEEPSEEK_API_KEY="):
                            api_key = line.split("=", 1)[1].strip().strip("\"'")
                            break

    if not api_key:
        return "[MODEL HATASI] DEEPSEEK_API_KEY bulunamadi"

    url = "https://api.deepseek.com/v1/chat/completions"
    payload = json.dumps({
        "model": "deepseek-chat",
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 4096,
    }).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data["choices"][0]["message"]["content"]
    except Exception as e:
        return f"[API HATASI] {e}"


# ---------------------------------------------------------------------
# 3b) Kod bloklarini ayikla
# ---------------------------------------------------------------------
def extract_code_blocks(text: str) -> list:
    """```python ... ``` icindeki kod bloklarini bul."""
    blocks = re.findall(r"```python\s*(.*?)```", text, re.DOTALL)
    if not blocks:
        # ``` (dil belirtilmemis) dene
        blocks = re.findall(r"```\s*(.*?)```", text, re.DOTALL)
    return [b.strip() for b in blocks]


# ---------------------------------------------------------------------
# 4) Gatekeeper dongusu â€” asil enforcement burada
# ---------------------------------------------------------------------
def run_gatekept_turn(session_id: str, messages: list, max_retries: int = 2) -> dict:
    """
    Gatekeeper ile korunan model cagrisi.

    Parametreler:
        session_id: Oturum kimligi
        messages:   OpenAI-uyumlu mesaj listesi
        max_retries: Maksimum tekrar deneme sayisi

    Donus:
        {"success": bool, "response": str, "executions": int, "attempts": int}
    """
    init_log()
    turn_start_ts = time.time()

    for attempt in range(max_retries + 1):
        response_text = call_model(messages, session_id)
        code_blocks = extract_code_blocks(response_text)

        # Kod varsa gercekten calistir, ciktiyi modele geri ver
        if code_blocks:
            exec_results = []
            for code in code_blocks:
                sonuc = run_and_log(session_id, code)
                exec_results.append(sonuc)

            messages.append({"role": "assistant", "content": response_text})
            messages.append({
                "role": "user",
                "content": (
                    "GERCEK CALISTIRMA CIKTISI:\n"
                    f"{json.dumps(exec_results, ensure_ascii=False, indent=2)}\n\n"
                    "Bu ham ciktiya dayanarak nihai cevabini ver."
                ),
            })
            continue  # Modelin ham ciktiyi gorup nihai cevabi uretmesi icin tekrar cagir

        # Kod yok ama sayisal/DB iddiasi varsa VE execution kaydi yoksa -> REDDET
        if response_makes_numeric_claim(response_text) and not has_real_execution(session_id, 0):
            messages.append({"role": "assistant", "content": response_text})
            messages.append({
                "role": "user",
                "content": (
                    "REDDEDILDI: Sayisal/DB iddian var ama gercek bir kod calistirma "
                    "kaydi yok. Once ```python kod blokunda gercek kod uret, "
                    "calistir, sonra iddiayi yaz."
                ),
            })
            continue

        # Buraya geldiyse: ya iddia yok, ya da execution gercekten yapilmis -> KABUL
        execution_count = 0
        try:
            conn = sqlite3.connect(str(_LOG_DB))
            row = conn.execute(
                "SELECT COUNT(*) FROM executions WHERE session_id=? AND ts>?",
                (session_id, turn_start_ts)
            ).fetchone()
            execution_count = row[0] if row else 0
            conn.close()
        except Exception:
            pass

        return {
            "success": True,
            "response": response_text,
            "executions": execution_count,
            "attempts": attempt + 1,
        }

    return {
        "success": False,
        "response": "GATEKEEPER: Maksimum deneme sayisina ulasildi, dogrulanmis cevap uretilemedi.",
        "executions": 0,
        "attempts": max_retries + 1,
    }


# ---------------------------------------------------------------------
# 5) Komut satiri kullanimi
# ---------------------------------------------------------------------
if __name__ == "__main__":
    import sys
    # Test: dogrudan bir soru sor
    test_session = "gatekeeper_test"
    test_messages = [
        {"role": "system", "content": "Sen ReYMeN ajanisin. Turkce cevap ver."},
        {"role": "user", "content": "2+2 kac eder? Once python kodu yaz, sonra sonucu soyle."},
    ]
    sonuc = run_gatekept_turn(test_session, test_messages)
    print(json.dumps(sonuc, ensure_ascii=False, indent=2))
