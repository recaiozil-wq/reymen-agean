#!/usr/bin/env python3
"""
reward_v2 — Behavioral Reward Function
Ton-üstü davranışsal sinyallerle skill başarısını ölçer.

Sinyaller:
  - correction_signal: aynı konuda ardışık 2. mesaj → güçlü negatif
  - progression_signal: yeni konu/adım → güçlü pozitif
  - tone_signal: %93 doğru ton etiketi → orta ağırlık
  - silence_signal: yalnız diğer sinyallerle birlikte değerlendirilir
"""
import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

LOG_DIR = Path(__file__).parent
LOG_FILE = LOG_DIR / "skill_log.jsonl"

# Mevcut auto_reward'ı içe aktar
from rl_skill_logger import auto_reward, _hash_query


def load_recent_entries(n: int = 10) -> List[Dict]:
    """Son n log entry'i yükler."""
    if not LOG_FILE.exists():
        return []
    lines = LOG_FILE.read_text(encoding="utf-8").strip().splitlines()
    entries = [json.loads(l) for l in lines if l.strip()]
    return entries[-n:]


def compute_behavioral_reward(
    current_query: str,
    current_skill: str,
    previous_entries: List[Dict] = None,
    user_reply: str = None,
    silence_seconds: float = 0,
    category: str = None
) -> dict:
    """
    Davranışsal reward hesaplar.

    Args:
        current_query: Kullanıcının mevcut sorgusu
        current_skill: Seçilen skill
        previous_entries: Önceki log entry'leri (en son 3-5 yeterli)
        user_reply: Kullanıcının bir önceki yanıtı (tone için)
        silence_seconds: Bir önceki mesajdan bu yana geçen süre
        category: Sorgu kategorisi

    Returns:
        {"reward": float, "components": {...}}
    """
    components = {
        "correction": 0.0,
        "progression": 0.0,
        "tone": 0.0,
        "silence": 0.0
    }

    # Boş mesaj: kullanıcı bir şey söylememiş, tüm correction sıfır
    # Sessizlik ayrı sinyaldir, correction'ı kirletmez
    if current_query and current_query.strip():
        current_hash = _hash_query(current_query)
        is_empty_message = False
    else:
        current_hash = ""  # boş hash → hiçbir prev_hash ile eşleşmez
        is_empty_message = True

    # --- 1) CORRECTION SIGNAL ---
    # Aynı query_hash tekrar ediyorsa → kullanıcı düzeltme istiyor
    # Aynı skill tekrar seçilmişse → zayıf düzeltme sinyali
    # Boş mesajda correction tetiklenmez (kullanıcı bir şey söylememiş)
    if previous_entries and not is_empty_message:
        for prev in previous_entries[-3:]:  # son 3 entry'e bak
            prev_hash = prev.get("query_hash", "")
            prev_skills = prev.get("selected_skills", "")
            if isinstance(prev_skills, list):
                prev_skills = ",".join(prev_skills)

            if prev_hash == current_hash:
                # Aynı sorgu tekrar → güçlü düzeltme talebi
                components["correction"] = -0.6
                break
            elif prev_skills and current_skill and prev_skills == current_skill:
                # Aynı skill ama farklı sorgu → zayıf düzeltme
                components["correction"] = min(components["correction"], -0.3)

    # --- 2) PROGRESSION SIGNAL ---
    # Kategori değiştiyse → yeni adıma geçilmiş, önceki başarılı
    if previous_entries and category:
        last_entry = previous_entries[-1]
        prev_cat = last_entry.get("category", "")
        prev_hash = last_entry.get("query_hash", "")
        current_cat = category

        if current_cat and prev_cat and current_cat != prev_cat:
            # Kategori değişmiş → yeni konu, önceki adım başarılı
            components["progression"] = 0.5
        elif current_hash != prev_hash:
            # Aynı kategoride farklı sorgu → zayıf ilerleme
            components["progression"] = 0.2

    # --- 3) TONE SIGNAL (orta ağırlık) ---
    if user_reply:
        tone = auto_reward(user_reply)
        # Tone tek başına karar vermez, orta ağırlık
        components["tone"] = tone * 0.4
    else:
        components["tone"] = 0.0

    # --- 4) SILENCE SIGNAL (modülatör) ---
    if silence_seconds > 300:
        components["silence"] = -0.3
    elif silence_seconds > 120:
        components["silence"] = -0.15
    else:
        components["silence"] = 0.0

    # --- AĞIRLIKLANDIRMA ---
    # Correction varsa (skill veya hash bazlı), progression ve tone'u ezer
    # Aynı skill tekrar seçilmişse, bu "yeni adım" değil "düzeltme"dir
    # Davranışsal sinyal (correction) tonu yenmeli
    if components["correction"] < 0:
        components["progression"] = 0.0
        components["tone"] = 0.0

    reward = components["correction"] + components["progression"] + components["tone"]

    # Silence modülasyonu: correction veya progression ile birlikteyse
    if components["silence"] < 0:
        if components["correction"] < 0:
            reward += components["silence"]  # sessizlik + düzeltme = daha kötü
        elif components["progression"] == 0 and components["tone"] == 0:
            pass  # sadece sessizlik, tek başına 0
        else:
            reward += components["silence"] * 0.5

    # Reward'u -1.0 ile +1.0 arasına sıkıştır
    reward = max(-1.0, min(1.0, reward))

    return {
        "reward": round(reward, 3),
        "components": {k: round(v, 3) for k, v in components.items()}
    }


