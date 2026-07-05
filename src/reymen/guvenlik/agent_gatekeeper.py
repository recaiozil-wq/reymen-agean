"""
Agent Gatekeeper â€” ReYMeN / DeepSeek-V4-Flash için
zorunlu araç-çalÄ±ÅŸtÄ±rma doÄŸrulama iskeleti.

Amaç: Modelin "TOOL CALL yaptÄ±m" ya da "test ettim" demesine
GÃœVENMEMEK. Bunun yerine:
  1. Modelin ürettiÄŸi kodu gerçekten çalÄ±ÅŸtÄ±r.
  2. Ã‡alÄ±ÅŸtÄ±rma logunu diske yaz.
  3. Final cevap üretilmeden önce, o oturumda gerçek bir
     execution kaydÄ± var mÄ± diye kontrol et (gatekeeper).
  4. KayÄ±t yoksa cevabÄ± REDDET, modele "önce çalÄ±ÅŸtÄ±r" diye geri gönder.

Bu enforcement modelin PROMPT'una deÄŸil, bu koda dayanÄ±r.
"""

import json
import os
import re
import subprocess
import sqlite3
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

# â”€â”€ Konfigürasyon â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
PROJE_KOK = Path(__file__).resolve().parent.parent.parent.parent
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "").strip()
DEEPSEEK_BASE_URL = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
DEEPSEEK_MODEL = os.environ.get("DEEPSEEK_MODEL", "deepseek-v4-flash")
LOG_DB = PROJE_KOK / "execution_log.sqlite"


def init_log():
    """Execution log tablosunu oluÅŸtur."""
    conn = sqlite3.connect(str(LOG_DB))
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
            [sys.executable if hasattr(__import__('sys'), 'executable') else "python3", "-c", code],
            capture_output=True, text=True, timeout=timeout
        )
        stdout, stderr, rc = result.stdout, result.stderr, result.returncode
    except subprocess.TimeoutExpired:
        stdout, stderr, rc = "", "TIMEOUT", -1
    except Exception as e:
        stdout, stderr, rc = "", str(e), -1

    conn = sqlite3.connect(str(LOG_DB))
    conn.execute(
        "INSERT INTO executions (session_id, code, stdout, stderr, returncode, ts) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (session_id, code[:5000], stdout[:10000], stderr[:5000], rc, time.time())
    )
    conn.commit()
    conn.close()

    return {"stdout": stdout, "stderr": stderr, "returncode": rc}


def has_real_execution(session_id: str, since_ts: float = 0) -> bool:
    """Gatekeeper: bu oturumda, since_ts'ten sonra gerçek bir çalÄ±ÅŸtÄ±rma var mÄ±?"""
    conn = sqlite3.connect(str(LOG_DB))
    row = conn.execute(
        "SELECT COUNT(*) FROM executions WHERE session_id=? AND ts>?",
        (session_id, since_ts)
    ).fetchone()
    conn.close()
    return row[0] > 0


# ---------------------------------------------------------------------
# 2) SayÄ±sal / DB iddiasÄ± tespiti
#    ReYMeN'e özgü pattern'ler: SQL, dosya sayÄ±sÄ±, satÄ±r sayÄ±sÄ±, yüzde, hata kodu
# ---------------------------------------------------------------------
NUMERIC_CLAIM_PATTERN = re.compile(
    r"(\bSELECT\b|\bCOUNT\b|\bSUM\b|\bAVG\b|"
    r"sonuç.*\d|toplam.*\d|"
    r"=\s*\d+\.?\d*|%\s*\d+|"
    r"\d+\s*kayÄ±t|\d+\s*satÄ±r|\d+\s*dosya|"
    r"HTTP\s*\d+|exit\s*=\s*\d+|"
    r"baÅŸarÄ±lÄ±|\bbaÅŸarÄ±sÄ±z|\bhata)",
    re.IGNORECASE
)


def response_makes_numeric_claim(text: str) -> bool:
    return bool(NUMERIC_CLAIM_PATTERN.search(text))


