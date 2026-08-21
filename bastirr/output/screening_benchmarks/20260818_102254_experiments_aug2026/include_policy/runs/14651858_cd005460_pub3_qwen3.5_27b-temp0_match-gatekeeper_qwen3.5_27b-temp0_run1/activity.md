# Pipeline Activity Log

> **Review:** Traditional birth attendant training for improving health behaviours and pregnancy outcomes  
> **Date:** 2026-08-18 10:23  
> **Duration:** 3m 33s  
> **Total tokens:** 217,434 (input: 206,976 / output: 10,458)

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
| Orchestrator | 4 | 3m 32s | 17,124 / 1,109 |
| Gatekeeper | 6 | 3m 03s | 189,852 / 9,349 |
| **Total** | **10** | **3m 33s** | **206,976 / 10,458** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*10:23:24 — 14s — 3,749 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*10:26:35 — 3m 10s — 203,407 tokens*

The orchestrator executed step 2. Used tools: python_interpreter.

---

### 3. Orchestrator (python_interpreter)

*10:26:40 — 6s — 4,941 tokens*

The orchestrator executed step 3. Used tools: python_interpreter.

---

### 4. Final Output (Orchestrator)

*10:26:43 — 3s — 5,337 tokens*

The orchestrator executed step 4. Used tools: python_interpreter. Produced the final output.

---
