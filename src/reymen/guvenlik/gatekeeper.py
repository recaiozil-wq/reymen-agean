"""
Agent Gatekeeper â€” çaÄŸrÄ± akÄ±ÅŸÄ± doÄŸrulama katmanÄ±.

Bu bir araç DEÄÄ°LDÄ°R. Modelin haberi olmadan çalÄ±ÅŸÄ±r.
Main loop'unda call_model() yerine run_gatekept_turn() çaÄŸrÄ±lÄ±r.

AkÄ±ÅŸ:
  1. KullanÄ±cÄ± mesajÄ± gelir (sayÄ±sal/DB içerikli olabilir)
  2. run_gatekept_turn() modeli çaÄŸÄ±rÄ±r
  3. Model ```python bloÄŸu üretirse â†’ otomatik çalÄ±ÅŸtÄ±r â†’ ham çÄ±ktÄ±yÄ± modele geri ver
  4. Model sayÄ±sal/DB iddiasÄ± yaparsa ama execution kaydÄ± yoksa â†’ REDDET
  5. KayÄ±t varsa veya iddia yoksa â†’ cevabÄ± kabul et

Bu enforcement modelin PROMPT'una deÄŸil, bu koda dayanÄ±r.
"""

import json
import subprocess
import sqlite3
import re
import time
import os
import urllib.request
import urllib.error
from pathlib import Path

LOG_DB = Path(__file__).parent / "execution_log.sqlite"
FORMAT_SYSTEM_MSG = {
    "role": "system",
    "content": (
        "Kod üretirken mutlaka ```python bloÄŸu kullan. "
        "Sistem bu bloÄŸu otomatik çalÄ±ÅŸtÄ±rÄ±p sana gerçek çÄ±ktÄ±yÄ± geri verecek. "
        "Kod bloklarÄ±nÄ±n dÄ±ÅŸÄ±nda kalan metinler doÄŸrudan kullanÄ±cÄ±ya gönderilir."
    )
}


# ---------------------------------------------------------------------
# 1) Ã‡alÄ±ÅŸtÄ±rma logu â€” gerçek kanÄ±t burada tutulur
# ---------------------------------------------------------------------
def init_log():
    conn = sqlite3.connect(LOG_DB)
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
    """Kodu gerçekten çalÄ±ÅŸtÄ±rÄ±r, ham çÄ±ktÄ±yÄ± yakalar ve DB'ye yazar."""
    try:
        result = subprocess.run(
            ["python3", "-c", code],
            capture_output=True, text=True, timeout=timeout
        )
        stdout, stderr, rc = result.stdout, result.stderr, result.returncode
    except subprocess.TimeoutExpired:
        stdout, stderr, rc = "", "TIMEOUT", -1

    conn = sqlite3.connect(LOG_DB)
    conn.execute(
        "INSERT INTO executions (session_id, code, stdout, stderr, returncode, ts) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (session_id, code, stdout, stderr, rc, time.time())
    )
    conn.commit()
    conn.close()

    return {"stdout": stdout, "stderr": stderr, "returncode": rc}


def has_real_execution(session_id: str, since_ts: float) -> bool:
    """Gatekeeper: bu oturumda, since_ts'ten sonra gerçek bir çalÄ±ÅŸtÄ±rma var mÄ±?"""
    conn = sqlite3.connect(LOG_DB)
    row = conn.execute(
        "SELECT COUNT(*) FROM executions WHERE session_id=? AND ts>?",
        (session_id, since_ts)
    ).fetchone()
    conn.close()
    return row[0] > 0


# ---------------------------------------------------------------------
# 2) SayÄ±sal / DB iddiasÄ± tespiti
# ---------------------------------------------------------------------
NUMERIC_CLAIM_PATTERN = re.compile(
    r"(\bSELECT\b|\bsonuç\b.*\d|\btoplam\b.*\d|=\s*\d|%\d)", re.IGNORECASE
)

def response_makes_numeric_claim(text: str) -> bool:
    return bool(NUMERIC_CLAIM_PATTERN.search(text))


# ---------------------------------------------------------------------
# 3) Model çaÄŸrÄ±sÄ± â€” DeepSeek-V4-Flash endpoint
# ---------------------------------------------------------------------
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

