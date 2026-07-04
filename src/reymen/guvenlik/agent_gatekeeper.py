"""
Agent Gatekeeper — Hermes / DeepSeek-V4-Flash için
zorunlu araç-çalıştırma doğrulama iskeleti.

Amaç: Modelin "TOOL CALL yaptım" ya da "test ettim" demesine
GÜVENMEMEK. Bunun yerine:
  1. Modelin ürettiği kodu gerçekten çalıştır.
  2. Çalıştırma logunu diske yaz.
  3. Final cevap üretilmeden önce, o oturumda gerçek bir
     execution kaydı var mı diye kontrol et (gatekeeper).
  4. Kayıt yoksa cevabı REDDET, modele "önce çalıştır" diye geri gönder.

Bu enforcement modelin PROMPT'una değil, bu koda dayanır.
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

# ── Konfigürasyon ──────────────────────────────────────────────
PROJE_KOK = Path(__file__).resolve().parent.parent.parent.parent
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "").strip()
DEEPSEEK_BASE_URL = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
DEEPSEEK_MODEL = os.environ.get("DEEPSEEK_MODEL", "deepseek-v4-flash")
LOG_DB = PROJE_KOK / "execution_log.sqlite"


def init_log():
    """Execution log tablosunu oluştur."""
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
    """Kodu gerçekten çalıştırır, ham çıktıyı yakalar ve DB'ye yazar."""
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
    """Gatekeeper: bu oturumda, since_ts'ten sonra gerçek bir çalıştırma var mı?"""
    conn = sqlite3.connect(str(LOG_DB))
    row = conn.execute(
        "SELECT COUNT(*) FROM executions WHERE session_id=? AND ts>?",
        (session_id, since_ts)
    ).fetchone()
    conn.close()
    return row[0] > 0


# ---------------------------------------------------------------------
# 2) Sayısal / DB iddiası tespiti
#    ReYMeN'e özgü pattern'ler: SQL, dosya sayısı, satır sayısı, yüzde, hata kodu
# ---------------------------------------------------------------------
NUMERIC_CLAIM_PATTERN = re.compile(
    r"(\bSELECT\b|\bCOUNT\b|\bSUM\b|\bAVG\b|"
    r"sonuç.*\d|toplam.*\d|"
    r"=\s*\d+\.?\d*|%\s*\d+|"
    r"\d+\s*kayıt|\d+\s*satır|\d+\s*dosya|"
    r"HTTP\s*\d+|exit\s*=\s*\d+|"
    r"başarılı|\bbaşarısız|\bhata)",
    re.IGNORECASE
)


def response_makes_numeric_claim(text: str) -> bool:
    return bool(NUMERIC_CLAIM_PATTERN.search(text))


