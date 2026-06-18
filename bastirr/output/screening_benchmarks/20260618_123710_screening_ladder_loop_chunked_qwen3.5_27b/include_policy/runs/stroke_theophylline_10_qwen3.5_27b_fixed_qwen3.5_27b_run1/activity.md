# Pipeline Activity Log

> **Review:** Theophylline, aminophylline, caffeine and analogues for acute ischaemic stroke  
> **Date:** 2026-06-18 12:37  
> **Duration:** 1m 42s  
> **Total tokens:** 52,569 (input: 45,734 / output: 6,835)

> **Benchmark suite:** screening_ladder  
> **Benchmark architecture:** loop_chunk_orchestrator_v1  
> **Loop mode:** chunked  
> **Review key:** stroke_theophylline_10  
> **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD000211.pub2/full  
> **Dataset split:** val  
> **Studies:** 10  
> **Chunk count:** 1  
> **Chunk sizes:** 10  
> **Gatekeeper preset:** qwen3.5_27b  
> **Gatekeeper model:** qwen3.5-27b [Qwen 3.5 27B]  
> **Orchestrator preset:** qwen3.5_27b  
> **Orchestrator model:** qwen3.5-27b [Qwen 3.5 27B]  
> **Orchestrator policy:** fixed  
> **Gold label policy:** include_label_0_5  

## Resource Usage by Agent

| Agent | Steps | Time | Tokens (in / out) |
|-------|-------|------|-------------------|
| Orchestrator | 4 | 1m 41s | 16,980 / 1,110 |
| Gatekeeper | 3 | 1m 20s | 28,754 / 5,725 |
| **Total** | **7** | **1m 42s** | **45,734 / 6,835** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*12:37:17 — 6s — 3,876 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*12:38:43 — 1m 26s — 38,712 tokens*

The orchestrator executed step 2. Used tools: python_interpreter.

---

### 3. Orchestrator (python_interpreter)

*12:38:48 — 5s — 4,787 tokens*

The orchestrator executed step 3. Used tools: python_interpreter.

---

### 4. Final Output (Orchestrator)

*12:38:53 — 5s — 5,194 tokens*

The orchestrator executed step 4. Used tools: python_interpreter. Produced the final output.

---
