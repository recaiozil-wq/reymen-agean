#!/usr/bin/env python3
"""
ReYMeN Terminal-Bench HARD Task Runner
57 hard görevi batch halinde çalıştırır.
"""
import os, subprocess, json, sys, time, re

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "terminal-bench-benchmark", "original-tasks")
RESULTS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".ReYMeN", "reports", "tbench-hard-results.json")
REPORT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".ReYMeN", "reports", "tbench-hard-report.md")

# Tüm 57 hard task
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

def get_base_image(task_dir):
    """Dockerfile'dan base image'i al."""
    try:
        with open(os.path.join(BASE, task_dir, "Dockerfile")) as f:
            for line in f:
                if line.startswith("FROM"):
                    # platform flag'lerini temizle
                    img = line.replace("FROM", "").strip()
                    img = re.sub(r'--platform=[\w/-]+', '', img).strip()
                    return img
    except: pass
    return "TEMPLATE_ONLY"

def run_cmd(cmd, timeout=120):
    """Komut çalıştır, timeout ile."""
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return r.returncode, r.stdout, r.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "TIMEOUT"
    except Exception as e:
        return -1, "", str(e)

def test_task(task_dir):
    """Hard task'ı test et."""
    task_path = os.path.join(BASE, task_dir)
    yaml_file = os.path.join(task_path, "task.yaml")
    
    if not os.path.isfile(yaml_file):
        return {"task": task_dir, "status": "NO_YAML", "error": ""}
    
    # Difficulty oku
    diff = ""
    cat = ""
    instr = ""
    with open(yaml_file) as f:
        for line in f:
            if line.startswith("difficulty:"):
                diff = line.split(":", 1)[1].strip()
            elif line.startswith("category:"):
                cat = line.split(":", 1)[1].strip()
            elif line.startswith("instruction:"):
                instr = line.split(":", 1)[1].strip()[:100]
    
    # Base image
    base_img = get_base_image(task_dir)
    
    # solution.sh var mı?
    sol_sh = os.path.join(task_path, "solution.sh")
    sol_py = os.path.join(task_path, "solution.py")
    has_solution = os.path.isfile(sol_sh) or os.path.isfile(sol_py)
    
    # Test dizini var mı?
    has_tests = os.path.isdir(os.path.join(task_path, "tests"))
    
    # Dockerfile var ve gerçek bir FROM içeriyor mu?
    dockerfile_path = os.path.join(task_path, "Dockerfile")
    has_real_dockerfile = False
    if os.path.isfile(dockerfile_path):
        with open(dockerfile_path) as f:
            content = f.read()
            has_real_dockerfile = "FROM" in content and not all(
                l.strip().startswith("#") for l in content.splitlines() if l.strip()
            )
    
    # Tahmin et: çözülebilir mi?
    # Kriterler: Python tabanlı ve torchi yok
    needs_torch = "torch" in base_img.lower() or any(
        kw in task_dir.lower() for kw in ["torch", "cartpole", "hf-train", "lora", "leelachess"]
    )
    needs_specialized = any(
        kw in task_dir.lower() for kw in [
            "zork", "windows-3.11", "windows-xp", "lean4", "doom-for-mips",
            "mips-interpreter", "pdp11", "ocaml", "rust-c", "dna-assembly",
            "protein-assembly", "sam-cell", "sparql", "causal-inference-r",
            "mcmc-sampling-stan", "feal-", "magsac"
        ]
    )
    
    expected_feasible = not needs_torch and not needs_specialized
    
    return {
        "task": task_dir,
        "difficulty": diff or "hard",
        "category": cat or "unknown",
        "instruction_preview": instr,
        "has_solution": has_solution,
        "has_tests": has_tests,
        "has_real_dockerfile": has_real_dockerfile,
        "base_image": base_img,
        "needs_torch": needs_torch,
        "needs_specialized": needs_specialized,
        "expected_feasible": expected_feasible
    }