def batch_evaluate(entries: List[Dict]) -> List[Dict]:
    """
    Toplu değerlendirme: her entry için reward_v2 hesaplar.
    entries, skill_log.jsonl'den alınmış sıralı kayıtlardır.
    Her entry için önceki entry'leri kullanarak reward hesaplar.
    """
    results = []
    for i, entry in enumerate(entries):
        prev = entries[:i]  # sadece önceki entry'ler
        query = entry.get("query", "")  # not: query metni log'da yoksa empty
        query_hash = entry.get("query_hash", "")
        skill = entry.get("selected_skills", "")
        if isinstance(skill, list):
            skill = ",".join(skill)
        category = entry.get("category", "")
        existing_reward = entry.get("reward", 0)

        # Query metni log'da olmadığı için hash üzerinden çalışıyoruz
        # Tone sinyali için user_reply gerekli — log'da yok
        result = compute_behavioral_reward(
            current_query=query_hash,  # hash kullanıyoruz
            current_skill=skill,
            previous_entries=prev,
            user_reply=None,  # log'da user_reply yok
            silence_seconds=0,
            category=category
        )

        results.append({
            "index": i + 1,
            "query_hash": query_hash[:14],
            "skill": skill[:30],
            "category": category,
            "existing_reward": existing_reward,
            "v2_reward": result["reward"],
            "components": result["components"]
        })

    return results


if __name__ == "__main__":
    # Test: son 40 kaydı dene
    entries = load_recent_entries(40)
    print(f"Toplam {len(entries)} entry yuklendi")
    print()

    results = batch_evaluate(entries)

    print(f"{'#':>3} {'Hash':<14} {'Skill':<30} {'Kat':<10} {'Eski':>6} {'v2':>6} {'corr':>6} {'prog':>6} {'tone':>6} {'sil':>6}")
    print("-" * 95)
    for r in results:
        c = r["components"]
        print(f"{r['index']:>3} {r['query_hash']:<14} {r['skill']:<30} {r['category']:<10} {r['existing_reward']:>6} {r['v2_reward']:>6} {c['correction']:>6} {c['progression']:>6} {c['tone']:>6} {c['silence']:>6}")

    print()
    # v2 reward dagilimi
    rewards = {"positif": 0, "notr": 0, "negatif": 0}
    for r in results:
        if r["v2_reward"] > 0.1:
            rewards["positif"] += 1
        elif r["v2_reward"] < -0.1:
            rewards["negatif"] += 1
        else:
            rewards["notr"] += 1
    print(f"v2 Reward dagilimi: +:{rewards['positif']} 0:{rewards['notr']} -:{rewards['negatif']}")
