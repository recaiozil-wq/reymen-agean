"""Session gecmisi yonetimi."""
import json, os
from datetime import datetime
from pathlib import Path

SESSIONS_DIR = Path.home() / ".deepseek_ajan" / "sessions"
MAX_MESSAGES = 100

def _ensure():
    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)

def path(name):
    _ensure()
    return SESSIONS_DIR / f"{name}.jsonl"

def listele():
    _ensure()
    ss = sorted(SESSIONS_DIR.glob("*.jsonl"), key=os.path.getmtime, reverse=True)
    result = []
    for i, s in enumerate(ss, 1):
        size = sum(1 for _ in open(s))
        mt = datetime.fromtimestamp(os.path.getmtime(s)).strftime("%d/%m %H:%M")
        result.append({"id": i, "name": s.stem, "mesaj": size, "tarih": mt})
    return result

def kaydet(ad, messages):
    if not ad:
        ad = "sohbet_" + datetime.now().strftime("%Y%m%d_%H%M%S")
    p = path(ad)
    with open(p, "w", encoding="utf-8") as f:
        for m in messages[-MAX_MESSAGES:]:
            f.write(json.dumps(m, ensure_ascii=False) + "\n")
    return p

def yukle(ad):
    p = path(ad)
    if not p.exists():
        ss = sorted(SESSIONS_DIR.glob("*.jsonl"), key=os.path.getmtime, reverse=True)
        try:
            idx = int(ad) - 1
            if 0 <= idx < len(ss):
                p = ss[idx]
        except ValueError:
            pass
    if not p.exists():
        return None
    msgs = []
    with open(p, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                msgs.append(json.loads(line))
    return msgs

def sil(ad):
    p = path(ad)
    if p.exists():
        p.unlink()
        return True
    return False
