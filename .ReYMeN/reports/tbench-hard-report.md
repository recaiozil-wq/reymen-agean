# ReYMeN Terminal-Bench HARD Task Results

**Date:** 2026-07-02
**Model:** DeepSeek V4 Flash (via plan+recovery katmanı)

## Summary

| Metric | Value |
|--------|-------|
| Total hard tasks | 57 |
| Feasible (Docker ile build+run) | 30 |
| Not feasible (özel env gerekli) | 27 |
| Test edilen | 5 |
| Tam çözüm (11/11 test geçti) | 1 |

## Test Results (5 hard task)

| Task | Kategori | Solution | Test | Not |
|------|----------|----------|------|-----|
| ✅ **stable-parallel-kmeans** | machine-learning | ✅ Çalıştı | ✅ **11/11 GEÇTİ** | Paralel k-means implementasyonu + test |
| ✅ **circuit-fibsqrt** | software-engineering | ✅ Çalıştı | ⚠️ 2/3 geçti | sim.c compilation path issue |
| ✅ **regex-chess** | software-engineering | ✅ 2.6MB regex | ⏱️ Timeout | 5000+ regex, test çok yavaş |
| ✅ **video-processing** | video-processing | ✅ Çalıştı | ❌ Collection error | OpenCV import path |
| ✅ **password-recovery** | security | ✅ Çalıştı | ⚠️ Template | Reference solution placeholder |

## Feasibility Breakdown

### Can attempt (30 tasks)
Python-3-13 base: cancel-async-tasks, chem-property-targeting, chem-rf, circuit-fibsqrt, extract-moves-from-video, gpt2-codegolf, llm-inference-batching-scheduler, model-extraction-relu-logits, organization-json-generator, regex-chess, stable-parallel-kmeans, train-fasttext, video-processing, word2vec-from-scratch, feal-differential-cryptanalysis, feal-linear-cryptanalysis, movie-helper

Ubuntu-24-04 base (compatible): configure-git-webserver, find-official-code, fix-code-vulnerability, password-recovery, path-tracing, path-tracing-reverse, port-compressor, reverse-engineering, vul-flink, write-compressor, parallelize-graph, rare-mineral-allocation, swe-bench-astropy-1, swe-bench-astropy-2, neuron-to-jaxley-conversion

### Not feasible (27 tasks)
Torch gerekli (6): cartpole-rl-training, hf-train-lora-adapter, leelachess0-pytorch-conversion, torch-pipeline-parallelism, torch-tensor-parallelism, model-extraction-relu-logits

Specialized env (21): 3d-model-format-legacy, bn-fit-modify, causal-inference-r, dna-assembly, feal-differential-cryptanalysis, feal-linear-cryptanalysis, fix-ocaml-gc, install-windows-3.11, install-windows-xp, lean4-proof, magsac-install, make-doom-for-mips, make-mips-interpreter, mcmc-sampling-stan, parallel-particle-simulator, play-zork, play-zork-easy, polyglot-rust-c, protein-assembly, run-pdp11-code, sam-cell-seg, sparql-university
