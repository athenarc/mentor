# Pipeline Activity Log

> **Review:** Combined oral contraceptives: venous thrombosis  
> **Date:** 2026-08-20 08:01  
> **Duration:** 3m 55s  
> **Total tokens:** 300,019 (input: 287,805 / output: 12,214)

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
| Orchestrator | 4 | 3m 55s | 17,197 / 1,238 |
| Gatekeeper | 4 | 3m 25s | 270,608 / 10,976 |
| **Total** | **8** | **3m 55s** | **287,805 / 12,214** |

---

## Activity Timeline

### 1. Orchestrator (python_interpreter)

*08:01:55 — 5s — 3,767 tokens*

The orchestrator executed step 1. Used tools: python_interpreter.

---

### 2. Orchestrator → Gatekeeper

*08:05:28 — 3m 33s — 285,877 tokens*

The orchestrator executed step 2. Used tools: python_interpreter.

---

### 3. Orchestrator (python_interpreter)

*08:05:41 — 13s — 4,970 tokens*

The orchestrator executed step 3. Used tools: python_interpreter.

---

### 4. Final Output (Orchestrator)

*08:05:45 — 4s — 5,405 tokens*

The orchestrator executed step 4. Used tools: python_interpreter. Produced the final output.

---
