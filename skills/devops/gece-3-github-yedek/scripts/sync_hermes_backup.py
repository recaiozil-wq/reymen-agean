"""
ReYMeN BACKUP SYNC — no_agent script
Günlük: skills + memory + state.db diff → sadece farkları push et
Sessiz çalışır (fark yoksa çıktı vermez)

Cron: gunluk-backup-sync (no_agent=true, her gün 21:00)
"""

import hashlib, json, os, shutil, subprocess, sys, zipfile
from datetime import datetime
from pathlib import Path
import logging
logger = logging.getLogger(__name__)

# --- CONFIG ---
ReYMeN_HOME = Path(os.environ.get("ReYMeN_HOME",
    r"C:\Users\marko\AppData\Local\ReYMeN"))
BACKUP_DIR = Path(os.environ.get("USERPROFILE", r"C:\Users\marko")) / "ReYMeN-backup"
LOG_FILE = ReYMeN_HOME / "logs" / "backup-sync.log"

def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line)
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def file_hash(path):
    if not path.exists() or not path.is_file():
        return None
    h = hashlib.sha256()
    h.update(str(path.stat().st_size).encode())
    h.update(str(int(path.stat().st_mtime)).encode())
    with open(path, "rb") as f:
        chunk = f.read(65536)
        h.update(chunk)
    return h.hexdigest()[:16]

def dir_manifest(path):
    manifest = {}
    if not path.exists():
        return manifest
    for f in sorted(path.rglob("*")):
        if f.is_file() and f.name != ".bundled_manifest":
            rel = f.relative_to(path)
            manifest[str(rel)] = file_hash(f)
    return manifest

def dir_diff(local_manifest, repo_manifest):
    added = {}
    modified = {}
    all_keys = set(local_manifest.keys()) | set(repo_manifest.keys())
    for key in all_keys:
        lh = local_manifest.get(key)
        rh = repo_manifest.get(key)
        if lh and not rh:
            added[key] = lh
        elif lh and rh and lh != rh:
            modified[key] = (rh, lh)
    return added, modified

def git_push(repo_path):
    subprocess.run(["git", "add", "-A"], cwd=repo_path, capture_output=True, timeout=15)
    result = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=repo_path, capture_output=True, timeout=15)
    if result.returncode == 0:
        return False
    date_str = datetime.now().strftime("%Y-%m-%d_%H:%M")
    subprocess.run(["git", "commit", "-m", f"auto-sync {date_str}"], cwd=repo_path, capture_output=True, timeout=30)
    push = subprocess.run(["git", "push", "origin", "main"], cwd=repo_path, capture_output=True, text=True, timeout=120)
    if push.returncode != 0:
        log(f"PUSH HATASI: {push.stderr.strip()[:200]}")
        return False
    return True

def main():
    changes = False

    if not (BACKUP_DIR / ".git").exists():
        log("Backup repo yok - klonlaniyor")
        subprocess.run(["git", "clone", "https://github.com/asdafgf/ReYMeN-full-backup.git", str(BACKUP_DIR)], timeout=120)
        log("Repo klonlandi")
        changes = True

    subprocess.run(["git", "pull", "--ff-only"], cwd=BACKUP_DIR, capture_output=True, timeout=30)

    # Skills diff
    ReYMeN_SKILLS = ReYMeN_HOME / "skills"
    REPO_SKILLS = BACKUP_DIR / "skills"

    if ReYMeN_SKILLS.exists() and REPO_SKILLS.exists():
        local_skills = dir_manifest(ReYMeN_SKILLS)
        repo_skills = dir_manifest(REPO_SKILLS)
        added, modified = dir_diff(local_skills, repo_skills)

        if added or modified:
            shutil.rmtree(REPO_SKILLS, ignore_errors=True)
            shutil.copytree(ReYMeN_SKILLS, REPO_SKILLS,
                ignore=shutil.ignore_patterns(
                    ".bundled_manifest", ".usage.json", ".usage.json.lock",
                    ".curator_state", ".curator_backups", ".hub", "__pycache__", "*.pyc"))
            log(f"Skills: {len(added)} yeni, {len(modified)} degismis")
            changes = True

    # Memory
    MEMORIES = ReYMeN_HOME / "memories"
    REPO_MEMOR = BACKUP_DIR / "ReYMeN Memor"
    if MEMORIES.exists():
        REPO_MEMOR.mkdir(parents=True, exist_ok=True)
        for fname in ["MEMORY.md", "USER.md"]:
            src = MEMORIES / fname
            dst = REPO_MEMOR / fname
            if src.exists():
                shutil.copy2(src, dst)
                log(f"Memory: {fname}")
                changes = True

    # state.db
    STATE_DB = ReYMeN_HOME / "state.db"
    PART1 = BACKUP_DIR / "ReYMeN-state-part001.zip"
    PART2 = BACKUP_DIR / "ReYMeN-state-part002.zip"

    if STATE_DB.exists():
        current_size = STATE_DB.stat().st_size
        last_size = 0
        if PART1.exists() and PART2.exists():
            last_size = (PART1.stat().st_size + PART2.stat().st_size) * 3

        mtime_diff = datetime.now().timestamp() - STATE_DB.stat().st_mtime
        size_diff = abs(current_size - last_size)

        if size_diff > 1_000_000 or (mtime_diff < 3600 and size_diff > 100_000):
            zip_path = BACKUP_DIR / "ReYMeN-state-full.zip"
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                zf.write(STATE_DB, arcname="state.db")
                for ext in ["-wal", "-shm"]:
                    f = STATE_DB.parent / f"state.db{ext}"
                    if f.exists():
                        zf.write(f, arcname=f"state.db{ext}")
            zip_data = zip_path.read_bytes()
            part_size = 55 * 1024 * 1024
            PART1.write_bytes(zip_data[:part_size])
            PART2.write_bytes(zip_data[part_size:])
            zip_path.unlink()
            log(f"state.db: {current_size/1024/1024:.0f}MB -> zip")
            changes = True

    if changes:
        if git_push(BACKUP_DIR):
            log("✓ GitHub'a push edildi")
    else:
        log("Her sey guncel")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"HATA: {e}")
        sys.exit(1)
