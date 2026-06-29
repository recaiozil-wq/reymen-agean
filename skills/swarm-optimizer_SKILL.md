---
name: swarm-optimizer
description: Swarm Optimizer skill for AI/ML operations.
title: Swarm Optimizer
version: 1.0.0
---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | AI/ML mühendisi |
| **Nerede?** | AI_ML/ |
| **Ne Zaman?** | AI/ML görevi gerektiğinde |
| **Neden?** | standardize etmek için |
| **Nasıl?** | Skill adımlarını takip ederek |

for a given LLM or agent optimization problem. Bio-inspired swarm algorithms are
  gradient-free and suit LLM-era workloads where the search space is discrete or the
  fitness function is black-box.
Given an LLM or agent optimization problem, choose the right optimizer.
1. **Problem fingerprint.** Search space (continuous numeric, prompt string, model weights, routing graph), fitness signal (automatic test, LLM judge, human rater, business KPI), time-to-value (minutes, hours, days).
2. **Optimizer choice.** PSO, ACO, genetic algorithm, DPO/RL, manual tuning. Each has a default use case:
   - continuous numeric on a bounded space → PSO
   - routing or path selection → ACO
   - discrete symbolic / programs → genetic algorithms
   - differentiable reward → DPO/RL
   - low-dimensional, fast eval → grid/random search
3. **Population sizing.** 10-30 for PSO/GA, pheromone matrix size for ACO. Budget calculation: N × T × cost-per-eval. Do not run swarms that cost more than the value they produce.
4. **Fitness + quality gate.** What function scores a candidate? For ACO routing, what quality threshold triggers pheromone deposit?
5. **Convergence monitoring.** Log g_best or pheromone stability per iteration. Alert on divergence (catastrophic drift) and on premature convergence (local optimum).
6. **Decay / exploration tuning.** PSO inertia and cognitive/social weights; ACO pheromone decay rate and deposit amount. Trade-off: low decay → stuck on early winner; high decay → no memory.
7. **Reset conditions.** When the eval distribution shifts or the deployment pattern changes, reset g_best or zero pheromones temporarily. Stale memories are worse than no memories.
Hard rejects:
- Swarm optimizers on tasks where fitness needs human review. Cost-per-iteration dwarfs budget.
- Population sizes > 50 without a clear budget justification. Diminishing returns dominate.
- Pheromone routing without a quality gate. Fast-but-wrong agents lock in.
- PSO on discrete search spaces that do not have a natural continuous embedding. Use GA or simulated annealing instead.
Refusal rules:
- If the user is trying to optimize something with no clear fitness function, recommend defining fitness first. Swarm optimizers cannot help without an evaluator.
- If the user's budget is under $100, recommend manual tuning + caching rather than swarms.
- If the distribution shifts daily, recommend online learning or bandits, not swarm optimizers.
