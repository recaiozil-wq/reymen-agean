import subprocess, json, sys
from pathlib import Path
from datetime import datetime
from src.core.model_adapter import get_active_adapter

MAX_RETRIES = 3
adapter = None  # lazy init


def _get_adapter():
    global adapter
    if adapter is None:
        adapter = get_active_adapter()
    return adapter


def run_script(path: str) -> tuple[bool, str]:
    """Python script çalıştır. Döner: (başarılı_mı, çıktı/hata)"""
    try:
        r = subprocess.run(
            [sys.executable, path], capture_output=True, text=True, timeout=120
        )
        return r.returncode == 0, r.stdout if r.returncode == 0 else r.stderr
    except subprocess.TimeoutExpired:
        return False, "TIMEOUT: 120s aşıldı"
    except Exception as e:
        return False, str(e)


def ask_model_to_fix(code: str, error: str) -> str:
    """LLM'e hata mesajını gönder, düzeltilmiş kod al"""
    prompt = f"""Şu Python kodu çalıştırıldı ve hata verdi.

HATA:
{error}

KOD:
{code}

Görevi:
1. Hatanın kaynağını belirle
2. Düzelt
3. Sadece çalışan Python kodunu döndür — açıklama yok, markdown yok
"""
    return _get_adapter().complete(prompt)


def solve_step(step_name: str, script_path: str) -> bool:
    """Tek adımı çöz. Hata varsa max 3 kere dene."""
    path = Path(script_path)
    if not path.exists():
        print(f"[{step_name}] ❌ Script bulunamadı: {path}")
        return False

    for attempt in range(1, MAX_RETRIES + 1):
        print(f"[{step_name}] ── Deneme {attempt}/{MAX_RETRIES}")
        success, output = run_script(str(path))
        if success:
            print(f"[{step_name}] ✅ Geçti")
            _log("logs/run_log.jsonl", step_name, attempt, True, output[:400])
            return True

        print(f"[{step_name}] ❌ Hata → modele gönderiliyor")
        print(f"  stderr: {output[:200]}")
        fixed = ask_model_to_fix(path.read_text("utf-8"), output)

        fix_dir = path.parent / "fix"
        fix_dir.mkdir(exist_ok=True)
        fix_path = fix_dir / f"{path.stem}_fix_v{attempt}.py"
        fix_path.write_text(fixed, "utf-8")
        print(f"[{step_name}]   → Fix yazıldı: {fix_path.name}")
        path = fix_path

    print(f"[{step_name}] 💀 Geçilemedi — loglandı")
    _log("logs/fail_log.jsonl", step_name, MAX_RETRIES, False, output[:400])
    return False


def solve_all(steps: list[tuple[str, str]]) -> dict:
    """Tüm adımları sırayla çöz. Döner: {step_name: success_bool}"""
    results = {}
    for name, path in steps:
        results[name] = solve_step(name, path)
    return results


def _log(file: str, step, attempt, success, output):
    Path(file).parent.mkdir(exist_ok=True)
    entry = {
        "ts": datetime.now().isoformat(),
        "step": step,
        "attempt": attempt,
        "ok": success,
        "tail": output,
    }
    with open(file, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


# ── Doğrudan hata çözümü (motor.py'den çağrılacak) ──────────


def coz_hata(hata: str, kod: str = "", ad: str = "acil_fix") -> str:
    """Herhangi bir hatayı LLM'e sor, düzeltilmiş kod al.
    Motor.py'de try/except içinde çağrılır."""
    if not kod:
        return f"[COZ] Hata loglandı: {hata[:200]}"
    fix = ask_model_to_fix(kod, hata)
    _log("logs/acil_fix_log.jsonl", ad, 1, False, hata[:200])
    return fix
