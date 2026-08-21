# Pipeline Activity Log

> **Review:** Early versus delayed antiretroviral treatment in HIV‐positive people with cryptococcal meningitis  
> **Date:** 2026-08-18 18:32  
> **Duration:** 13m 21s  
> **Total tokens:** 370,627 (input: 335,961 / output: 34,666)

> **Benchmark suite:** experiments_aug2026  
> **Review key:** 14651858_cd009012_pub3  
> **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD009012.pub3/full  
> **Dataset split:** dev  
> **Studies:** 30  
> **Gatekeeper preset:** qwen3.5_27b-temp0  
> **Gatekeeper model:** qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)]  
> **Orchestrator preset:** qwen3.5_27b-temp0  
> **Orchestrator model:** qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)]  
> **Orchestrator policy:** match-gatekeeper  
> **Gold label policy:** include_label_0_5  

## Resource Usage by Agent

| Agent | Steps | Time | Tokens (in / out) |
|-------|-------|------|-------------------|
| Orchestrator | 8 | 13m 21s | 29,779 / 2,218 |
| Gatekeeper | 6 | 11m 05s | 306,182 / 32,448 |
| **Total** | **14** | **13m 21s** | **335,961 / 34,666** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*18:32:31 — 6s — 4,056 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator (python_interpreter)

*18:32:34 — 3s — 4,348 tokens*

The orchestrator executed step 2. Used tools: python_interpreter.

---

### 3. Orchestrator → Gatekeeper

*18:41:45 — 9m 10s — 216,756 tokens*

The orchestrator executed step 3. Used tools: python_interpreter.

---

### 4. Orchestrator — Step 4

*18:42:47 — 1m 01s*

The orchestrator executed step 4. 

---

### 5. Orchestrator (python_interpreter)

*18:42:56 — 9s — 3,916 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 6. Orchestrator → Gatekeeper

*18:45:36 — 2m 39s — 131,027 tokens*

The orchestrator executed step 2. Used tools: python_interpreter.

---

### 7. Orchestrator (python_interpreter)

*18:45:41 — 5s — 5,063 tokens*

The orchestrator executed step 3. Used tools: python_interpreter.

---

### 8. Final Output (Orchestrator)

*18:45:47 — 6s — 5,461 tokens*

The orchestrator executed step 4. Used tools: python_interpreter. Produced the final output.

---