def call_model(messages: list, model: str = "deepseek-v4-flash") -> str:
    """
    DeepSeek-V4-Flash API'sine istek gönderir.
    Ä°lk çaÄŸrÄ±da system prompt'a format talimatÄ±nÄ± enjekte eder.
    """
    # Format talimatÄ±nÄ± system message'a ekle (yoksa)
    has_system = any(m.get("role") == "system" for m in messages)
    if not has_system:
        messages.insert(0, dict(FORMAT_SYSTEM_MSG))

    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        env_path = Path(__file__).parent.parent / ".env"
        if env_path.exists():
            for line in env_path.read_text().splitlines():
                if line.startswith("DEEPSEEK_API_KEY="):
                    api_key = line.split("=", 1)[1].strip()
                    break
    if not api_key:
        raise RuntimeError("DEEPSEEK_API_KEY bulunamadÄ± (.env veya ortam deÄŸiÅŸkeni)")

    payload = json.dumps({
        "model": model,
        "messages": messages,
        "max_tokens": 4096,
        "temperature": 0.7,
        "frequency_penalty": 0.8,
    }).encode("utf-8")

    req = urllib.request.Request(
        DEEPSEEK_API_URL,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data["choices"][0]["message"]["content"]
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        return f"API_HATASI [{e.code}]: {body[:200]}"
    except Exception as e:
        return f"ISTEK_HATASI: {e}"


def extract_code_blocks(text: str) -> list:
    """```python ... ``` içindeki kod bloklarÄ±nÄ± ayÄ±klar."""
    return [b.strip() for b in re.findall(r"```python\s*(.*?)```", text, re.DOTALL)]


# ---------------------------------------------------------------------
# 4) Gatekeeper döngüsü â€” main loop'unda call_model yerine bunu çaÄŸÄ±r
# ---------------------------------------------------------------------
def run_gatekept_turn(session_id: str, messages: list, max_retries: int = 2) -> str:
    """
    call_model() yerine bunu kullan.
    Modelin haberi olmadan:
    - Kod bloklarÄ±nÄ± yakala, çalÄ±ÅŸtÄ±r, ham çÄ±ktÄ±yÄ± geri ver
    - SayÄ±sal/DB iddiasÄ±nÄ± execution kaydÄ± olmadan geçirme
    """
    init_log()
    turn_start_ts = time.time()

    for attempt in range(max_retries + 1):
        response_text = call_model(messages)
        code_blocks = extract_code_blocks(response_text)

        # Kod varsa gerçekten çalÄ±ÅŸtÄ±r, çÄ±ktÄ±yÄ± modele geri ver
        if code_blocks:
            exec_results = [run_and_log(session_id, c) for c in code_blocks]
            messages.append({"role": "assistant", "content": response_text})
            messages.append({
                "role": "user",
                "content": f"GERÃ‡EK Ã‡ALIÅTIRMA Ã‡IKTISI:\n{json.dumps(exec_results, ensure_ascii=False, indent=2)}\n"
                           f"Bu ham çÄ±ktÄ±ya dayanarak nihai cevabÄ±nÄ± ver."
            })
            continue

        # Kod yok ama sayÄ±sal/DB iddiasÄ± varsa VE execution kaydÄ± yoksa â†’ REDDET
        if response_makes_numeric_claim(response_text) and not has_real_execution(session_id, 0):
            messages.append({"role": "assistant", "content": response_text})
            messages.append({
                "role": "user",
                "content": "REDDEDÄ°LDÄ°: SayÄ±sal/DB iddian var ama gerçek bir kod çalÄ±ÅŸtÄ±rma "
                           "kaydÄ± yok. Ã–nce ```python bloÄŸunda gerçek kod üret, "
                           "iddiayÄ± ondan sonra yaz."
            })
            continue

        # Ya iddia yok, ya da execution yapÄ±lmÄ±ÅŸ â†’ kabul
        return response_text

    return "GATEKEEPER: Maksimum deneme sayÄ±sÄ±na ulaÅŸÄ±ldÄ±, doÄŸrulanmÄ±ÅŸ cevap üretilemedi."


# ---------------------------------------------------------------------
# 5) Ã–rnek kullanÄ±m (CLI test)
# ---------------------------------------------------------------------
if __name__ == "__main__":
    import sys
    session_id = sys.argv[1] if len(sys.argv) > 1 else f"test_{int(time.time())}"
    gorev = sys.argv[2] if len(sys.argv) > 2 else "Merhaba, bugün nasÄ±lsÄ±n?"

    msgs = [{"role": "user", "content": gorev}]
    print(f"=== GATEKEEPER TEST ===\nSession: {session_id}\nGörev: {gorev}\n")
    sonuc = run_gatekept_turn(session_id, msgs)
    print(f"\n=== NÄ°HAÄ° CEVAP ===\n{sonuc}")
