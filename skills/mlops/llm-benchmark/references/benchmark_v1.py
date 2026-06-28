#!/usr/bin/env python3
"""
ReYMeN Benchmark v1 — Scaling Laws Test
Ölçer: Hız, Doğruluk, Tutarlılık, Maliyet
Detay: skill_view(name='llm-benchmark')
"""

import json, time, os, requests
from datetime import datetime
import logging
logger = logging.getLogger(__name__)

TEST_SET_PATH = r"C:\Users\marko\Desktop\benchmark\test_set.json"
RESULTS_DIR = r"C:\Users\marko\Desktop\benchmark"

# .env'den API anahtarları
def get_env():
    env_path = r"C:\Users\marko\AppData\Local\ReYMeN\.env"
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
DEEPSEEK_KEY = env.get("DEEPSEEK_API_KEY", "")
GROQ_KEY = env.get("GROQ_API_KEY", "")

# ─── MODELLER — yeni model eklemek için buraya ekle ───
MODELS = [
    {"name":"DeepSeek v4 Flash","provider":"deepseek","api_url":"https://api.deepseek.com/v1/chat/completions","api_key":DEEPSEEK_KEY,"model":"deepseek-chat","priority":1},
    {"name":"Groq Llama 3.3 70B","provider":"groq","api_url":"https://api.groq.com/openai/v1/chat/completions","api_key":GROQ_KEY,"model":"llama-3.3-70b-versatile","priority":2},
    {"name":"Groq Llama 4 Scout","provider":"groq","api_url":"https://api.groq.com/openai/v1/chat/completions","api_key":GROQ_KEY,"model":"meta-llama/llama-4-scout-17b-16e-instruct","priority":3},
    {"name":"Groq Llama 3.1 8B","provider":"groq","api_url":"https://api.groq.com/openai/v1/chat/completions","api_key":GROQ_KEY,"model":"llama-3.1-8b-instant","priority":4},
    {"name":"Groq Qwen3 32B","provider":"groq","api_url":"https://api.groq.com/openai/v1/chat/completions","api_key":GROQ_KEY,"model":"qwen/qwen3-32b","priority":5},
]

def score_answer(answer, keywords):
    answer_lower = answer.lower()
    found = sum(1 for kw in keywords if kw.lower() in answer_lower)
    return int((found / len(keywords)) * 100) if keywords else 50

def query_model(model_cfg, prompt):
    headers = {"Authorization": f"Bearer {model_cfg['api_key']}", "Content-Type": "application/json"}
    payload = {"model": model_cfg["model"], "messages":[{"role":"user","content":prompt}], "max_tokens":512, "temperature":0.1}
    t0 = time.time()
    try:
        resp = requests.post(model_cfg["api_url"], headers=headers, json=payload, timeout=30)
        elapsed = time.time() - t0
        if resp.status_code != 200:
            return {"error":f"HTTP {resp.status_code}","latency_ms":round(elapsed*1000),"answer":"","tokens_out":0}
        data = resp.json()
        answer = data.get("choices",[{}])[0].get("message",{}).get("content","")
        usage = data.get("usage",{})
        return {"answer":answer,"latency_ms":round(elapsed*1000),"tokens_out":usage.get("completion_tokens",0),"tokens_in":usage.get("prompt_tokens",0),"error":None}
    except Exception as e:
        return {"error":str(e),"latency_ms":round((time.time()-t0)*1000),"answer":"","tokens_out":0}

def test_model(model_cfg, test_set, runs=2):
    results = []; total_lat=total_tok=total_score=errors=0
    for q in test_set:
        scores, lats = [], []
        for _ in range(runs):
            r = query_model(model_cfg, q["prompt"])
            if r["error"]: errors+=1; continue
            scores.append(score_answer(r["answer"], q["score_keywords"]))
            lats.append(r["latency_ms"])
            total_tok += r.get("tokens_out",0)
        avg_s = sum(scores)/len(scores) if scores else 0
        avg_l = sum(lats)/len(lats) if lats else 0
        cons = 100-abs(scores[0]-scores[-1]) if len(scores)>1 else 100
        results.append({"id":q["id"],"category":q["category"],"avg_score":round(avg_s,1),"avg_latency_ms":round(avg_l,0),"consistency":round(cons,0)})
        total_score += avg_s; total_lat += avg_l
    n=len(test_set)
    return {"model":model_cfg["name"],"sorular":n,"ortalama_puan":round(total_score/n,1) if n else 0,"ortalama_latency_ms":round(total_lat/n,0) if n else 0,"toplam_token":total_tok,"hata_sayisi":errors,"detay":results}

def generate_report(all_results):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    sr = sorted(all_results, key=lambda r: r["ortalama_puan"], reverse=True)
    lines = [f"# ReYMeN BENCHMARK RAPORU\n**Tarih:** {now}\n**Test Seti:** {sr[0]['sorular']} soru (kod/mantık/güvenlik/bilgi)\n**Her soru:** 2 tekrar\n",
             "## ÖZET SIRALAMA\n| Sıra | Model | Doğruluk | Hız (ms) | Token | Hata |\n|------|-------|----------|----------|-------|------|"]
    for i,r in enumerate(sr,1): lines.append(f"| {i} | **{r['model']}** | %{r['ortalama_puan']} | {r['ortalama_latency_ms']} | {r['toplam_token']} | {r['hata_sayisi']} |")
    lines.append("\n## KATEGORİ BAZINDA\n")
    cats = {"kod":"Kod","mantik":"Mantık","guvenlik":"Güvenlik","bilgi":"Bilgi"}
    for r in sr:
        lines.append(f"\n### {r['model']}\n| Kategori | Puan | Hız |\n|----------|------|-----|")
        for ck,cn in cats.items():
            cr = [d for d in r["detay"] if d["category"]==ck]
            if cr:
                cs = sum(d["avg_score"] for d in cr)/len(cr)
                cl = sum(d["avg_latency_ms"] for d in cr)/len(cr)
                lines.append(f"| {cn} | %{round(cs,1)} | {round(cl,0)} ms |")
    if sr:
        fast = min(sr, key=lambda r: r["ortalama_latency_ms"])
        lines.append(f"\n## ÖNERİLER\n- **En doğru:** {sr[0]['model']} (%{sr[0]['ortalama_puan']})\n- **En hızlı:** {fast['model']} ({fast['ortalama_latency_ms']} ms)\n- **Kod:** {sr[0]['model']}")
    lines.append(f"\n---\n_ReYMeN Benchmark v1 • {now}_")
    return "\n".join(lines)

def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)
    with open(TEST_SET_PATH, encoding="utf-8") as f: test_set = json.load(f)["test_set"]
    print(f"📋 {len(test_set)} soru, {len(MODELS)} model\n"); all_res=[]
    for m in MODELS:
        if not m["api_key"]: print(f"⚠️ {m['name']}: API anahtarı yok"); continue
        t0=time.time(); r=test_model(m,test_set); t=time.time()-t0
        print(f"{m['name']}: %{r['ortalama_puan']} | {r['ortalama_latency_ms']}ms | {r['hata_sayisi']} hata | ⏱{round(t,1)}sn")
        all_res.append(r); time.sleep(1)
    report = generate_report(all_res)
    rp = os.path.join(RESULTS_DIR,"benchmark_raporu.md")
    with open(rp,"w",encoding="utf-8") as f: f.write(report)
    print(f"\n✅ {rp}\n\n{report}")

if __name__ == "__main__": main()
