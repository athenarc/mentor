# Pipeline Activity Log

> **Review:** Early versus delayed antiretroviral treatment in HIV‐positive people with cryptococcal meningitis  
> **Date:** 2026-08-25 09:11  
> **Duration:** 10m 51s  
> **Total tokens:** 222,196 (input: 196,812 / output: 25,384)

> **Benchmark suite:** experiments_aug2026  
> **Benchmark architecture:** loop_chunk_orchestrator_v1  
> **Loop mode:** chunked  
> **Review key:** 14651858_cd009012_pub3  
> **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD009012.pub3/full  
> **Dataset split:** dev  
> **Studies:** 30  
> **Chunk count:** 2  
> **Chunk sizes:** 20, 10  
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
| Orchestrator | 8 | 10m 50s | 34,896 / 2,186 |
| Gatekeeper | 9 | 9m 36s | 161,916 / 23,198 |
| **Total** | **17** | **10m 51s** | **196,812 / 25,384** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*09:12:09 — 16s — 4,006 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*09:18:15 — 6m 05s — 119,470 tokens*

The orchestrator executed step 2. Used tools: python_interpreter.

---

### 3. Orchestrator (python_interpreter)

*09:18:25 — 10s — 4,977 tokens*

The orchestrator executed step 3. Used tools: python_interpreter.

---

### 4. Final Output (Orchestrator)

*09:18:30 — 5s — 5,295 tokens*

The orchestrator executed step 4. Used tools: python_interpreter. Produced the final output.

---

### 5. Orchestrator (python_interpreter)

*09:18:38 — 7s — 3,934 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 6. Orchestrator → Gatekeeper

*09:22:33 — 3m 55s — 74,348 tokens*

The orchestrator executed step 2. Used tools: python_interpreter.

---

### 7. Orchestrator (python_interpreter)

*09:22:39 — 6s — 4,864 tokens*

The orchestrator executed step 3. Used tools: python_interpreter.

---

### 8. Final Output (Orchestrator)

*09:22:44 — 4s — 5,302 tokens*

The orchestrator executed step 4. Used tools: python_interpreter. Produced the final output.

---
