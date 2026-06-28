#!/usr/bin/env python3
"""
ReYMeN Benchmark v1 — Cross-Model Test Pipeline
Usage: python benchmark_v1.py
"""

import json, time, os, requests
from datetime import datetime
import logging
logger = logging.getLogger(__name__)

TEST_SET_PATH = r"references/test_set.json"
RESULTS_DIR = r"."

def get_env():
    env_path = os.path.expanduser("~/AppData/Local/ReYMeN/.env")
    env = {}
    try:
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if "=" in line and not line.startswith("#"):
                    k, v = line.split("=", 1)
                    env[k.strip()] = v.strip()
    except: pass
    return env

env = get_env()

# ─── MODELLER — Güncellemek için burayı düzenle ───
MODELS = [
    {
        "name": "DeepSeek v4 Flash",
        "api_url": "https://api.deepseek.com/v1/chat/completions",
        "api_key": env.get("DEEPSEEK_API_KEY", ""),
        "model": "deepseek-chat"
    },
    {
        "name": "Groq Llama 3.3 70B",
        "api_url": "https://api.groq.com/openai/v1/chat/completions",
        "api_key": env.get("GROQ_API_KEY", ""),
        "model": "llama-3.3-70b-versatile"
    },
    {
        "name": "Groq Llama 4 Scout",
        "api_url": "https://api.groq.com/openai/v1/chat/completions",
        "api_key": env.get("GROQ_API_KEY", ""),
        "model": "meta-llama/llama-4-scout-17b-16e-instruct"
    },
]

def score_answer(answer, keywords):
    answer_lower = answer.lower()
    found = sum(1 for kw in keywords if kw.lower() in answer_lower)
    return int((found / len(keywords)) * 100) if keywords else 50

def query_model(cfg, prompt):
    headers = {"Authorization": f"Bearer {cfg['api_key']}", "Content-Type": "application/json"}
    payload = {"model": cfg["model"], "messages": [{"role": "user", "content": prompt}],
               "max_tokens": 512, "temperature": 0.1}
    t0 = time.time()
    try:
        resp = requests.post(cfg["api_url"], headers=headers, json=payload, timeout=30)
        elapsed = time.time() - t0
        if resp.status_code != 200:
            return {"error": f"HTTP {resp.status_code}", "latency_ms": round(elapsed*1000), "answer": "", "tokens_out": 0}
        data = resp.json()
        answer = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        usage = data.get("usage", {})
        return {"answer": answer, "latency_ms": round(elapsed*1000), "tokens_out": usage.get("completion_tokens", 0), "tokens_in": usage.get("prompt_tokens", 0), "error": None}
    except Exception as e:
        return {"error": str(e), "latency_ms": round((time.time()-t0)*1000), "answer": "", "tokens_out": 0}

def test_model(cfg, test_set, runs=2):
    results = []
    total_score = total_lat = total_tok = errors = 0
    for q in test_set:
        scores, lats = [], []
        for _ in range(runs):
            r = query_model(cfg, q["prompt"])
            if r["error"]:
                errors += 1; continue
            scores.append(score_answer(r["answer"], q["score_keywords"]))
            lats.append(r["latency_ms"])
            total_tok += r.get("tokens_out", 0)
        if scores:
            results.append({"id": q["id"], "category": q["category"],
                "avg_score": round(sum(scores)/len(scores), 1),
                "avg_latency_ms": round(sum(lats)/len(lats), 0)})
            total_score += sum(scores)/len(scores)
            total_lat += sum(lats)/len(lats)
    n = len(test_set)
    return {"model": cfg["name"], "ortalama_puan": round(total_score/n, 1) if n else 0,
            "ortalama_latency_ms": round(total_lat/n, 0) if n else 0,
            "toplam_token": total_tok, "hata_sayisi": errors, "detay": results}

def main():
    with open(TEST_SET_PATH, encoding="utf-8") as f:
        test_set = json.load(f)["test_set"]
    print(f"📋 {len(test_set)} soru, {len(MODELS)} model")

    all_results = []
    for m in MODELS:
        if not m["api_key"]:
            print(f"⚠️ {m['name']}: anahtar yok"); continue
        print(f"🔄 {m['name']}...", end=" ", flush=True)
        t0 = time.time()
        r = test_model(m, test_set)
        print(f"⏱ {round(time.time()-t0, 1)}sn | %{r['ortalama_puan']} | {r['ortalama_latency_ms']}ms | {r['hata_sayisi']} hata")
        all_results.append(r)
        time.sleep(1)

    sorted_r = sorted(all_results, key=lambda r: r["ortalama_puan"], reverse=True)
    report = f"# ReYMeN BENCHMARK RAPORU\n**{datetime.now():%Y-%m-%d %H:%M}**\n\n## ÖZET\n| # | Model | Doğruluk | Hız | Hata |\n|---|-------|----------|-----|------|\n"
    for i, r in enumerate(sorted_r, 1):
        report += f"| {i} | **{r['model']}** | %{r['ortalama_puan']} | {r['ortalama_latency_ms']}ms | {r['hata_sayisi']} |\n"

    if sorted_r:
        best = sorted_r[0]
        fastest = min(sorted_r, key=lambda r: r["ortalama_latency_ms"])
        report += f"\n## ÖNERİ\n- En doğru: {best['model']} (%{best['ortalama_puan']})\n- En hızlı: {fastest['model']} ({fastest['ortalama_latency_ms']}ms)\n"

    with open("benchmark_raporu.md", "w", encoding="utf-8") as f:
        f.write(report)
    print(f"\n✅ benchmark_raporu.md kaydedildi")

if __name__ == "__main__":
    main()
