# Pipeline Activity Log

> **Review:** Traditional birth attendant training for improving health behaviours and pregnancy outcomes  
> **Date:** 2026-08-17 09:58  
> **Duration:** 10m 51s  
> **Total tokens:** 345,247 (input: 325,214 / output: 20,033)

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
| Orchestrator | 4 | 10m 51s | 54,917 / 1,231 |
| Gatekeeper | 6 | 9m 26s | 270,297 / 18,802 |
| **Total** | **10** | **10m 51s** | **325,214 / 20,033** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*09:59:01 — 10s — 3,838 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*10:08:40 — 9m 38s — 304,057 tokens*

The orchestrator executed step 2. Used tools: python_interpreter.

---

### 3. Orchestrator (python_interpreter)

*10:09:18 — 38s — 18,540 tokens*

The orchestrator executed step 3. Used tools: python_interpreter.

---

### 4. Final Output (Orchestrator)

*10:09:42 — 25s — 18,812 tokens*

The orchestrator executed step 4. Used tools: python_interpreter. Produced the final output.

---
