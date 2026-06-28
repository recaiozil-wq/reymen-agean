#!/usr/bin/env python3
"""
MAB Engine v2.0 — Thompson Sampling + Contextual Bandit + Sliding Window
ReYMeN Agent skill selection optimization.
"""

import json
import random
import math
from pathlib import Path
from datetime import datetime, timedelta
import logging
logger = logging.getLogger(__name__)

LOG_DIR = Path(__file__).parent
LOGGER_PATH = LOG_DIR / "rl_skill_logger.py"
import importlib.util
spec = importlib.util.spec_from_file_location("rl_skill_logger", LOGGER_PATH)
logger = importlib.util.module_from_spec(spec)
spec.loader.exec_module(logger)


def extract_context(query: str) -> dict:
    """Extract context features from a query for contextual bandit."""
    q = query.lower()
    return {
        "length_bucket": "short" if len(q) < 20 else "medium" if len(q) < 60 else "long",
        "category": logger.classify_query(query),
        "has_code": any(kw in q for kw in ["kod", "python", "script", "calistir", "build"]),
        "has_question": "?" in q,
        "word_count": len(q.split())
    }


class ContextualMAB:
    """
    Contextual Multi-Armed Bandit using Thompson Sampling.
    Maintains separate Beta distributions per context category.
    Supports full skill seeding from skill_seed.json (622 skills).
    """

    def __init__(self, seed_data: dict = None):
        self.contexts = {}  # {context_key: {arm: {"alpha": 1, "beta": 1}}}
        self.total_pulls = 0
        self.results = {"correct": 0, "incorrect": 0, "total": 0}
        self.seed_path = LOG_DIR / "skill_seed.json"
        self._load_seed()

    def _load_seed(self):
        """Load all 622 skills from seed file so MAB knows about them."""
        try:
            if self.seed_path.exists():
                with open(self.seed_path, "r", encoding="utf-8") as f:
                    seed = json.load(f)
                # Seed all skills under "genel" context as neutral starting point
                # They'll get real data as they're actually used
                ctx_genel = "len_medium|cat_genel"
                if ctx_genel not in self.contexts:
                    self.contexts[ctx_genel] = {}
                for skill_name, data in seed.items():
                    if skill_name not in self.contexts[ctx_genel]:
                        self.contexts[ctx_genel][skill_name] = {
                            "alpha": 1,
                            "beta": 1,
                            "pulls": 0
                        }
                print(f"[MAB] Seed yuklendi: {len(seed)} skill ({ctx_genel})")
        except Exception as e:
            print(f"[MAB] Seed yukleme hatasi (onemsiz): {e}")

    def _get_context_key(self, context: dict) -> str:
        """Generate a context key from features."""
        return f"len_{context['length_bucket']}|cat_{context['category']}"

    def _ensure_arm(self, ctx_key: str, arm: str):
        if ctx_key not in self.contexts:
            self.contexts[ctx_key] = {}
        if arm not in self.contexts[ctx_key]:
            # Check if skill exists in genel seed → inherit seed values
            ctx_genel = "len_medium|cat_genel"
            if ctx_genel in self.contexts and arm in self.contexts[ctx_genel]:
                seed = self.contexts[ctx_genel][arm]
                self.contexts[ctx_key][arm] = {
                    "alpha": seed["alpha"],
                    "beta": seed["beta"],
                    "pulls": seed["pulls"]
                }
            else:
                self.contexts[ctx_key][arm] = {"alpha": 1, "beta": 1, "pulls": 0}

    def _get_arm_data(self, ctx_key: str, arm: str) -> dict:
        """Get arm data: prefer specific context, fallback to genel, then flatten all."""
        # 1) Check specific context
        if ctx_key in self.contexts and arm in self.contexts[ctx_key]:
            return self.contexts[ctx_key][arm]
        
        # 2) Fallback: aggregate from all contexts (flat Thompson Sampling)
        agg = {"alpha": 0, "beta": 0, "pulls": 0}
        found = False
        for ck, arms in self.contexts.items():
            if arm in arms:
                agg["alpha"] += arms[arm]["alpha"] - 1  # remove prior
                agg["beta"] += arms[arm]["beta"] - 1
                agg["pulls"] += arms[arm]["pulls"]
                found = True
        
        if found:
            agg["alpha"] = max(1, agg["alpha"] + 1)
            agg["beta"] = max(1, agg["beta"] + 1)
            # Cache in this context for next time
            self._ensure_arm(ctx_key, arm)
            self.contexts[ctx_key][arm] = dict(agg)
            return self.contexts[ctx_key][arm]
        
        # 3) Fresh arm
        self._ensure_arm(ctx_key, arm)
        return self.contexts[ctx_key][arm]

    def select_arm(self, available_arms: list, context: dict) -> str:
        if not available_arms:
            return None

        ctx_key = self._get_context_key(context)

        samples = {}
        for arm in available_arms:
            data = self._get_arm_data(ctx_key, arm)
            a = data["alpha"]
            b = data["beta"]
            pulls = data["pulls"]

            try:
                samples[arm] = random.betavariate(a, b)
            except ValueError:
                samples[arm] = random.random()

            if pulls == 0 and a <= 1 and b <= 1:
                samples[arm] *= 0.8  # Cold-start penalty

        best_arm = max(samples, key=samples.get)
        return best_arm

    def update(self, arm: str, reward: float, context: dict):
        """Update with multi-component reward."""
        ctx_key = self._get_context_key(context)
        self._ensure_arm(ctx_key, arm)

        self.total_pulls += 1
        self.results["total"] += 1

        if reward > 0:
            self.contexts[ctx_key][arm]["alpha"] += reward
            self.results["correct"] += 1
        elif reward < 0:
            self.contexts[ctx_key][arm]["beta"] += abs(reward)
            self.results["incorrect"] += 1
        else:
            self.contexts[ctx_key][arm]["alpha"] += 0.3
            self.contexts[ctx_key][arm]["beta"] += 0.3

        self.contexts[ctx_key][arm]["pulls"] += 1

    def get_confidence(self, arm: str, context: dict) -> float:
        ctx_key = self._get_context_key(context)
        if ctx_key not in self.contexts or arm not in self.contexts[ctx_key]:
            return 0.5
        a = self.contexts[ctx_key][arm]["alpha"]
        b = self.contexts[ctx_key][arm]["beta"]
        return a / (a + b)

    def get_stats(self) -> dict:
        """Aggregate stats across all contexts."""
        arm_agg = {}
        total_pulls = 0
        for ctx_key, arms in self.contexts.items():
            for arm, data in arms.items():
                if arm not in arm_agg:
                    arm_agg[arm] = {"alpha": 0, "beta": 0, "pulls": 0}
                arm_agg[arm]["alpha"] += data["alpha"]
                arm_agg[arm]["beta"] += data["beta"]
                arm_agg[arm]["pulls"] += data["pulls"]
                total_pulls += data["pulls"]

        arms_out = {}
        for arm, data in arm_agg.items():
            a = data["alpha"]
            b = data["beta"]
            arms_out[arm] = {
                "alpha": round(a, 2),
                "beta": round(b, 2),
                "confidence": round(a / (a + b), 3),
                "pulls": data["pulls"]
            }

        return {
            "total_arms": len(arms_out),
            "total_pulls": total_pulls,
            "total_contexts": len(self.contexts),
            "accuracy": round(self.results["correct"] / max(self.results["total"], 1), 3),
            "results": self.results,
            "arms": arms_out
        }


