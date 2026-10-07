# Pipeline Activity Log

> **Review:** Non‐invasive diagnostic tests for   Helicobacter pylori infection  
> **Date:** 2026-09-15 16:08  
> **Duration:** 33m 54s  
> **Total tokens:** 899,341 (input: 787,626 / output: 111,715)

> **Benchmark suite:** experiments_sep2026_biggest_reviews  
> **Benchmark architecture:** loop_chunk_orchestrator_v1  
> **Loop mode:** chunked  
> **Review key:** 14651858_cd012080_pub2  
> **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD012080.pub2/full  
> **Dataset split:** dev  
> **Studies:** 1271  
> **Chunk count:** 13  
> **Chunk sizes:** 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 71  
> **Gatekeeper preset:** qwen3.5_27b-temp0  
> **Gatekeeper model:** qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)]  
> **Orchestrator preset:** qwen3.5_27b-temp0  
> **Orchestrator model:** qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)]  
> **Orchestrator policy:** match-gatekeeper  
> **Orchestrator max steps:** 20  
> **Gold label policy:** include_label_0_5  

## Resource Usage by Agent

| Agent | Steps | Time | Tokens (in / out) |
|-------|-------|------|-------------------|
| Orchestrator | 8 | 33m 53s | 31,137 / 2,709 |
| Gatekeeper | 8 | 30m 38s | 756,489 / 109,006 |
| **Total** | **16** | **33m 54s** | **787,626 / 111,715** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*16:08:41 — 15s — 4,755 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*16:21:07 — 12m 25s — 289,739 tokens*

The orchestrator executed step 2. Used tools: python_interpreter.

---

### 3. Orchestrator (python_interpreter)

*16:21:22 — 14s — 6,259 tokens*

The orchestrator executed step 3. Used tools: python_interpreter.

---

### 4. Final Output (Orchestrator)

*16:21:25 — 4s — 6,504 tokens*

The orchestrator executed step 4. Used tools: python_interpreter. Produced the final output.

---

### 5. Orchestrator (python_interpreter)

*16:21:45 — 19s — 4,982 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 6. Orchestrator → Gatekeeper

*16:40:18 — 18m 33s — 587,102 tokens*

The orchestrator executed step 2. Used tools: python_interpreter.

---

### 7. Orchestrator — Step 3

*16:41:19 — 1m 01s*

The orchestrator executed step 3. 

---

### 8. Orchestrator — Step 1

*16:42:21 — 1m 01s*

The orchestrator executed step 1. 

---
