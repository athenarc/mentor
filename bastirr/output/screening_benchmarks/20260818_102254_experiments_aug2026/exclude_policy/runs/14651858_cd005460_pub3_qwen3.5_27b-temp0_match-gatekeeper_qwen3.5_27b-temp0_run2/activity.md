# Pipeline Activity Log

> **Review:** Traditional birth attendant training for improving health behaviours and pregnancy outcomes  
> **Date:** 2026-08-18 10:26  
> **Duration:** 7m 03s  
> **Total tokens:** 174,449 (input: 159,299 / output: 15,150)

> **Benchmark suite:** experiments_aug2026  
> **Review key:** 14651858_cd005460_pub3  
> **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD005460.pub3/full  
> **Dataset split:** dev  
> **Studies:** 33  
> **Gatekeeper preset:** qwen3.5_27b-temp0  
> **Gatekeeper model:** qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)]  
> **Orchestrator preset:** qwen3.5_27b-temp0  
> **Orchestrator model:** qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)]  
> **Orchestrator policy:** match-gatekeeper  
> **Gold label policy:** include_label_0_5  

## Resource Usage by Agent

| Agent | Steps | Time | Tokens (in / out) |
|-------|-------|------|-------------------|
| Orchestrator | 4 | 7m 03s | 17,152 / 1,092 |
| Gatekeeper | 6 | 6m 40s | 142,147 / 14,058 |
| **Total** | **10** | **7m 03s** | **159,299 / 15,150** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*10:27:02 — 4s — 3,741 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*10:33:47 — 6m 45s — 160,373 tokens*

The orchestrator executed step 2. Used tools: python_interpreter.

---

### 3. Orchestrator (python_interpreter)

*10:33:57 — 10s — 4,919 tokens*

The orchestrator executed step 3. Used tools: python_interpreter.

---

### 4. Final Output (Orchestrator)

*10:34:01 — 4s — 5,416 tokens*

The orchestrator executed step 4. Used tools: python_interpreter. Produced the final output.

---
