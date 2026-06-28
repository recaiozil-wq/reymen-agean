#!/usr/bin/env python3
"""
RL Decision Layer v2.0 — Hybrid + Contextual + Auto-Threshold
Phase 3: Shadow mode (MAB parallel)
Phase 4: Hybrid mode (kural + MAB)
+ Contextual Bandit + Sliding Window + Log Rotation
"""

import sys
import os
from pathlib import Path

RL_DIR = Path(__file__).parent
sys.path.insert(0, str(RL_DIR))

from rl_skill_logger import (
    log_skill_decision, update_reward, classify_query, export_mab_data, get_stats
)
from rl_mab_engine import (
    ContextualMAB, extract_context, compute_multicomponent_reward,
    auto_adjust_threshold, rotate_log_if_needed, SlidingWindowDecay
)


class RulesEngine:
    RULES = [
        ("tor", "tor-browser-arama", 0.95),
        ("ara", "tor-browser-arama", 0.85),
        ("youtube.com", "youtube-video-isleme", 0.95),
        ("ekran goruntusu", "windows-screen-capture", 0.95),
        ("ekran al", "windows-screen-capture", 0.90),
        ("screen", "windows-screen-capture", 0.85),
        ("vision", "screen-vision-analiz", 0.90),
        ("goruntu", "screen-vision-analiz", 0.85),
        ("adb", "adb-sdk-path-fix", 0.95),
        ("apk", "android-apk-hardening", 0.95),
        ("kod", "code-exec", 0.80),
        ("script", "code-exec", 0.85),
        ("python", "code-exec", 0.80),
        ("calistir", "code-exec", 0.85),
        ("kali", "kali-linux-remote", 0.95),
        ("usb", "usb-driver-kontrol", 0.90),
        ("camera", "network-camera-discovery", 0.90),
        ("kamera", "network-camera-discovery", 0.90),
        ("obsidian", "obsidian", 0.90),
        ("cron", "cronjob", 0.90),
        ("otomasyon", "windows-system-automation", 0.85),
        ("yardim", "yardim", 0.80),
        ("help", "yardim", 0.80),
        ("nedir", "ogrenme", 0.75),
        ("ogren", "ogrenme", 0.80),
        ("ne demek", "ogrenme", 0.80),
        ("telegram", "telegram-gateway-monitor", 0.75),
        ("guvenlik", "guvenlik-izleme", 0.70),
        ("analiz", "analiz", 0.65),
        ("kontrol", "analiz", 0.60),
        ("ayar", "yapilandirma", 0.65),
        ("config", "yapilandirma", 0.70),
        ("build", "code-exec", 0.75),
        ("hata", "analiz", 0.60),
        ("log", "analiz", 0.70),
    ]

    def match(self, query: str) -> dict:
        q = query.lower()
        best_skill = None
        best_confidence = 0.0
        for keyword, skill, confidence in self.RULES:
            if keyword in q and confidence > best_confidence:
                best_confidence = confidence
                best_skill = skill
        return {"skill": best_skill, "confidence": best_confidence, "rule_based": best_skill is not None}