# ---------------------------------------------------------------------
# 3) Model çağrısı — DeepSeek-V4-Flash / OpenAI-uyumlu endpoint
# ---------------------------------------------------------------------
def call_model(messages: list, model: str = None, temperature: float = 0.3) -> str:
    """
    DeepSeek-V4-Flash API'sine OpenAI-uyumlu chat completions çağrısı yapar.

    Args:
        messages:  OpenAI-uyumlu mesaj listesi [{"role": "...", "content": "..."}]
        model:     Model adı (varsayılan: deepseek-v4-flash)
        temperature: Sıcaklık (varsayılan: 0.3 — daha deterministik)

    Returns:
        Modelin ham metin yanıtı

    Raises:
        ConnectionError: API'ye erişilemezse
        ValueError: API key yoksa veya hatalı yanıt gelirse
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
    """Metinden ```python ... ``` bloklarını çıkarır."""
    return re.findall(r"```python\s*(.*?)```", text, re.DOTALL)


# ---------------------------------------------------------------------
# 4) Gatekeeper döngüsü — asıl enforcement burada
# ---------------------------------------------------------------------
def run_gatekept_turn(session_id: str, messages: list, max_retries: int = 2) -> str:
    """
    Gatekeeper ile korunan model çağrısı.

    Süreç:
      1. Modeli çağır
      2. Kod bloğu varsa → çalıştır, logla, çıktıyı modele geri ver
      3. Sayısal/DB iddiası varsa ama execution kaydı yoksa → REDDET
      4. İkisi de yoksa → cevabı kabul et

    Args:
        session_id: Oturum kimliği (UUID)
        messages:   Konuşma geçmişi
        max_retries: Maksimum yeniden deneme sayısı

    Returns:
        Doğrulanmış model yanıtı
    """
    init_log()
    turn_start_ts = time.time()

    # ── System prompt'a kod formatı talimatını ekle ────────────
    gk_talimat = (
        "\n[GATEKEEPER KURALI]\n"
        "Sayısal değer, DB sorgusu, dosya sayısı veya benzer bir "
        "kanıt gerektiren iddiada bulunacaksan, mutlaka önce "
        "```python\nkod bloğu üret. Sistem bu bloğu otomatik "
        "çalıştırıp sana gerçek çıktıyı geri verecek. "
        "İddianı ancak bu çıktıya dayanarak yaz.\n"
        "Kodsuz sayısal iddia = REDDEDİLİR."
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

        # ── Kod bloğu varsa gerçekten çalıştır ─────────────────
        if code_blocks:
            exec_results = [run_and_log(session_id, c) for c in code_blocks]
            messages.append({"role": "assistant", "content": response_text})
            messages.append({
                "role": "user",
                "content": (
                    f"GERÇEK ÇALIŞTIRMA ÇIKTISI:\n"
                    f"{json.dumps(exec_results, ensure_ascii=False, indent=2)}\n"
                    f"Bu ham çıktıya dayanarak nihai cevabını ver."
                ),
            })
            continue  # model ham çıktıyı görüp nihai cevabı üretsin

        # ── Sayısal/DB iddiası var ama execution kaydı yok → REDDET ──
        since = turn_start_ts if attempt > 0 else 0
        if response_makes_numeric_claim(response_text) and not has_real_execution(session_id, since):
            messages.append({"role": "assistant", "content": response_text})
            messages.append({
                "role": "user",
                "content": (
                    "REDDEDİLDİ: Sayısal/DB iddian var ama gerçek bir kod çalıştırma "
                    "kaydı yok. Önce ```python kod bloğunda gerçek kod üret, "
                    "çalışmasını bekle, iddiayı ondan sonra yaz."
                ),
            })
            continue

        # ── Kabul: ya iddia yok, ya da execution gerçekten yapılmış ──
        return response_text

    return (
        "GATEKEEPER: Maksimum deneme sayısına ulaşıldı, "
        "doğrulanmış cevap üretilemedi."
    )


# ═══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    # Test
    import sys
    init_log()
    print(f"Execution log DB: {LOG_DB}")
    print(f"DeepSeek API: {DEEPSEEK_BASE_URL} model={DEEPSEEK_MODEL}")
    print(f"API Key var: {'EVET' if DEEPSEEK_API_KEY and not DEEPSEEK_API_KEY.startswith('***') else 'HAYIR'}")

    # Test: kod çalıştırma
    sonuc = run_and_log("test-session", "print('hello gatekeeper')")
    print(f"Kod calistirma testi: {sonuc}")

    # Test: sayısal iddia tespiti
    testler = [
        ("Toplam 42 kayıt bulundu", True),
        ("Hata kodu: 500", True),
        ("Bu bir testtir", False),
        ("SELECT COUNT(*) FROM users = 5", True),
        ("İşlem başarılı", True),
    ]
    print("\nSayisal idida tespit testleri:")
    for metin, beklenen in testler:
        sonuc = response_makes_numeric_claim(metin)
        durum = "✅" if sonuc == beklenen else "❌"
        print(f"  {durum} '{metin}' -> {sonuc} (beklenen: {beklenen})")

    print("\nHazir.")