class SlidingWindowDecay:
    """
    Exponential decay for old log entries.
    Older observations get weighted less.
    """

    def __init__(self, half_life_days: int = 30, max_entries: int = 1000):
        self.half_life_days = half_life_days
        self.max_entries = max_entries

    def compute_weight(self, timestamp_str: str) -> float:
        """Compute weight for an entry based on age."""
        try:
            ts = datetime.fromisoformat(timestamp_str)
            age_days = (datetime.now() - ts).days
            return 2 ** (-age_days / self.half_life_days)
        except (ValueError, TypeError):
            return 1.0

    def prune_log(self, log_path: Path):
        """Remove oldest entries beyond max_entries, and weigh rewards."""
        if not log_path.exists():
            return 0

        lines = log_path.read_text(encoding="utf-8").strip().splitlines()
        if len(lines) <= self.max_entries:
            return 0  # No pruning needed

        # Keep only the most recent max_entries
        keep = lines[-self.max_entries:]
        log_path.write_text("\n".join(keep) + "\n", encoding="utf-8")
        return len(lines) - self.max_entries  # removed count


def compute_multicomponent_reward(
    task_complete: bool = False,
    user_corrections: int = 0,
    quality_score: float = 0.5,
    cost_factor: float = 1.0
) -> float:
    """
    Multi-component reward calculation:
    reward = α * complete + β * (1 / (corrections + 1)) + γ * quality - δ * cost
    """
    alpha = 0.5  # completion weight
    beta = 0.3   # correction penalty weight
    gamma = 0.15  # quality weight
    delta = 0.05  # cost weight

    reward = (
        alpha * (1.0 if task_complete else 0.0) +
        beta * (1.0 / (user_corrections + 1)) +
        gamma * quality_score -
        delta * cost_factor
    )
    return max(-1.0, min(1.0, reward))


