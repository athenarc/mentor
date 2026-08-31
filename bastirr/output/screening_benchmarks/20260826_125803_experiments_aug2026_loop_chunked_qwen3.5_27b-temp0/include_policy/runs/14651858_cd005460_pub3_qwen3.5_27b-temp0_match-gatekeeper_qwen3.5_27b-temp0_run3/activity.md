# Pipeline Activity Log

> **Review:** Traditional birth attendant training for improving health behaviours and pregnancy outcomes  
> **Date:** 2026-08-26 13:36  
> **Duration:** 9m 10s  
> **Total tokens:** 155,051 (input: 130,292 / output: 24,759)

> **Benchmark suite:** experiments_aug2026  
> **Benchmark architecture:** loop_chunk_orchestrator_v1  
> **Loop mode:** chunked  
> **Review key:** 14651858_cd005460_pub3  
> **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD005460.pub3/full  
> **Dataset split:** dev  
> **Studies:** 33  
> **Chunk count:** 2  
> **Chunk sizes:** 20, 13  
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
| Orchestrator | 8 | 9m 10s | 33,442 / 1,961 |
| Gatekeeper | 6 | 8m 20s | 96,850 / 22,798 |
| **Total** | **14** | **9m 10s** | **130,292 / 24,759** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*13:36:55 — 11s — 3,919 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*13:43:04 — 6m 08s — 25,921 tokens*

The orchestrator executed step 2. Used tools: python_interpreter.

---

### 3. Orchestrator (python_interpreter)

*13:43:09 — 5s — 4,584 tokens*

The orchestrator executed step 3. Used tools: python_interpreter.

---

### 4. Final Output (Orchestrator)

*13:43:12 — 3s — 4,910 tokens*

The orchestrator executed step 4. Used tools: python_interpreter. Produced the final output.

---

### 5. Orchestrator (python_interpreter)

*13:43:18 — 5s — 3,910 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 6. Orchestrator → Gatekeeper

*13:45:38 — 2m 20s — 102,072 tokens*

The orchestrator executed step 2. Used tools: python_interpreter.

---

### 7. Orchestrator (python_interpreter)

*13:45:47 — 10s — 4,642 tokens*

The orchestrator executed step 3. Used tools: python_interpreter.

---

### 8. Final Output (Orchestrator)

*13:45:55 — 8s — 5,093 tokens*

The orchestrator executed step 4. Used tools: python_interpreter. Produced the final output.

---