def run_solution_in_docker(task_dir, base_img, timeout=300):
    """solution.sh'i Docker'da çalıştırmayı dene."""
    task_path = os.path.join(BASE, task_dir)
    sol_sh = os.path.join(task_path, "solution.sh")
    
    if not os.path.isfile(sol_sh):
        return {"status": "NO_SOLUTION", "error": ""}
    
    # Dockerfile build
    docker_tag = f"tbench-hard-{task_dir}"
    
    # Build image
    rc, out, err = run_cmd(
        f'docker build -t {docker_tag} "{task_path}" 2>&1', timeout=120
    )
    if rc != 0:
        return {"status": "BUILD_FAILED", "error": err[:300]}
    
    # Run solution
    rc, out, err = run_cmd(
        f'docker run --rm {docker_tag} bash /app/solution.sh 2>&1', timeout=timeout
    )
    if rc == 0:
        return {"status": "SOLUTION_PASSED", "output": out[:200]}
    else:
        return {"status": "SOLUTION_FAILED", "error": err[:300]}

def main():
    os.makedirs(os.path.dirname(RESULTS_FILE), exist_ok=True)
    
    print("=" * 60)
    print("🧠  ReYMeN HARD Task Analyzer")
    print("=" * 60)
    print(f"  Toplam: {len(HARD_TASKS)} hard görev")
    print()
    
    # Phase 1: Analyze all tasks
    print("📋  Phase 1: Task Analysis")
    print("-" * 40)
    
    analyses = []
    feasible = []
    not_feasible = []
    
    for i, task in enumerate(HARD_TASKS):
        a = test_task(task)
        analyses.append(a)
        status = "✅" if a["expected_feasible"] else "❌"
        reason = ""
        if a["needs_torch"]:
            reason = " (torch gerekli)"
        elif a["needs_specialized"]:
            reason = " (specialized env)"
        elif not a["has_real_dockerfile"]:
            reason = " (template Dockerfile)"
        print(f"  [{i+1:2d}/{len(HARD_TASKS)}] {status} {task:40s}{reason}")
        
        if a["expected_feasible"] and a["has_real_dockerfile"]:
            feasible.append(task)
        else:
            not_feasible.append(task)
    
    print(f"\n  Feasible: {len(feasible)} | Not feasible: {len(not_feasible)}")
    
    # Phase 2: Run feasible tasks
    if feasible:
        print(f"\n🚀  Phase 2: Running {len(feasible)} feasible hard tasks")
        print("-" * 40)
        
        results = []
        for i, task in enumerate(feasible):
            print(f"  [{i+1}/{len(feasible)}] {task:40s} ", end="", flush=True)
            a = next(a for a in analyses if a["task"] == task)
            result = run_solution_in_docker(task, a["base_image"])
            results.append(result)
            
            status_icon = "✅" if result["status"] == "SOLUTION_PASSED" else "❌"
            print(f"{status_icon} {result['status']}")
        
        # Save results
        output = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_hard": len(HARD_TASKS),
            "feasible": len(feasible),
            "not_feasible": len(not_feasible),
            "analyses": analyses,
            "results": results
        }
        with open(RESULTS_FILE, "w") as f:
            json.dump(output, f, indent=2)
        
        print(f"\n📄  Results saved: {RESULTS_FILE}")
    
    # Summary
    print(f"\n📊  SUMMARY")
    print("=" * 60)
    print(f"  Total hard tasks: {len(HARD_TASKS)}")
    
    by_cat = {}
    for a in analyses:
        cat = a["category"] or "unknown"
        by_cat.setdefault(cat, {"total": 0, "feasible": 0})
        by_cat[cat]["total"] += 1
        if a["expected_feasible"]:
            by_cat[cat]["feasible"] += 1
    
    print(f"\n  Category breakdown:")
    for cat, counts in sorted(by_cat.items()):
        print(f"    {cat:25s}: {counts['total']:2d} tasks, {counts['feasible']:2d} feasible")
    
    print(f"\n  Feasible tasks ({len(feasible)}):")
    for t in feasible:
        print(f"    ✅ {t}")
    
    print(f"\n  Not feasible ({len(not_feasible)}):")
    for t in not_feasible:
        a = next(a for a in analyses if a["task"] == t)
        reason = ""
        if a["needs_torch"]:
            reason = "torch"
        elif a["needs_specialized"]:
            reason = "specialized"
        else:
            reason = "template or other"
        print(f"    ❌ {t:45s} ({reason})")

if __name__ == "__main__":
    main()