# ---------------------------------------------------------------------
# 3) Model çaÄŸrÄ±sÄ± â€” DeepSeek-V4-Flash / OpenAI-uyumlu endpoint
# ---------------------------------------------------------------------
def call_model(messages: list, model: str = None, temperature: float = 0.3) -> str:
    """
    DeepSeek-V4-Flash API'sine OpenAI-uyumlu chat completions çaÄŸrÄ±sÄ± yapar.

    Args:
        messages:  OpenAI-uyumlu mesaj listesi [{"role": "...", "content": "..."}]
        model:     Model adÄ± (varsayÄ±lan: deepseek-v4-flash)
        temperature: SÄ±caklÄ±k (varsayÄ±lan: 0.3 â€” daha deterministik)

    Returns:
        Modelin ham metin yanÄ±tÄ±

    Raises:
        ConnectionError: API'ye eriÅŸilemezse
        ValueError: API key yoksa veya hatalÄ± yanÄ±t gelirse
    """
    if not DEEPSEEK_API_KEY or DEEPSEEK_API_KEY.startswith("***"):
        raise ValueError("DEEPSEEK_API_KEY bulunamadi. .env dosyasini kontrol edin.")

    model = model or DEEPSEEK_MODEL
    url = f"{DEEPSEEK_BASE_URL}/v1/chat/completions"

    payload = json.dumps({
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": 4096,
    }).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=payload,
        headers={
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        hata_metni = e.read().decode("utf-8", errors="replace")[:500]
        raise ConnectionError(f"HTTP {e.code}: {hata_metni}")
    except urllib.error.URLError as e:
        raise ConnectionError(f"API baglanti hatasi: {e.reason}")
    except json.JSONDecodeError as e:
        raise ValueError(f"API yaniti JSON degil: {e}")

    try:
        return body["choices"][0]["message"]["content"]
    except (KeyError, IndexError) as e:
        raise ValueError(f"API yanitinda 'choices[0].message.content' bulunamadi: {body}")


def extract_code_blocks(text: str) -> list:
    """Metinden ```python ... ``` bloklarÄ±nÄ± çÄ±karÄ±r."""
    return re.findall(r"```python\s*(.*?)```", text, re.DOTALL)


# ---------------------------------------------------------------------
# 4) Gatekeeper döngüsü â€” asÄ±l enforcement burada
# ---------------------------------------------------------------------
def run_gatekept_turn(session_id: str, messages: list, max_retries: int = 2) -> str:
    """
    Gatekeeper ile korunan model çaÄŸrÄ±sÄ±.

    Süreç:
      1. Modeli çaÄŸÄ±r
      2. Kod bloÄŸu varsa â†’ çalÄ±ÅŸtÄ±r, logla, çÄ±ktÄ±yÄ± modele geri ver
      3. SayÄ±sal/DB iddiasÄ± varsa ama execution kaydÄ± yoksa â†’ REDDET
      4. Ä°kisi de yoksa â†’ cevabÄ± kabul et

    Args:
        session_id: Oturum kimliÄŸi (UUID)
        messages:   KonuÅŸma geçmiÅŸi
        max_retries: Maksimum yeniden deneme sayÄ±sÄ±

    Returns:
        DoÄŸrulanmÄ±ÅŸ model yanÄ±tÄ±
    """
    init_log()
    turn_start_ts = time.time()

    # â”€â”€ System prompt'a kod formatÄ± talimatÄ±nÄ± ekle â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    gk_talimat = (
        "\n[GATEKEEPER KURALI]\n"
        "SayÄ±sal deÄŸer, DB sorgusu, dosya sayÄ±sÄ± veya benzer bir "
        "kanÄ±t gerektiren iddiada bulunacaksan, mutlaka önce "
        "```python\nkod bloÄŸu üret. Sistem bu bloÄŸu otomatik "
        "çalÄ±ÅŸtÄ±rÄ±p sana gerçek çÄ±ktÄ±yÄ± geri verecek. "
        "Ä°ddianÄ± ancak bu çÄ±ktÄ±ya dayanarak yaz.\n"
        "Kodsuz sayÄ±sal iddia = REDDEDÄ°LÄ°R."
    )
    system_eklendi = False
    for m in messages:
        if m.get("role") == "system":
            m["content"] += gk_talimat
            system_eklendi = True
            break
    if not system_eklendi:
        messages.insert(0, {"role": "system", "content": gk_talimat.strip()})

    for attempt in range(max_retries + 1):
        response_text = call_model(messages)
        code_blocks = extract_code_blocks(response_text)

        # â”€â”€ Kod bloÄŸu varsa gerçekten çalÄ±ÅŸtÄ±r â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        if code_blocks:
            exec_results = [run_and_log(session_id, c) for c in code_blocks]
            messages.append({"role": "assistant", "content": response_text})
            messages.append({
                "role": "user",
                "content": (
                    f"GERÃ‡EK Ã‡ALIÅTIRMA Ã‡IKTISI:\n"
                    f"{json.dumps(exec_results, ensure_ascii=False, indent=2)}\n"
                    f"Bu ham çÄ±ktÄ±ya dayanarak nihai cevabÄ±nÄ± ver."
                ),
            })
            continue  # model ham çÄ±ktÄ±yÄ± görüp nihai cevabÄ± üretsin

        # â”€â”€ SayÄ±sal/DB iddiasÄ± var ama execution kaydÄ± yok â†’ REDDET â”€â”€
        since = turn_start_ts if attempt > 0 else 0
        if response_makes_numeric_claim(response_text) and not has_real_execution(session_id, since):
            messages.append({"role": "assistant", "content": response_text})
            messages.append({
                "role": "user",
                "content": (
                    "REDDEDÄ°LDÄ°: SayÄ±sal/DB iddian var ama gerçek bir kod çalÄ±ÅŸtÄ±rma "
                    "kaydÄ± yok. Ã–nce ```python kod bloÄŸunda gerçek kod üret, "
                    "çalÄ±ÅŸmasÄ±nÄ± bekle, iddiayÄ± ondan sonra yaz."
                ),
            })
            continue

        # â”€â”€ Kabul: ya iddia yok, ya da execution gerçekten yapÄ±lmÄ±ÅŸ â”€â”€
        return response_text

    return (
        "GATEKEEPER: Maksimum deneme sayÄ±sÄ±na ulaÅŸÄ±ldÄ±, "
        "doÄŸrulanmÄ±ÅŸ cevap üretilemedi."
    )


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
if __name__ == "__main__":
    # Test
    import sys
    init_log()
    print(f"Execution log DB: {LOG_DB}")
    print(f"DeepSeek API: {DEEPSEEK_BASE_URL} model={DEEPSEEK_MODEL}")
    print(f"API Key var: {'EVET' if DEEPSEEK_API_KEY and not DEEPSEEK_API_KEY.startswith('***') else 'HAYIR'}")

    # Test: kod çalÄ±ÅŸtÄ±rma
    sonuc = run_and_log("test-session", "print('hello gatekeeper')")
    print(f"Kod calistirma testi: {sonuc}")

    # Test: sayÄ±sal iddia tespiti
    testler = [
        ("Toplam 42 kayÄ±t bulundu", True),
        ("Hata kodu: 500", True),
        ("Bu bir testtir", False),
        ("SELECT COUNT(*) FROM users = 5", True),
        ("Ä°ÅŸlem baÅŸarÄ±lÄ±", True),
    ]
    print("\nSayisal idida tespit testleri:")
    for metin, beklenen in testler:
        sonuc = response_makes_numeric_claim(metin)
        durum = "âœ…" if sonuc == beklenen else "âŒ"
        print(f"  {durum} '{metin}' -> {sonuc} (beklenen: {beklenen})")

    print("\nHazir.")
