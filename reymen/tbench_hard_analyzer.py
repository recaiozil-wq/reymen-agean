#!/usr/bin/env python3
"""ReYMeN HARD Task - Sadece Analiz (build yok)"""
import os, json, time, re

BASE = r"C:\Users\marko\Desktop\Reymen Proje\ReYMeN-Ajan\terminal-bench-benchmark\original-tasks"

HARD_TASKS = [
    "3d-model-format-legacy", "bn-fit-modify", "cancel-async-tasks",
    "cartpole-rl-training", "causal-inference-r", "chem-property-targeting",
    "chem-rf", "circuit-fibsqrt", "configure-git-webserver",
    "dna-assembly", "extract-moves-from-video",
    "feal-differential-cryptanalysis", "feal-linear-cryptanalysis",
    "find-official-code", "fix-code-vulnerability", "fix-ocaml-gc",
    "gpt2-codegolf", "hf-train-lora-adapter",
    "install-windows-3.11", "install-windows-xp",
    "lean4-proof", "leelachess0-pytorch-conversion",
    "llm-inference-batching-scheduler", "magsac-install",
    "make-doom-for-mips", "make-mips-interpreter", "mcmc-sampling-stan",
    "model-extraction-relu-logits", "movie-helper",
    "neuron-to-jaxley-conversion", "organization-json-generator",
    "parallelize-graph", "parallel-particle-simulator",
    "password-recovery", "path-tracing", "path-tracing-reverse",
    "play-zork", "play-zork-easy",
    "polyglot-rust-c", "port-compressor", "protein-assembly",
    "rare-mineral-allocation", "regex-chess", "reverse-engineering",
    "run-pdp11-code", "sam-cell-seg",
    "sparql-university", "stable-parallel-kmeans",
    "swe-bench-astropy-1", "swe-bench-astropy-2",
    "torch-pipeline-parallelism", "torch-tensor-parallelism",
    "train-fasttext", "video-processing", "vul-flink",
    "word2vec-from-scratch", "write-compressor"
]

results = []
for task in HARD_TASKS:
    task_path = os.path.join(BASE, task)
    yaml_file = os.path.join(task_path, "task.yaml")
    
    diff = cat = instr = ""
    if os.path.isfile(yaml_file):
        with open(yaml_file) as f:
            for line in f:
                if line.startswith("difficulty:"): diff = line.split(":",1)[1].strip()
                elif line.startswith("category:"): cat = line.split(":",1)[1].strip()
                elif line.startswith("instruction:"): instr = line.split(":",1)[1].strip()[:80]
    
    # Dockerfile base
    base = "N/A"
    df = os.path.join(task_path, "Dockerfile")
    if os.path.isfile(df):
        with open(df) as f:
            for line in f:
                if line.startswith("FROM"):
                    base = re.sub(r'--platform=[\w/-]+', '', line).replace("FROM","").strip()
                    break
    
    # solution
    has_sh = os.path.isfile(os.path.join(task_path, "solution.sh"))
    has_py = os.path.isfile(os.path.join(task_path, "solution.py"))
    has_tests = os.path.isdir(os.path.join(task_path, "tests"))
    
    # Feasibility
    needs_torch = "torch" in base.lower() or any(kw in task.lower() for kw in ["torch","cartpole","hf-train","lora","leelachess"])
    needs_specialized = any(kw in task.lower() for kw in [
        "zork","windows-3.11","windows-xp","lean4","doom-for-mips",
        "mips-interpreter","pdp11","ocaml","rust-c","dna-assembly",
        "protein-assembly","sam-cell","sparql","causal-inference-r",
        "mcmc","feal-","magsac","3d-model","bn-fit","parallel-particle"
    ])
    is_template = "TEMPLATE" in base or "#" == base[:1] if len(base) > 0 else True
    
    feasible = (has_sh or has_py) and not needs_torch and not needs_specialized and not is_template
    
    results.append({
        "task": task, "cat": cat or "?", "base": base[:60],
        "has_sh": "✅" if has_sh else "❌",
        "has_tests": "✅" if has_tests else "❌",
        "torch": "⚠️" if needs_torch else "✅",
        "special": "⚠️" if needs_specialized else "✅",
        "feasible": "✅" if feasible else "❌",
    })

# Print table
print(f"\n{'='*80}")
print(f"  ReYMeN HARD Task Analysis - {len(HARD_TASKS)} tasks")
print(f"{'='*80}")
print(f"{'#':>3} {'Task':35s} {'Cat':20s} {'SH':2s} {'Tst':2s} {'Torch':5s} {'Spec':5s} {'Run?':3s}")
print(f"{'-'*80}")
feasible_list = []
for i, r in enumerate(results):
    flag = "✅" if r["feasible"] == "✅" else "❌"
    if flag == "✅":
        feasible_list.append(r["task"])
    print(f"{i+1:3d} {r['task']:35s} {r['cat']:20s} {r['has_sh']:2s} {r['has_tests']:2s} {r['torch']:5s} {r['special']:5s} {flag:3s}")

print(f"{'='*80}")
print(f"\n📊  Summary:")
print(f"  Total hard: {len(HARD_TASKS)}")
print(f"  Feasible (can attempt): {len(feasible_list)}")
print(f"  Not feasible: {len(HARD_TASKS)-len(feasible_list)}")
print(f"\n  Feasible tasks:")
for t in feasible_list:
    print(f"    ✅ {t}")