def auto_adjust_threshold(mab_stats: dict, current_threshold: float) -> float:
    """
    Auto-adjust rule confidence threshold based on MAB performance.
    If MAB accuracy > 70%, lower threshold (trust MAB more).
    If MAB accuracy < 30%, raise threshold (trust rules more).
    """
    accuracy = mab_stats.get("accuracy", 0.5)
    total = mab_stats.get("results", {}).get("total", 0)

    if total < 20:
        return current_threshold  # Not enough data yet

    if accuracy > 0.70 and current_threshold > 0.60:
        return round(current_threshold - 0.05, 2)
    elif accuracy < 0.30 and current_threshold < 0.95:
        return round(current_threshold + 0.05, 2)

    return current_threshold


def rotate_log_if_needed(log_path: Path, max_size_mb: int = 5):
    """Rotate log file if it exceeds max_size_mb."""
    if not log_path.exists():
        return None

    size_mb = log_path.stat().st_size / (1024 * 1024)
    if size_mb < max_size_mb:
        return None

    # Rename with timestamp
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    rotated = log_path.with_name(f"skill_log_{ts}.jsonl")
    log_path.rename(rotated)
    logger.log_skill_decision("system: log rotated", "system", category="sistem")
    return str(rotated)


# ---- Backward compat: old ThompsonSamplingMAB uses new engine ----
class ThompsonSamplingMAB:
    """Thin wrapper for backward compatibility."""

    def __init__(self, seed_data: dict = None):
        self._engine = ContextualMAB()
        self.alpha = {}
        self.beta = {}
        self.total_pulls = {}
        self.results = {"correct": 0, "incorrect": 0, "total": 0}

    def select_arm(self, available_arms: list) -> str:
        # Flat mode: use generic context
        ctx = {"length_bucket": "medium", "category": "genel"}
        return self._engine.select_arm(available_arms, ctx)

    def update(self, arm: str, reward: int):
        ctx = {"length_bucket": "medium", "category": "genel"}
        self._engine.update(arm, float(reward), ctx)
        self.results["total"] += 1
        if reward > 0:
            self.results["correct"] += 1
            self.alpha[arm] = self.alpha.get(arm, 1) + reward
        elif reward < 0:
            self.results["incorrect"] += 1
            self.beta[arm] = self.beta.get(arm, 1) + 1
        self.total_pulls[arm] = self.total_pulls.get(arm, 0) + 1

    def get_stats(self):
        return self._engine.get_stats()

    def from_logger(self):
        data = logger.export_mab_data()
        for skill, d in data.items():
            self.alpha[skill] = d.get("alpha", 1)
            self.beta[skill] = d.get("beta", 1)
            self.total_pulls[skill] = d.get("total", 0)


