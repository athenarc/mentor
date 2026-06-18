# Pipeline Activity Log

> **Review:** Theophylline, aminophylline, caffeine and analogues for acute ischaemic stroke  
> **Date:** 2026-06-18 07:03  
> **Duration:** 21m 43s  
> **Total tokens:** 150,571 (input: 102,756 / output: 47,815)

> **Benchmark suite:** screening_ladder  
> **Benchmark architecture:** loop_chunk_orchestrator_v1  
> **Loop mode:** chunked  
> **Review key:** stroke_theophylline_10  
> **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD000211.pub2/full  
> **Dataset split:** val  
> **Studies:** 10  
> **Chunk count:** 1  
> **Chunk sizes:** 10  
> **Gatekeeper preset:** kimi_k2.6  
> **Gatekeeper model:** kimi-k2.6 [Kimi K2.6]  
> **Orchestrator preset:** kimi_k2.6  
> **Orchestrator model:** kimi-k2.6 [Kimi K2.6]  
> **Orchestrator policy:** fixed  
> **Gold label policy:** include_label_0_5  

## Resource Usage by Agent

| Agent | Steps | Time | Tokens (in / out) |
|-------|-------|------|-------------------|
| Orchestrator | 3 | 21m 43s | 11,600 / 1,236 |
| Gatekeeper | 12 | 21m 02s | 91,156 / 46,579 |
| **Total** | **15** | **21m 43s** | **102,756 / 47,815** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*07:03:34 — 16s — 3,802 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*07:24:55 — 21m 21s — 141,958 tokens*

The orchestrator executed step 2. Used tools: python_interpreter.

---

### 3. Final Output (Orchestrator)

*07:25:01 — 6s — 4,811 tokens*

The orchestrator executed step 3. Used tools: python_interpreter. Produced the final output.

---
