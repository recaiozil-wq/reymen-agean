#!/usr/bin/env python3
"""
RL Skill Logger v1.5 — ReYMeN Agent Observation Infrastructure
Logs every skill selection decision for future MAB training.
"""

import json
import hashlib
import uuid
import os
import re
from datetime import datetime
from pathlib import Path
import logging
logger = logging.getLogger(__name__)

LOG_DIR = Path(__file__).parent
LOG_FILE = LOG_DIR / "skill_log.jsonl"

# --- Sentiment keywords ---
POSITIVE_KEYWORDS = [
    "tesekkur", "tamam", "oldu", "harika", "cozuldu",
    "mukemmel", "dogru", "super", "guzel", "eyvallah",
    "saol", "tşk", "helal", "iyi", "sorun kalmadi",
    "oldubitti", "hallettim", "bitti", "works",
    "evet", "anladim", "devam", "güzel", "başarılı",
    "sen karar ver", "uygula", "yap", "tmm"
]
NEGATIVE_KEYWORDS = [
    "yanlis oldu", "yanlis yaptin", "istemedigim",
    "anlamadin beni", "anlamadin", "duzelt bunu",
    "hatali calisiyor", "olmamis bu", "calismadi",
    "sorun var", "hata verdi", "bozuk bu",
    "yanlis anladin", "dogru degil", "olmadi yani"
]

# --- Category keywords ---
CATEGORY_KEYWORDS = {
    "kod": ["kod", "kodla", "yaz", "script", "python", "program", "calistir", "build"],
    "guvenlik": ["guvenlik", "exploit", "cve", "zafiyet", "saldiri", "reversing"],
    "arama": ["tor", "ara", "bul", "internet", "search", "web"],
    "analiz": ["analiz", "incele", "kontrol", "log", "debug", "test"],
    "goruntu": ["ekran", "gor", "screen", "vision", "foto", "resim"],
    "ogrenme": ["ogren", "egitim", "ders", "ne demek", "nedir", "tutorial"],
    "yapilandirma": ["ayar", "yapilandir", "kur", "config", "setup", "install"],
    "yardim": ["yardim", "help", "ne yapabilirsin", "komutlar"]
}


def _hash_query(query: str) -> str:
    """MD5 first 12 chars — enough for dedup, no PII."""
    return hashlib.md5(query.encode()).hexdigest()[:12]


def classify_query(query: str) -> str:
    """Rule-based keyword classification."""
    q = query.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in q:
                return category
    return "genel"


def auto_reward(user_message: str) -> int:
    """
    Detect user sentiment from message text.
    Returns +1 (positive), -1 (negative), or 0 (neutral).
    Negative signals checked first.
    """
    msg = user_message.lower()
    for kw in NEGATIVE_KEYWORDS:
        if kw in msg:
            return -1
    for kw in POSITIVE_KEYWORDS:
        if kw in msg:
            return +1
    return 0


def log_skill_decision(
    query: str,
    selected_skills,
    rule_based: bool = True,
    reward: int = 0,
    category: str = None,
    mode: str = None,
    user_reply: str = None,
    additional: dict = None
) -> str:
    """
    Log a skill selection decision.
    Returns log_id (UUID4) for future reward updates.
    
    Args:
        query: Original user query
        selected_skills: Skill name (str) or list of skill names
        rule_based: True if rule-decided, False if MAB-decided
        reward: Initial reward value (0 = neutral)
        category: Query category (auto-classified if not provided)
        mode: Active mode (optional)
        user_reply: If provided, auto_reward() runs and overrides reward
        additional: Extra fields to include in the log entry
    """
    log_id = str(uuid.uuid4())
    
    if isinstance(selected_skills, str):
        selected_skills = [selected_skills]
    
    if category is None:
        category = classify_query(query)
    
    if user_reply is not None:
        auto_val = auto_reward(user_reply)
        if auto_val != 0:
            reward = auto_val
    
    entry = {
        "log_id": log_id,
        "timestamp": datetime.now().isoformat(),
        "query_hash": _hash_query(query),
        "query_length": len(query),
        "category": category,
        "selected_skills": selected_skills,
        "rule_based": rule_based,
        "reward": reward,
        "mode": mode or "default"
    }
    
    if additional:
        entry["additional"] = additional
    
    # Append to log
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    
    return log_id


