# Pipeline Activity Log

> **Review:** Combined oral contraceptives: venous thrombosis  
> **Date:** 2026-08-20 08:06  
> **Duration:** 14m 55s  
> **Total tokens:** 372,986 (input: 349,553 / output: 23,433)

> **Benchmark suite:** experiments_aug2026  
> **Review key:** 14651858_cd010813_pub2  
> **Review URL:** https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD010813.pub2/full  
> **Dataset split:** dev  
> **Studies:** 121  
> **Gatekeeper preset:** qwen3.5_27b-temp0  
> **Gatekeeper model:** qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)]  
> **Orchestrator preset:** qwen3.5_27b-temp0  
> **Orchestrator model:** qwen3.5_27b-temp0 [Qwen 3.5 27B (temperature 0)]  
> **Orchestrator policy:** match-gatekeeper  
> **Gold label policy:** include_label_0_5  

## Resource Usage by Agent

| Agent | Steps | Time | Tokens (in / out) |
|-------|-------|------|-------------------|
| Orchestrator | 4 | 14m 55s | 16,967 / 1,212 |
| Gatekeeper | 4 | 14m 05s | 332,586 / 22,221 |
| **Total** | **8** | **14m 55s** | **349,553 / 23,433** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*08:06:09 — 9s — 4,042 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*08:20:40 — 14m 30s — 359,172 tokens*

The orchestrator executed step 2. Used tools: python_interpreter.

---

### 3. Orchestrator (python_interpreter)

*08:20:52 — 12s — 4,756 tokens*

The orchestrator executed step 3. Used tools: python_interpreter.

---

### 4. Final Output (Orchestrator)

*08:20:55 — 3s — 5,016 tokens*

The orchestrator executed step 4. Used tools: python_interpreter. Produced the final output.

---