class RLDecisionLayer:
    MODE_SHADOW = "shadow"
    MODE_HYBRID = "hybrid"

    def __init__(self, mode: str = "hybrid", confidence_threshold: float = 0.70, auto_tune: bool = True):
        self.mode = mode
        self.confidence_threshold = confidence_threshold
        self.auto_tune = auto_tune
        self.rules = RulesEngine()
        self.mab = ContextualMAB()
        self.decay = SlidingWindowDecay(half_life_days=30, max_entries=1000)
        self.divergence_count = 0
        self.total_decisions = 0

        # Log file path
        self.log_path = RL_DIR / "skill_log.jsonl"

    def decide(self, query: str, available_skills: list) -> dict:
        self.total_decisions += 1

        context = extract_context(query)
        rule_result = self.rules.match(query)
        mab_skill = self.mab.select_arm(available_skills, context) if available_skills else None

        if self.mode == self.MODE_SHADOW:
            selected_skill = rule_result["skill"] or mab_skill
            decision_source = "rule" if rule_result["skill"] else "mab_fallback"
            if rule_result["skill"] and mab_skill and rule_result["skill"] != mab_skill:
                self.divergence_count += 1
        else:
            if rule_result["confidence"] >= self.confidence_threshold:
                selected_skill = rule_result["skill"]
                decision_source = "rule"
            elif rule_result["confidence"] >= 0.5:
                selected_skill = mab_skill or rule_result["skill"]
                decision_source = "mab_ambiguous"
            else:
                selected_skill = mab_skill
                decision_source = "mab_nomatch"

        return {
            "skill": selected_skill,
            "source": decision_source,
            "context": context,
            "rule_result": rule_result,
            "mab_skill": mab_skill
        }

    def log_and_update(self, query: str, decision: dict, user_reply: str = None) -> str:
        log_id = log_skill_decision(
            query=query,
            selected_skills=decision["skill"] or "none",
            rule_based=(decision["source"] == "rule"),
            category=classify_query(query),
            mode=self.mode,
            user_reply=user_reply,
            additional={
                "decision_source": decision["source"],
                "mab_skill": decision.get("mab_skill"),
                "context": decision.get("context", {}),
                "rule_confidence": decision.get("rule_result", {}).get("confidence", 0)
            }
        )

        if user_reply:
            from rl_skill_logger import auto_reward
            sentiment = auto_reward(user_reply)

            # Multi-component reward
            reward = compute_multicomponent_reward(
                task_complete=(sentiment > 0),
                user_corrections=(1 if sentiment < 0 else 0),
                quality_score=0.8 if sentiment > 0 else 0.3 if sentiment < 0 else 0.5
            )

            if decision["skill"] and sentiment != 0:
                self.mab.update(decision["skill"], reward, decision.get("context", {}))
                update_reward(log_id, reward)

        # Auto-adjust threshold
        if self.auto_tune and self.total_decisions % 10 == 0:
            old = self.confidence_threshold
            stats = self.mab.get_stats()
            self.confidence_threshold = auto_adjust_threshold(stats, self.confidence_threshold)
            if old != self.confidence_threshold:
                log_skill_decision(
                    f"system: threshold adjusted {old}→{self.confidence_threshold}",
                    "system_auto_tune", category="sistem"
                )

        return log_id

    def maintain_logs(self):
        """Run log maintenance: rotation + pruning."""
        rotated = rotate_log_if_needed(self.log_path)
        pruned = self.decay.prune_log(self.log_path)
        return {"rotated": rotated, "pruned": pruned}

    def switch_mode(self, mode: str):
        self.mode = mode

    def get_stats(self) -> dict:
        mab_stats = self.mab.get_stats()
        log_stats = get_stats()
        return {
            "mode": self.mode,
            "threshold": self.confidence_threshold,
            "auto_tune": self.auto_tune,
            "total_decisions": self.total_decisions,
            "divergence_count": self.divergence_count,
            "mab": mab_stats,
            "logger": log_stats
        }


if __name__ == "__main__":
    print("=== Decision Layer v2.0 ===\n")

    dl = RLDecisionLayer(mode="hybrid", auto_tune=True)

    all_skills = [
        "tor-browser-arama", "windows-screen-capture", "code-exec",
        "yardim", "android-apk-hardening", "network-camera-discovery",
        "ogrenme", "yapilandirma", "screen-vision-analiz",
        "windows-system-automation", "cronjob", "obsidian",
        "analiz", "guvenlik-izleme", "telegram-gateway-monitor",
        "kali-linux-remote", "usb-driver-kontrol", "adb-sdk-path-fix",
        "youtube-video-isleme"
    ]

    test_queries = [
        "tor ile arama yap",
        "merhaba nasilsin",
        "ekran goruntusu al",
        "bu kodu calistir",
        "apk sertlestir",
        "kamera kesfi yap",
        "bugun ne yaptin",
        "log kontrol et",
        "python script yaz internette ara",
        "cron job ayarla",
        "yardim lazim",
        "telegram baglanti sorunu",
        "kali linux kur",
        "obsidian not ac",
        "build hatasi aliyorum"
    ]

    for query in test_queries:
        decision = dl.decide(query, all_skills)
        log_id = dl.log_and_update(query, decision)
        print(f"  [{decision['source']:17s}] {query[:40]:40s} → {decision['skill'] or 'none':30s} ctx={decision['context']['length_bucket']}/{decision['context']['category']}")

    stats = dl.get_stats()
    print(f"\n--- Stats ---")
    print(f"Mode: {stats['mode']}")
    print(f"Threshold: {stats['threshold']}")
    print(f"Total decisions: {stats['total_decisions']}")
    print(f"Divergence: {stats['divergence_count']}")
    print(f"MAB contexts: {stats['mab']['total_contexts']}")
    print(f"MAB arms: {stats['mab']['total_arms']}")
    print(f"MAB accuracy: {stats['mab']['accuracy']*100:.0f}%")
    print(f"Logger entries: {stats['logger']['total_entries']}")

    # Test maintenance
    print("\n--- Maintenance Check ---")
    maint = dl.maintain_logs()
    print(f"Rotated: {maint['rotated']}")
    print(f"Pruned: {maint['pruned']} entries")
