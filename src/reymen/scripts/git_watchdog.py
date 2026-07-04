#!/usr/bin/env python3
"""
git_watchdog.py — Her 10dk'da bir git status --short calistirir.

Davranis:
- Degisiklik > 0 → stdout'a yaz (cron deliver eder)
- Degisiklik = 0 → sessiz, cikti vermez

Kullanim (no_agent=True ile cron job):
    cronjob create --script git_watchdog.py --no-agent --schedule "every 10m"

Konfigurasyon:
    PROJE_YOLU = degistirmek icin asagi bak
"""

import subprocess
import sys
from pathlib import Path
from datetime import datetime

# ── Konfigurasyon ──────────────────────────────────────────────
# ReYMeN-Ajan projesi
PROJE_YOLU = Path(__file__).resolve().parent.parent.parent
if not (PROJE_YOLU / ".git").exists():
    PROJE_YOLU = Path.cwd()
    if not (PROJE_YOLU / ".git").exists():
        print("[GIT_WATCHDOG] HATA: .git bulunamadi", file=sys.stderr)
        sys.exit(1)

# Paylasilan durum dosyasi (tum botlar okur)
SHARED_STATE = PROJE_YOLU / "shared_state" / "git_watchdog_state.json"
# Kendi state dosyasini git status'tan filtrele (self-trigger)
SHARED_STATE_REL = "shared_state/git_watchdog_state.json"

# ── Ana fonksiyon ──────────────────────────────────────────────
def main() -> int:
    """Git status --short calistir, degisiklik varsa yaz yoksa sessiz."""
    result = subprocess.run(
        ["git", "status", "--short"],
        capture_output=True, text=True, timeout=30,
        cwd=str(PROJE_YOLU),
    )

    if result.returncode != 0:
        print(f"[GIT_WATCHDOG] git hatasi (returncode={result.returncode})")
        print(result.stderr.strip())
        return 1

    output = result.stdout.strip()
    if not output:
        # Degisiklik yok → sessiz
        return 0

    # Degisiklik var → raporla
    raw_lines = [l for l in output.split("\n") if l.strip()]
    # Kendi state dosyasini filtrele (self-trigger)
    lines = [l for l in raw_lines if SHARED_STATE_REL not in l]
    print(f"🔍 Git Durumu — {len(lines)} dosyada degisiklik")
    print()

    # Gruplandir: M, ?? basliklari
    modified = [l for l in lines if l.startswith(" M") or l.startswith("M")]
    added = [l for l in lines if l.startswith("??")]
    deleted = [l for l in lines if l.startswith(" D") or l.startswith("D")]

    if modified:
        print(f"📝 Degisen ({len(modified)}):")
        for l in modified[:15]:
            print(f"  {l.strip()}")
        if len(modified) > 15:
            print(f"  ... ve {len(modified)-15} dosya daha")

    if added:
        print(f"\n🆕 Yeni ({len(added)}):")
        for l in added[:10]:
            print(f"  {l.strip()}")
        if len(added) > 10:
            print(f"  ... ve {len(added)-10} dosya daha")

    if deleted:
        print(f"\n🗑️ Silinen ({len(deleted)}):")
        for l in deleted[:5]:
            print(f"  {l.strip()}")
        if len(deleted) > 5:
            print(f"  ... ve {len(deleted)-5} dosya daha")

    print(f"\n📊 Toplam: {len(lines)} dosya ({len(modified)} degisen, {len(added)} yeni, {len(deleted)} silinen)")

    # Paylasilan durum dosyasina kaydet (tum botlar okur)
    _durum_kaydet(len(lines), len(modified), len(added), len(deleted), lines)
    return 0


def _durum_kaydet(toplam: int, degisen: int, yeni: int, silinen: int, ham_lines: list[str]):
    """Son durumu shared_state/git_watchdog_state.json'a yaz (tum botlar icin)."""
    import json
    try:
        SHARED_STATE.parent.mkdir(parents=True, exist_ok=True)
        SHARED_STATE.write_text(json.dumps({
            "timestamp": datetime.now().isoformat(),
            "toplam": toplam,
            "degisen": degisen,
            "yeni": yeni,
            "silinen": silinen,
            "dosyalar": [l.strip() for l in ham_lines[:50]],  # Ilk 50 dosya
            "ham_cikti": "\n".join(ham_lines),
        }, indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception as e:
        print(f"[GIT_WATCHDOG] Durum kayit hatasi: {e}", file=sys.stderr)


if __name__ == "__main__":
    sys.exit(main())