def update_reward(log_id: str, new_reward: int) -> bool:
    """
    Update reward for a specific log entry by log_id.
    Rewrites the file (acceptable at current scale).
    """
    if not LOG_FILE.exists():
        return False
    
    updated = False
    lines = LOG_FILE.read_text(encoding="utf-8").splitlines()
    new_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
            if entry.get("log_id") == log_id:
                entry["reward"] = new_reward
                updated = True
            new_lines.append(json.dumps(entry, ensure_ascii=False))
        except json.JSONDecodeError:
            new_lines.append(line)
    
    if updated:
        LOG_FILE.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
    
    return updated


def update_reward_by_hash(query_hash: str, new_reward: int) -> int:
    """
    Legacy: update the most recent entry matching this hash.
    Returns number of entries updated (0 or 1).
    """
    if not LOG_FILE.exists():
        return 0
    
    lines = LOG_FILE.read_text(encoding="utf-8").splitlines()
    new_lines = []
    found_idx = -1
    
    # Find the LAST matching entry (most recent)
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
            if entry.get("query_hash") == query_hash:
                found_idx = i
        except json.JSONDecodeError:
            logger.warning("[fix_01_sessiz_except] JSONDecodeError")
    
    if found_idx == -1:
        return 0
    
    # Update only that entry
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
            if i == found_idx:
                entry["reward"] = new_reward
            new_lines.append(json.dumps(entry, ensure_ascii=False))
        except json.JSONDecodeError:
            new_lines.append(line)
    
    LOG_FILE.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
    return 1


def export_mab_data() -> dict:
    """
    Prepare data for MAB engine.
    Returns {skill_name: {alpha, beta, total}} 
    alpha = non-negative reward count, beta = negative reward count.
    """
    if not LOG_FILE.exists():
        return {}
    
    skill_data = {}
    
    for line in LOG_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        
        for skill in entry.get("selected_skills", []):
            if skill not in skill_data:
                skill_data[skill] = {"alpha": 1, "beta": 1, "total": 0}
            
            skill_data[skill]["total"] += 1
            reward = entry.get("reward", 0)
            if reward >= 0:
                skill_data[skill]["alpha"] += 1
            else:
                skill_data[skill]["beta"] += 1
    
    return skill_data


def get_stats() -> dict:
    """Return summary statistics from the log."""
    if not LOG_FILE.exists():
        return {"total_entries": 0, "skills": {}, "categories": {}, "rewards": {}, "by_source": {"rule": 0, "mab": 0}}
    
    total = 0
    skills = {}
    categories = {}
    reward_sum = {"positive": 0, "negative": 0, "neutral": 0}
    by_source = {"rule": 0, "mab": 0}
    
    for line in LOG_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        
        total += 1
        
        for skill in entry.get("selected_skills", []):
            skills[skill] = skills.get(skill, 0) + 1
        
        cat = entry.get("category", "genel")
        categories[cat] = categories.get(cat, 0) + 1
        
        r = entry.get("reward", 0)
        if r > 0:
            reward_sum["positive"] += 1
        elif r < 0:
            reward_sum["negative"] += 1
        else:
            reward_sum["neutral"] += 1
        
        if entry.get("rule_based", True):
            by_source["rule"] += 1
        else:
            by_source["mab"] += 1
    
    return {
        "total_entries": total,
        "skills": skills,
        "categories": categories,
        "rewards": reward_sum,
        "by_source": by_source
    }


if __name__ == "__main__":
    # Quick test
    print("=== RL Skill Logger v1.5 ===\n")
    
    lid = log_skill_decision("merhaba yardim", "yardim", category="yardim")
    print(f"Logged entry: {lid}")
    
    lid2 = log_skill_decision("ekran goruntusu al", "goruntu-ekran", reward=0)
    print(f"Logged entry: {lid2}")
    
    lid3 = log_skill_decision(
        "python script yaz", ["kod", "python-testing"],
        user_reply="tesekkurler harika oldu"
    )
    print(f"Logged entry (auto-reward): {lid3}")
    
    print("\nLog stats:")
    stats = get_stats()
    print(json.dumps(stats, indent=2, ensure_ascii=False))
    
    print("\nMAB data:")
    mab = export_mab_data()
    print(json.dumps(mab, indent=2, ensure_ascii=False))
