#!/usr/bin/env python3
"""
RL Integration Bridge — ReYMeN canlı akışına RL bağlantısı.
nexus-core adım 9.5'in aktif uygulaması.
Kullanım: python rl_integration.py --query "<sorgu>" --skill "<skill>" [--reward 0] [--category auto]
"""

import sys
import json
import argparse
from pathlib import Path

RL_DIR = Path(__file__).parent
sys.path.insert(0, str(RL_DIR))

from rl_skill_logger import log_skill_decision, update_reward, classify_query, get_stats, export_mab_data


def parse_args():
    parser = argparse.ArgumentParser(description="ReYMeN RL Integration Bridge")
    parser.add_argument("--query", default="", help="User query text")
    parser.add_argument("--skill", default="none", help="Selected skill name")
    parser.add_argument("--reward", type=int, default=0, help="Reward value (-1, 0, +1)")
    parser.add_argument("--category", default=None, help="Query category (auto if omitted)")
    parser.add_argument("--mode", default="default", help="Active ReYMeN mode")
    parser.add_argument("--rule-based", dest="rule_based", action="store_true", default=True)
    parser.add_argument("--mab", dest="rule_based", action="store_false")
    parser.add_argument("--update-reward", metavar="LOG_ID", help="Update reward for a log entry")
    parser.add_argument("--new-reward", type=int, default=None, help="New reward value (with --update-reward)")
    parser.add_argument("--action", choices=["log", "stats", "mab-data", "auto-reward"], default="log",
                        help="Action to perform")
    parser.add_argument("--user-reply", default=None, help="User reply for auto_reward detection")

    return parser.parse_args()


def main():
    args = parse_args()

    if args.action == "stats":
        stats = get_stats()
        print(json.dumps(stats, ensure_ascii=False, indent=2))
        return

    if args.action == "mab-data":
        data = export_mab_data()
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return

    if args.action == "auto-reward" and args.user_reply:
        from rl_skill_logger import auto_reward
        reward = auto_reward(args.user_reply)
        print(json.dumps({"reward": reward, "message": args.user_reply}, ensure_ascii=False))
        return

    if args.update_reward and args.new_reward is not None:
        success = update_reward(args.update_reward, args.new_reward)
        print(json.dumps({"updated": success, "log_id": args.update_reward, "new_reward": args.new_reward}))
        return

    # Default: log a skill decision
    category = args.category or classify_query(args.query)
    log_id = log_skill_decision(
        query=args.query,
        selected_skills=args.skill,
        rule_based=args.rule_based,
        reward=args.reward,
        category=category,
        mode=args.mode,
        user_reply=args.user_reply
    )

    result = {
        "log_id": log_id,
        "skill": args.skill,
        "category": category,
        "rule_based": args.rule_based,
        "reward": args.reward
    }
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