class EpsilonGreedyMAB:
    """Unchanged — kept as simple alternative."""
    def __init__(self, epsilon: float = 0.1):
        self.epsilon = epsilon
        self.successes = {}
        self.failures = {}
        self.total_pulls = {}

    def select_arm(self, available_arms: list) -> str:
        if not available_arms:
            return None
        if random.random() < self.epsilon:
            return random.choice(available_arms)
        best_score = -1
        best_arm = available_arms[0]
        for arm in available_arms:
            s = self.successes.get(arm, 0)
            f = self.failures.get(arm, 0)
            total = s + f
            score = s / max(total, 1)
            if total == 0:
                score = 0.5
            if score > best_score:
                best_score = score
                best_arm = arm
        return best_arm

    def update(self, arm: str, reward: int):
        if arm not in self.successes:
            self.successes[arm] = 0
            self.failures[arm] = 0
            self.total_pulls[arm] = 0
        self.total_pulls[arm] += 1
        if reward > 0:
            self.successes[arm] += reward
        elif reward < 0:
            self.failures[arm] += abs(reward)
        else:
            self.successes[arm] += 0.5
            self.failures[arm] += 0.5

    def get_stats(self) -> dict:
        arms = {}
        for arm in set(list(self.successes.keys()) + list(self.failures.keys())):
            s = self.successes.get(arm, 0)
            f = self.failures.get(arm, 0)
            arms[arm] = {
                "successes": s, "failures": f,
                "rate": round(s / max(s + f, 1), 3),
                "pulls": self.total_pulls.get(arm, 0)
            }
        return {"algorithm": "epsilon-greedy", "epsilon": self.epsilon, "arms": arms}


def choose_mab_algorithm(total_log_entries: int) -> str:
    if total_log_entries < 50:
        return "epsilon-greedy"
    return "thompson"


if __name__ == "__main__":
    print("=== MAB Engine v2.0 — Contextual + Sliding Window + Multi-Reward ===\n")

    # Test Contextual MAB
    print("-- Contextual Bandit Test --")
    cmab = ContextualMAB()

    queries = [
        ("python script yaz", {"length_bucket": "short", "category": "kod"}),
        ("tor ile ara", {"length_bucket": "short", "category": "arama"}),
        ("bu uzun bir analiz sorgusu ve karmasik", {"length_bucket": "long", "category": "analiz"}),
    ]

    for q, ctx in queries:
        chosen = cmab.select_arm(["kod", "arama", "analiz"], ctx)
        reward = compute_multicomponent_reward(task_complete=True, quality_score=0.8)
        cmab.update(chosen, reward, ctx)
        print(f"  ctx={ctx} → {chosen} reward={reward:.2f}")

    stats = cmab.get_stats()
    print(f"\nContextual MAB stats: {stats['total_contexts']} contexts, {stats['total_arms']} arms")

    # Test Sliding Window
    print("\n-- Sliding Window Decay Test --")
    decay = SlidingWindowDecay(half_life_days=30)
    weight_old = decay.compute_weight("2025-01-01T00:00:00")
    weight_new = decay.compute_weight(datetime.now().isoformat())
    print(f"  1 year old entry weight: {weight_old:.4f}")
    print(f"  Today entry weight:      {weight_new:.4f}")

    # Test auto threshold
    print("\n-- Auto Threshold Test --")
    thresholds = [(0.85, 0.8), (0.30, 0.8), (0.75, 0.8)]
    for acc, current in thresholds:
        new = auto_adjust_threshold(
            {"accuracy": acc, "results": {"total": 50}}, current
        )
        print(f"  accuracy={acc:.2f} → threshold {current} → {new}")

    # Test multi-component reward
    print("\n-- Multi-Component Reward Test --")
    scenarios = [
        dict(task_complete=True, user_corrections=0, quality_score=0.9),
        dict(task_complete=False, user_corrections=2, quality_score=0.3),
        dict(task_complete=True, user_corrections=1, quality_score=0.7),
    ]
    for s in scenarios:
        r = compute_multicomponent_reward(**s)
        print(f"  {s} → reward={r:.2f}")

    print("\nAll systems ready.")
